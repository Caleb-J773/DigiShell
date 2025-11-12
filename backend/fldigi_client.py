import logging
import threading
from typing import Optional, Dict, Any
from pyfldigi import Client

logger = logging.getLogger(__name__)


class FldigiClient:

    def __init__(self, host: str = "127.0.0.1", port: int = 7362):
        self.host = host
        self.port = port
        self.client: Optional[Client] = None
        self._connected = False

    def connect(self) -> tuple[bool, Optional[str]]:
        try:
            self.client = Client(hostname=self.host, port=self.port)
            name = self.client.name
            logger.info(f"Connected to FLDIGI: {name}")
            self._connected = True
            return True, None
        except ConnectionRefusedError:
            error_msg = f"Connection refused to {self.host}:{self.port}. Is FLDIGI running with XML-RPC enabled?"
            logger.error(error_msg)
            self._connected = False
            return False, error_msg
        except TimeoutError:
            error_msg = f"Connection to {self.host}:{self.port} timed out. Check if FLDIGI is responding."
            logger.error(error_msg)
            self._connected = False
            return False, error_msg
        except Exception as e:
            error_str = str(e)
            if "10061" in error_str or "refused" in error_str.lower():
                error_msg = f"FLDIGI is not running or XML-RPC is not enabled on {self.host}:{self.port}"
            else:
                error_msg = f"Failed to connect to FLDIGI: {error_str}"
            logger.error(error_msg)
            self._connected = False
            return False, error_msg

    def disconnect(self):
        self.client = None
        self._connected = False
        logger.info("Disconnected from FLDIGI")

    def is_connected(self) -> bool:
        return self._connected

    def get_version(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            version = self.client.version
            return f"{version['major']}.{version['minor']}{version['patch']}"
        except Exception as e:
            logger.error(f"Error getting version: {e}")
            return None

    def get_name(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.name
        except Exception as e:
            logger.error(f"Error getting name: {e}")
            return None

    def get_modem(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.modem.name
        except Exception as e:
            logger.error(f"Error getting modem: {e}")
            return None

    def set_modem(self, modem_name: str) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.modem.name = modem_name
            logger.info(f"Set modem to: {modem_name}")
            return True
        except Exception as e:
            logger.error(f"Error setting modem: {e}")
            return False

    def get_carrier(self) -> Optional[int]:
        if not self.is_connected():
            return None
        try:
            return self.client.modem.carrier
        except Exception as e:
            logger.error(f"Error getting carrier: {e}")
            return None

    def set_carrier(self, frequency: int) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.modem.carrier = frequency
            logger.info(f"Set carrier to: {frequency} Hz")
            return True
        except Exception as e:
            logger.error(f"Error setting carrier: {e}")
            return False

    def get_bandwidth(self) -> Optional[int]:
        if not self.is_connected():
            return None
        try:
            return self.client.modem.bandwidth
        except Exception as e:
            logger.error(f"Error getting bandwidth: {e}")
            return None

    def set_bandwidth(self, bandwidth: int) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.modem.bandwidth = bandwidth
            logger.info(f"Set bandwidth to: {bandwidth} Hz")
            return True
        except Exception as e:
            logger.error(f"Error setting bandwidth: {e}")
            return False

    def get_quality(self) -> Optional[float]:
        if not self.is_connected():
            return None
        try:
            return self.client.modem.quality
        except Exception as e:
            logger.error(f"Error getting quality: {e}")
            return None

    def get_trx_status(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.main.get_trx_state()
        except Exception as e:
            logger.error(f"Error getting TRX status: {e}")
            return None

    def tx(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.tx()
            logger.info("Started TX")
            return True
        except Exception as e:
            logger.error(f"Error starting TX: {e}")
            return False

    def rx(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.rx()
            logger.info("Switched to RX")
            return True
        except Exception as e:
            logger.error(f"Error switching to RX: {e}")
            return False

    def tune(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.tune()
            logger.info("Started TUNE")
            return True
        except Exception as e:
            logger.error(f"Error starting TUNE: {e}")
            return False

    def abort(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.abort()
            logger.info("Aborted TX/TUNE")
            return True
        except Exception as e:
            logger.error(f"Error aborting: {e}")
            return False

    def get_rx_text(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            data = self.client.text.get_rx_data()
            if isinstance(data, bytes):
                return data.decode('utf-8', errors='ignore')
            return data if data else ""
        except Exception as e:
            logger.error(f"Error getting RX text: {e}")
            return None

    def get_tx_text(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            data = self.client.text.get_tx_data()
            if isinstance(data, bytes):
                return data.decode('utf-8', errors='ignore')
            return data if data else ""
        except Exception as e:
            logger.error(f"Error getting TX text: {e}")
            return None

    def add_tx_text(self, text: str, wait: bool = False) -> bool:
        if not self.is_connected():
            return False

        try:
            if not text.endswith('^r'):
                text = text + '^r'

            self.client.main.send(text, block=wait, timeout=30)
            logger.info(f"[TX] Sent {len(text)} chars (block={wait}): {text[:50]}...")

            return True
        except Exception as e:
            logger.error(f"Error transmitting text: {e}")
            return False

    def start_live_tx(self, text: str) -> bool:
        if not self.is_connected():
            return False

        try:
            logger.info(f"[TX LIVE] Starting new TX session with {len(text)} chars")
            self.client.main.send(text, block=False, timeout=30)
            logger.info("[TX LIVE] TX started via main.send()")
            return True
        except Exception as e:
            logger.error(f"Error starting live TX: {e}")
            return False

    def add_tx_chars(self, text: str, start_tx: bool = True) -> bool:
        if not self.is_connected():
            return False

        try:
            self.client.client.text.add_tx(text)

            if start_tx:
                trx_status = self.get_trx_status()
                if trx_status and trx_status != 'TX':
                    self.client.main.tx()
                    logger.info("[TX LIVE] Started transmission")

            return True
        except Exception as e:
            logger.error(f"Error adding characters to TX buffer: {e}")
            return False

    def send_backspace(self) -> bool:
        if not self.is_connected():
            return False

        try:
            self.client.client.text.add_tx('\x08')
            return True
        except Exception as e:
            logger.error(f"Error sending backspace: {e}")
            return False

    def end_tx_live(self, wait_for_drain: bool = False) -> bool:
        if not self.is_connected():
            return False

        try:
            if wait_for_drain:
                import time
                time.sleep(0.5)

            self.client.main.rx()
            logger.info("[TX LIVE] Switched to RX mode")
            return True
        except Exception as e:
            logger.error(f"Error ending TX: {e}")
            return False

    def clear_rx(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.text.clear_rx()
            logger.info("Cleared RX buffer")
            return True
        except Exception as e:
            logger.error(f"Error clearing RX: {e}")
            return False

    def clear_tx(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.text.clear_tx()
            logger.info("Cleared TX buffer")
            return True
        except Exception as e:
            logger.error(f"Error clearing TX: {e}")
            return False

    def get_rsid(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return self.client.main.rsid
        except Exception as e:
            logger.error(f"Error getting RSID: {e}")
            return None

    def set_rsid(self, enabled: bool) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.rsid = enabled
            logger.info(f"Set RSID to: {enabled}")
            return True
        except Exception as e:
            logger.error(f"Error setting RSID: {e}")
            return False

    def get_txid(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return bool(self.client.client.main.get_txid())
        except Exception as e:
            logger.error(f"Error getting TXID: {e}")
            return None

    def set_txid(self, enabled: bool) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.client.main.set_txid(bool(enabled))
            logger.info(f"Set TXID to: {enabled}")
            return True
        except Exception as e:
            logger.error(f"Error setting TXID: {e}")
            return False

    def get_rig_name(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.rig.name
        except Exception as e:
            logger.error(f"Error getting rig name: {e}")
            return None

    def get_rig_frequency(self) -> Optional[float]:
        if not self.is_connected():
            return None
        try:
            return self.client.rig.frequency
        except Exception as e:
            logger.error(f"Error getting rig frequency: {e}")
            return None

    def set_rig_frequency(self, frequency: float) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.rig.frequency = frequency
            logger.info(f"Set rig frequency to: {frequency} Hz")
            return True
        except Exception as e:
            logger.error(f"Error setting rig frequency: {e}")
            return False

    def get_rig_mode(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.rig.mode
        except Exception as e:
            logger.error(f"Error getting rig mode: {e}")
            return None

    def set_rig_mode(self, mode: str) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.rig.mode = mode
            logger.info(f"Set rig mode to: {mode}")
            return True
        except Exception as e:
            logger.error(f"Error setting rig mode: {e}")
            return False

    def get_afc(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return bool(self.client.client.modem.get_afc())
        except Exception as e:
            return None

    def set_afc(self, enabled: bool) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.client.modem.set_afc(bool(enabled))
            logger.info(f"Set AFC to: {enabled}")
            return True
        except Exception as e:
            return False

    def get_squelch(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return bool(self.client.client.main.get_squelch())
        except Exception as e:
            logger.error(f"Error getting squelch status: {e}")
            return None

    def set_squelch(self, enabled: bool) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.client.main.set_squelch(bool(enabled))
            logger.info(f"Set squelch to: {enabled}")
            return True
        except Exception as e:
            logger.error(f"Error setting squelch: {e}")
            return False

    def get_reverse(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return bool(self.client.client.modem.get_reverse())
        except Exception as e:
            return None

    def set_reverse(self, enabled: bool) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.client.modem.set_reverse(bool(enabled))
            logger.info(f"Set reverse to: {enabled}")
            return True
        except Exception as e:
            return False

    def get_squelch_level(self) -> Optional[float]:
        if not self.is_connected():
            return None
        try:
            return float(self.client.client.main.get_squelch_level())
        except Exception as e:
            logger.error(f"Error getting squelch level: {e}")
            return None

    def set_squelch_level(self, level: float) -> bool:
        if not self.is_connected():
            return False
        try:
            clamped_level = max(0.0, min(1.0, level))
            self.client.client.main.set_squelch_level(float(clamped_level))
            logger.info(f"Set squelch level to: {clamped_level}")
            return True
        except Exception as e:
            logger.error(f"Error setting squelch level: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected(),
            "version": self.get_version(),
            "name": self.get_name(),
            "modem": self.get_modem(),
            "carrier": self.get_carrier(),
            "bandwidth": self.get_bandwidth(),
            "quality": self.get_quality(),
            "trx_status": self.get_trx_status(),
            "rig_name": self.get_rig_name(),
            "rig_frequency": self.get_rig_frequency(),
            "rig_mode": self.get_rig_mode(),
        }


fldigi_client = FldigiClient()
