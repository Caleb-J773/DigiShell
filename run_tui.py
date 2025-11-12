#!/usr/bin/env python3

import asyncio
import sys
import json
import os
from datetime import datetime, timedelta, timezone
from backend.fldigi_client import fldigi_client
import re

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, FormattedTextControl, Dimension
from prompt_toolkit.layout.containers import WindowAlign
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.application import get_app

rx_buffer = []
last_tx = ""
last_call = ""
MAX_RX_LINES = 25
connection_time = None
command_status = ""
show_status_until = None
last_trx_status = None

live_tx_mode = True
live_tx_active = False
live_tx_ending = False
live_tx_buffer = ""
last_input_text = ""
live_tx_start_time = 0

CONFIG_FILE = ".fldigi_tui.json"
config = {
    "callsign": "NOCALL",
    "name": "Operator",
    "qth": "Somewhere",
    "macros": {},
}

COMMON_MODES = [
    "BPSK31", "BPSK63", "BPSK125", "QPSK31", "QPSK63",
    "RTTY-45", "RTTY-50", "OLIVIA 8/250", "OLIVIA 16/500",
    "CONTESTIA 8/250", "MT63-1000", "MFSK16", "THOR8"
]


def first_time_setup():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║         DigiShell - First Time Setup Wizard          ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()
    print("Welcome! Let's configure your station information.")
    print()

    while True:
        callsign = input("Enter your callsign (e.g., W1AW): ").strip().upper()
        if callsign and len(callsign) >= 3:
            config['callsign'] = callsign
            break
        print("Please enter a valid callsign (at least 3 characters)")

    name = input("Enter your name (or press Enter to skip): ").strip()
    if name:
        config['name'] = name

    qth = input("Enter your QTH/Location (or press Enter to skip): ").strip()
    if qth:
        config['qth'] = qth

    if not config.get('macros'):
        config['macros'] = {
            "1": "CQ CQ CQ CQ de <MYCALL> <MYCALL> <MYCALL>\nCQ CQ CQ CQ de <MYCALL> <MYCALL> <MYCALL> pse k",
            "2": "<CALL> de <MYCALL> = Good morning! Name here is <MYNAME>. QTH is <MYQTH>. How copy? <CALL> de <MYCALL> k",
            "3": "<CALL> de <MYCALL> = Thanks for the report. 73 and best DX! <MYCALL> sk",
            "4": "<CALL> de <MYCALL> = QSL QSL, roger that. <MYCALL> k",
            "5": "<CALL> de <MYCALL> = Signal report is 5x9. <MYCALL> k"
        }

    if save_config():
        print()
        print("✓ Configuration saved!")
        print(f"  Callsign: {config['callsign']}")
        print(f"  Name: {config['name']}")
        print(f"  QTH: {config['qth']}")
        print(f"  Macros: {len(config['macros'])} loaded")
    else:
        print()
        print("✗ WARNING: Failed to save configuration!")
        print("  Your settings will not persist between sessions.")

    print()
    input("Press Enter to start DigiShell...")


def load_config():
    global config
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                loaded = json.load(f)
                config.update(loaded)
        else:
            return False
    except Exception as e:
        print(f"WARNING: Failed to load config from {CONFIG_FILE}: {e}")
        print("Using default configuration.")
    return True


def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save config to {CONFIG_FILE}: {e}")
        return False


def expand_macros(text):
    global last_call

    replacements = {
        '<MYCALL>': config.get('callsign', 'NOCALL'),
        '<MYNAME>': config.get('name', 'Operator'),
        '<MYQTH>': config.get('qth', 'Somewhere'),
        '<CALL>': last_call or 'NOCALL',
        '<DATE>': datetime.now().strftime('%Y-%m-%d'),
        '<TIME>': datetime.now().strftime('%H:%M'),
        '<UTC>': datetime.now(timezone.utc).strftime('%H:%MZ'),
    }

    result = text
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result


def get_header_text():
    if fldigi_client.is_connected():
        status = "● CONNECTED"
        version = fldigi_client.get_version() or "Unknown"
        if connection_time:
            uptime = int((datetime.now() - connection_time).total_seconds())
            uptime_str = f"Uptime: {uptime}s"
        else:
            uptime_str = "Just connected"
    else:
        status = "● DISCONNECTED"
        version = "N/A"
        uptime_str = ""

    time_str = datetime.now().strftime("%H:%M:%S")

    return FormattedText([
        ('class:header.title', 'DigiShell'),
        ('', '  '),
        ('class:header.status', status),
        ('', '  '),
        ('class:header.time', time_str),
        ('', '\n'),
        ('class:header.version', f'Version: {version}'),
        ('', '  '),
        ('class:header.uptime', uptime_str),
    ])


def get_rx_text():
    if not rx_buffer:
        return FormattedText([('class:dim', 'Waiting for data...')])

    text = []
    line_count = 0

    for item in reversed(rx_buffer):
        if line_count >= MAX_RX_LINES:
            break

        if isinstance(item, dict):
            timestamp = item['time']
            message = item['text']
            item_text = [
                ('class:rx.timestamp', f"[{timestamp}] "),
                ('class:tx.text', f"{message}\n")
            ]
            text = item_text + text
            line_count += 1
        else:
            if item.strip():
                text = [('class:rx', item)] + text
                line_count += item.count('\n') + (1 if not item.endswith('\n') else 0)

    if text and not (isinstance(text[-1], tuple) and text[-1][1].endswith('\n')):
        text.append(('class:rx', '\n'))

    text.append(('', '\n'))
    text.append(('class:dim', f'[{len(rx_buffer)} messages]'))
    return FormattedText(text)


def get_commands_text():
    text = [
        ('class:help.title', 'TX Mode:\n'),
        ('class:help', '  '),
        ('class:help.cmd', 'LIVE' if live_tx_mode else 'BATCH'),
        ('class:help', ' - '),
        ('class:dim', 'Enter starts TX\n' if live_tx_mode else 'Enter sends all\n'),
        ('class:help', '\n'),
        ('class:help.title', 'Transmit:\n'),
        ('class:help', '  Type message\n'),
        ('class:help', '  '),
        ('class:help.cmd', 'Enter'),
        ('class:help', ' ' + ('to start/end TX\n' if live_tx_mode else 'to send\n')),
        ('class:help', '  '),
        ('class:help.cmd', 'Tab'),
        ('class:help', ' for newline\n'),
        ('class:dim', '  (edit live when TX)\n' if live_tx_mode else ''),
        ('class:help', '\n'),
        ('class:help.title', 'Commands:\n'),
        ('class:help.cmd', '  /live'),
        ('class:help', ' Toggle TX mode\n'),
        ('class:help.cmd', '  /m <mode>'),
        ('class:help', ' Set modem\n'),
        ('class:help.cmd', '  /carrier'),
        ('class:help', ' Adjust freq\n'),
        ('class:dim', '    /carrier 1500\n'),
        ('class:dim', '    /carrier +50\n'),
        ('class:help.cmd', '  /macro <#>'),
        ('class:help', ' Send macro\n'),
        ('class:help.cmd', '  /call <call>'),
        ('class:help', ' Set last call\n'),
        ('class:help.cmd', '  /config'),
        ('class:help', ' Set info\n'),
        ('class:help.cmd', '  /clear'),
        ('class:help', ' Clear RX\n'),
        ('class:help.cmd', '  /save'),
        ('class:help', ' Save RX\n'),
        ('class:help.cmd', '  Ctrl+C'),
        ('class:help', ' Quit\n\n'),
        ('class:dim', '/ = command | no / = TX\n\n'),
    ]

    if config.get('callsign') != 'NOCALL':
        text.append(('class:help.title', 'Station:\n'))
        text.append(('class:help', f"  {config['callsign']}"))
        if last_call:
            text.append(('class:dim', f" → {last_call}"))
        text.append(('class:help', '\n'))

    return FormattedText(text)


def get_status_text():
    global command_status, show_status_until, last_tx

    if not fldigi_client.is_connected():
        return FormattedText([('class:warning', 'Not connected to FLDIGI')])

    modem = fldigi_client.get_modem() or "Unknown"
    carrier = fldigi_client.get_carrier() or 0
    frequency = fldigi_client.get_rig_frequency() or 0
    trx_status = fldigi_client.get_trx_status() or "Unknown"

    if trx_status == "RX":
        status_class = 'class:status.rx'
    elif trx_status == "TX":
        status_class = 'class:status.tx'
    else:
        status_class = 'class:status.other'

    freq_display = f'{frequency / 1000000:.4f} MHz' if frequency > 0 else 'N/A'

    text = [
        ('class:status.label', 'Mode: '),
        ('class:status.value', modem),
        ('', '  '),
        ('class:status.label', 'Freq: '),
        ('class:status.value', freq_display),
        ('', '  '),
        ('class:status.label', 'Carrier: '),
        ('class:status.value', f'{carrier}Hz'),
        ('', '  '),
        ('class:status.label', 'Status: '),
        (status_class, trx_status),
    ]

    now = datetime.now()
    if command_status and show_status_until and now < show_status_until:
        text.append(('', '  |  '))
        text.append(('class:command.status', command_status))
    elif command_status and show_status_until and now >= show_status_until:
        command_status = ""
        show_status_until = None

    return FormattedText(text)


header_window = Window(
    content=FormattedTextControl(get_header_text),
    height=3,
    style='class:header'
)

rx_window = Window(
    content=FormattedTextControl(get_rx_text),
    wrap_lines=True,
    style='class:frame.rx',
    always_hide_cursor=True
)

help_window = Window(
    content=FormattedTextControl(get_commands_text),
    wrap_lines=True,
    style='class:frame.help'
)

status_window = Window(
    content=FormattedTextControl(get_status_text),
    height=3,
    style='class:status'
)

input_field = TextArea(
    height=Dimension(min=4, max=10, preferred=6),
    prompt='> ',
    multiline=True,
    wrap_lines=True,
    style='class:input',
    focus_on_click=True,
)


def get_input_help_text():
    if live_tx_mode:
        if live_tx_active:
            help_text = 'Live editing | Enter=end TX | Tab=newline | Ctrl+C=quit'
        else:
            help_text = '/cmd for commands | Enter=TX | Tab=newline | Ctrl+C=quit'
    else:
        help_text = '/cmd for commands | Enter=send | Tab=newline | Ctrl+C=quit'

    return FormattedText([
        ('class:dim', help_text)
    ])


input_help_window = Window(
    content=FormattedTextControl(get_input_help_text),
    height=Dimension(min=1, max=2),
    wrap_lines=True,
    style='class:input.help'
)


async def send_tx_text(text):
    try:
        return fldigi_client.add_tx_text(text, wait=False)
    except Exception as e:
        return False


async def handle_live_tx_change():
    global live_tx_buffer, last_input_text

    if not live_tx_active or live_tx_ending:
        return

    current_text = input_field.text

    if current_text == last_input_text:
        return

    if len(current_text) > len(last_input_text):
        new_chars = current_text[len(last_input_text):]
        try:
            success = fldigi_client.add_tx_chars(new_chars, start_tx=False)
            if success:
                live_tx_buffer += new_chars
        except Exception as e:
            pass

    elif len(current_text) < len(last_input_text):
        num_deleted = len(last_input_text) - len(current_text)
        try:
            for _ in range(num_deleted):
                fldigi_client.send_backspace()
            if len(live_tx_buffer) >= num_deleted:
                live_tx_buffer = live_tx_buffer[:-num_deleted]
        except Exception as e:
            pass

    last_input_text = current_text


async def process_input(text):
    global command_status, show_status_until, last_tx

    if not text.strip():
        return

    if text.startswith('/'):
        cmd_parts = text[1:].split(maxsplit=1)
        command = cmd_parts[0].lower()
        args = cmd_parts[1] if len(cmd_parts) > 1 else ""

        if command in ['q', 'quit']:
            command_status = "Shutting down..."
            show_status_until = datetime.now() + timedelta(seconds=2)
            await asyncio.sleep(2)
            get_app().exit()

        elif command in ['c', 'clear']:
            rx_buffer.clear()
            command_status = "RX buffer cleared"
            show_status_until = datetime.now() + timedelta(seconds=2)

        elif command in ['s', 'save']:
            if not rx_buffer:
                command_status = "RX buffer is empty"
                show_status_until = datetime.now() + timedelta(seconds=2)
            else:
                try:
                    from pathlib import Path
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = args if args else f"fldigi-rx-{timestamp}.txt"

                    if not filename.endswith('.txt'):
                        filename += '.txt'

                    filepath = Path(filename)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        for entry in rx_buffer:
                            prefix = "[YOU]" if entry['type'] == 'tx' else "[RX]"
                            f.write(f"{entry['time']} {prefix} {entry['text']}\n")

                    command_status = f"Saved to {filename}"
                    show_status_until = datetime.now() + timedelta(seconds=3)
                except Exception as e:
                    command_status = f"Save failed: {str(e)}"
                    show_status_until = datetime.now() + timedelta(seconds=3)

        elif command == 'm':
            if not args:
                command_status = "Usage: /m <mode>"
                show_status_until = datetime.now() + timedelta(seconds=3)
            else:
                if fldigi_client.set_modem(args.upper()):
                    command_status = f"Mode: {args.upper()}"
                    show_status_until = datetime.now() + timedelta(seconds=2)
                else:
                    command_status = "Failed to set mode"
                    show_status_until = datetime.now() + timedelta(seconds=3)

        elif command == 'modes':
            modes_str = ', '.join(COMMON_MODES[:5]) + '...'
            command_status = modes_str
            show_status_until = datetime.now() + timedelta(seconds=5)

        elif command == 'carrier':
            if not args:
                current = fldigi_client.get_carrier()
                command_status = f"Carrier: {current}Hz"
                show_status_until = datetime.now() + timedelta(seconds=3)
            else:
                try:
                    if args.startswith('+') or args.startswith('-'):
                        current = fldigi_client.get_carrier()
                        adjustment = int(args)
                        freq = current + adjustment
                    else:
                        freq = int(args)

                    if fldigi_client.set_carrier(freq):
                        command_status = f"Carrier: {freq}Hz"
                        show_status_until = datetime.now() + timedelta(seconds=2)
                    else:
                        command_status = "Failed to set carrier"
                        show_status_until = datetime.now() + timedelta(seconds=3)
                except ValueError:
                    command_status = "Usage: /carrier <hz> or /carrier +/-<hz>"
                    show_status_until = datetime.now() + timedelta(seconds=3)

        elif command == 'txid':
            current = fldigi_client.get_txid()
            new_state = not current if current is not None else True
            if fldigi_client.set_txid(new_state):
                command_status = f"TXID {'ON' if new_state else 'OFF'}"
                show_status_until = datetime.now() + timedelta(seconds=2)
            else:
                command_status = "Failed to toggle TXID"
                show_status_until = datetime.now() + timedelta(seconds=3)

        elif command in ['h', 'help']:
            command_status = "See Commands panel →"
            show_status_until = datetime.now() + timedelta(seconds=2)

        elif command == 'live':
            global live_tx_mode, live_tx_buffer, live_tx_active, live_tx_ending
            live_tx_mode = not live_tx_mode
            live_tx_buffer = ""
            live_tx_active = False
            live_tx_ending = False
            mode_name = "LIVE" if live_tx_mode else "BATCH"
            command_status = f"TX mode: {mode_name}"
            show_status_until = datetime.now() + timedelta(seconds=3)

        elif command == 'macro':
            if not args:
                macros = config.get('macros', {})
                if macros:
                    macro_list = ', '.join(sorted(macros.keys()))
                    command_status = f"Macros: {macro_list}"
                    show_status_until = datetime.now() + timedelta(seconds=5)
                else:
                    command_status = "No macros defined"
                    show_status_until = datetime.now() + timedelta(seconds=3)
            else:
                macro_num = args.strip()
                macros = config.get('macros', {})
                if macro_num in macros:
                    macro_text = expand_macros(macros[macro_num])
                    success = await send_tx_text(macro_text)
                    if success:
                        last_tx = macro_text
                        rx_buffer.append({
                            'time': datetime.now().strftime("%H:%M:%S"),
                            'text': macro_text,
                            'type': 'tx'
                        })
                        command_status = f"✓ Macro {macro_num}"
                        show_status_until = datetime.now() + timedelta(seconds=2)
                    else:
                        command_status = "✗ Failed to send macro"
                        show_status_until = datetime.now() + timedelta(seconds=3)
                else:
                    command_status = f"Macro {macro_num} not found"
                    show_status_until = datetime.now() + timedelta(seconds=3)

        elif command == 'call':
            global last_call
            if not args:
                if last_call:
                    command_status = f"Last call: {last_call}"
                else:
                    command_status = "No call set"
                show_status_until = datetime.now() + timedelta(seconds=3)
            else:
                last_call = args.upper().strip()
                command_status = f"Call set: {last_call}"
                show_status_until = datetime.now() + timedelta(seconds=2)

        elif command == 'config':
            if not args:
                command_status = f"{config['callsign']} | {config['name']} | {config['qth']}"
                show_status_until = datetime.now() + timedelta(seconds=5)
            else:
                parts = args.split(maxsplit=2)
                if len(parts) >= 1:
                    config['callsign'] = parts[0].upper()
                if len(parts) >= 2:
                    config['name'] = parts[1]
                if len(parts) >= 3:
                    config['qth'] = parts[2]

                if save_config():
                    command_status = f"✓ Config saved: {config['callsign']}"
                else:
                    command_status = f"✗ Failed to save config"
                show_status_until = datetime.now() + timedelta(seconds=3)

        elif command in ['addmacro', 'editmacro']:
            if not args:
                command_status = "Usage: /addmacro <key> <text>"
                show_status_until = datetime.now() + timedelta(seconds=3)
            else:
                parts = args.split(maxsplit=1)
                if len(parts) == 2:
                    key, macro_text = parts
                    config['macros'][key] = macro_text
                    if save_config():
                        command_status = f"✓ Macro '{key}' saved"
                    else:
                        command_status = f"✗ Failed to save macro"
                    show_status_until = datetime.now() + timedelta(seconds=3)
                else:
                    command_status = "Usage: /addmacro <key> <text>"
                    show_status_until = datetime.now() + timedelta(seconds=3)

        elif command in ['delmacro', 'deletemacro']:
            if not args:
                command_status = "Usage: /delmacro <key>"
                show_status_until = datetime.now() + timedelta(seconds=3)
            else:
                key = args.strip()
                if key in config.get('macros', {}):
                    del config['macros'][key]
                    if save_config():
                        command_status = f"✓ Macro '{key}' deleted"
                    else:
                        command_status = f"✗ Failed to save changes"
                    show_status_until = datetime.now() + timedelta(seconds=3)
                else:
                    command_status = f"Macro '{key}' not found"
                    show_status_until = datetime.now() + timedelta(seconds=3)

        else:
            command_status = f"Unknown: /{command}"
            show_status_until = datetime.now() + timedelta(seconds=3)
    else:
        success = await send_tx_text(text)
        if success:
            last_tx = text
            rx_buffer.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'text': text,
                'type': 'tx'
            })
            command_status = f"✓ Queued for TX"
            show_status_until = datetime.now() + timedelta(seconds=2)
        else:
            command_status = "✗ Failed to queue"
            show_status_until = datetime.now() + timedelta(seconds=3)


def accept_input(buff):
    text = input_field.text
    input_field.text = ""

    asyncio.create_task(process_input(text))


kb = KeyBindings()

@kb.add('c-c')
def _(event):
    event.app.exit()


@kb.add('enter')
def _(event):
    global live_tx_buffer, last_input_text, live_tx_active, live_tx_ending, live_tx_start_time, command_status, show_status_until
    import time

    if event.app.layout.has_focus(input_field):
        text = input_field.text

        if live_tx_mode:
            if not live_tx_active:
                if text.strip():
                    if text.startswith('/'):
                        input_field.text = ""
                        asyncio.create_task(process_input(text))
                    else:
                        try:
                            fldigi_client.start_live_tx(text)
                            live_tx_active = True
                            live_tx_ending = False
                            live_tx_buffer = text
                            last_input_text = text
                            live_tx_start_time = time.time()
                            command_status = "✓ TX Started - type to continue"
                            show_status_until = datetime.now() + timedelta(seconds=2)
                        except Exception:
                            command_status = "✗ Failed to start TX"
                            show_status_until = datetime.now() + timedelta(seconds=3)
            else:
                try:
                    live_tx_ending = True
                    fldigi_client.end_tx_live()
                    command_status = "Ending TX..."
                    show_status_until = datetime.now() + timedelta(seconds=2)
                except Exception:
                    command_status = "✗ Failed to end TX"
                    show_status_until = datetime.now() + timedelta(seconds=3)
                    live_tx_ending = False
        else:
            if text.strip():
                input_field.text = ""
                asyncio.create_task(process_input(text))


@kb.add('tab')
def _(event):
    if event.app.layout.has_focus(input_field):
        input_field.buffer.insert_text('\n')


root_container = HSplit([
    header_window,
    VSplit([
        HSplit([
            Frame(rx_window, title='Receive Buffer', height=Dimension(weight=70)),
            Frame(
                HSplit([
                    input_help_window,
                    input_field,
                ]),
                title='Input / TX Window',
                height=Dimension(weight=30)
            ),
        ], width=Dimension(weight=70)),
        Frame(help_window, title='Commands & Info', width=Dimension(weight=30, min=30, max=45)),
    ]),
    status_window,
])

layout = Layout(root_container, focused_element=input_field)

style = Style.from_dict({
    'header': 'bg:#0d1117 fg:#58a6ff',
    'header.title': 'bold fg:#58a6ff',
    'header.status': 'bold fg:#3fb950',
    'header.time': 'fg:#f0f6fc',
    'header.version': 'fg:#8b949e',
    'header.uptime': 'fg:#8b949e',
    'frame': 'bg:#0d1117',
    'frame.label': 'bold fg:#58a6ff',
    'frame.rx': 'bg:#0d1117',
    'frame.help': 'bg:#0d1117',
    'rx': 'fg:#7ee787',
    'rx.timestamp': 'fg:#6e7681',
    'tx': 'bold fg:#ff6b6b',
    'tx.text': 'fg:#ff9999',
    'help': 'fg:#c9d1d9',
    'help.title': 'bold fg:#58a6ff',
    'help.cmd': 'fg:#f0883e',
    'status': 'bg:#161b22 fg:#c9d1d9',
    'status.label': 'fg:#58a6ff',
    'status.value': 'bold fg:#f0f6fc',
    'status.rx': 'bold fg:#3fb950',
    'status.tx': 'bold fg:#f85149',
    'status.other': 'bold fg:#d29922',
    'input': 'bg:#161b22 fg:#f0f6fc',
    'input.help': 'bg:#0d1117 fg:#6e7681',
    'command.status': 'bold fg:#d29922',
    'dim': 'fg:#6e7681',
    'bold': 'bold',
    'warning': 'fg:#f0883e',
})


async def poll_fldigi():
    global last_trx_status, live_tx_buffer, last_input_text, live_tx_active, live_tx_ending, command_status, show_status_until

    while True:
        try:
            if fldigi_client.is_connected():
                new_rx = fldigi_client.get_rx_text()
                if new_rx:
                    new_rx = new_rx.replace('\r\n', '\n').replace('\r', '\n')

                    if rx_buffer and isinstance(rx_buffer[-1], str):
                        rx_buffer[-1] += new_rx
                    else:
                        rx_buffer.append(new_rx)

                    if len(rx_buffer) > MAX_RX_LINES * 2:
                        rx_buffer[:] = rx_buffer[-MAX_RX_LINES:]

                current_trx_status = fldigi_client.get_trx_status()
                if last_trx_status == 'TX' and current_trx_status == 'RX':
                    if live_tx_mode:
                        if input_field.text.strip():
                            text = input_field.text
                            rx_buffer.append({
                                'time': datetime.now().strftime("%H:%M:%S"),
                                'text': text,
                                'type': 'tx'
                            })

                        input_field.text = ""
                        live_tx_buffer = ""
                        last_input_text = ""
                        live_tx_active = False
                        live_tx_ending = False

                        command_status = "✓ TX Complete"
                        show_status_until = datetime.now() + timedelta(seconds=2)

                last_trx_status = current_trx_status

            await asyncio.sleep(0.1)
        except Exception as e:
            await asyncio.sleep(1)


async def update_display():
    app = get_app()
    while True:
        try:
            if live_tx_mode and fldigi_client.is_connected():
                await handle_live_tx_change()

            app.invalidate()
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.5)


async def run_app_async():
    global connection_time

    load_config()

    if not fldigi_client.connect():
        print("Failed to connect to FLDIGI!")
        print("Make sure FLDIGI is running with XML-RPC enabled on port 7362")
        sys.exit(1)

    connection_time = datetime.now()

    if config.get('callsign') != 'NOCALL':
        print(f"Station: {config['callsign']} ({config['name']})")
        print(f"Macros: {len(config.get('macros', {}))} available")

    app = Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=True,
        mouse_support=True,
    )

    poll_task = asyncio.create_task(poll_fldigi())
    display_task = asyncio.create_task(update_display())

    try:
        await app.run_async()
    finally:
        poll_task.cancel()
        display_task.cancel()
        try:
            await asyncio.gather(poll_task, display_task, return_exceptions=True)
        except:
            pass
        fldigi_client.disconnect()


def main():
    try:
        if not load_config():
            first_time_setup()

        asyncio.run(run_app_async())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
