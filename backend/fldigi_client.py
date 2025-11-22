import logging
import threading
from typing import Optional, Dict, Any
from pyfldigi import Client

logger = logging.getLogger(__name__)

# Suppress excessive logging from dependencies
logging.getLogger('pyfldigi').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('requests').setLevel(logging.CRITICAL)


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

    def check_connection_health(self) -> bool:
        """Check if the connection is actually alive by making a simple API call."""
        if not self._connected:
            return False
        try:
            # Try a lightweight operation to verify connection
            _ = self.client.name
            return True
        except Exception as e:
            logger.warning(f"Connection health check failed: {e}")
            self._connected = False
            return False

    def _is_connection_error(self, error: Exception) -> bool:
        """Check if an exception indicates a connection problem."""
        error_str = str(error).lower()
        error_type = type(error).__name__

        # Connection error keywords
        connection_indicators = [
            'connection', 'refused', '10054', '10061',
            'forcibly closed', 'max retries', 'failed to establish',
            'target machine actively refused'
        ]

        return any(keyword in error_str for keyword in connection_indicators) or \
               error_type in ['ConnectionError', 'ConnectionRefusedError', 'ConnectionResetError']

    def reconnect(self) -> tuple[bool, Optional[str]]:
        """Attempt to reconnect to FlDigi."""
        logger.info("Attempting to reconnect to FLDIGI...")
        self.disconnect()
        return self.connect()

    def get_version(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            version = self.client.version
            return f"{version['major']}.{version['minor']}{version['patch']}"
        except Exception as e:
            logger.debug(f"Error getting version: {e}")
            return None

    def get_name(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.name
        except Exception as e:
            logger.debug(f"Error getting name: {e}")
            return None

    def get_modem(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.modem.name
        except Exception as e:
            logger.debug(f"Error getting modem: {e}")
            return None

    def set_modem(self, modem_name: str) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.modem.name = modem_name
            logger.info(f"Set modem to: {modem_name}")
            return True
        except Exception as e:
            logger.debug(f"Error setting modem: {e}")
            return False

    def get_carrier(self) -> Optional[int]:
        if not self.is_connected():
            return None
        try:
            return self.client.modem.carrier
        except Exception as e:
            logger.debug(f"Error getting carrier: {e}")
            return None

    def set_carrier(self, frequency: int) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.modem.carrier = frequency
            logger.info(f"Set carrier to: {frequency} Hz")
            return True
        except Exception as e:
            logger.debug(f"Error setting carrier: {e}")
            return False

    def get_bandwidth(self) -> Optional[int]:
        if not self.is_connected():
            return None
        try:
            return self.client.modem.bandwidth
        except Exception as e:
            logger.debug(f"Error getting bandwidth: {e}")
            return None

    def set_bandwidth(self, bandwidth: int) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.modem.bandwidth = bandwidth
            logger.info(f"Set bandwidth to: {bandwidth} Hz")
            return True
        except Exception as e:
            logger.debug(f"Error setting bandwidth: {e}")
            return False

    def get_quality(self) -> Optional[float]:
        if not self.is_connected():
            return None
        try:
            return self.client.modem.quality
        except Exception as e:
            logger.debug(f"Error getting quality: {e}")
            return None

    def get_status1(self) -> Optional[str]:
        """Get status field 1 (typically S/N ratio)"""
        if not self.is_connected():
            return None
        try:
            return self.client.client.main.get_status1()
        except Exception as e:
            logger.debug(f"Error getting status1: {e}")
            return None

    def get_status2(self) -> Optional[str]:
        """Get status field 2"""
        if not self.is_connected():
            return None
        try:
            return self.client.client.main.get_status2()
        except Exception as e:
            logger.debug(f"Error getting status2: {e}")
            return None

    def get_signal_metrics(self) -> Dict[str, Any]:
        """Get comprehensive signal metrics including quality, S/N, and calculated RST"""
        metrics = {
            "quality": self.get_quality(),
            "status1": self.get_status1(),  # Usually S/N
            "status2": self.get_status2(),
            "snr": None,
            "rst_estimate": None,
            "rsq_estimate": None
        }

        # Try to parse S/N from status1
        if metrics["status1"]:
            try:
                # Status1 typically shows "s/n: XX dB" or similar
                import re
                match = re.search(r'[-+]?\d+\.?\d*', metrics["status1"])
                if match:
                    metrics["snr"] = float(match.group())
            except Exception:
                pass

        # Calculate RST/RSQ estimate based on quality and SNR
        if metrics["quality"] is not None:
            metrics["rst_estimate"] = self._calculate_rst(metrics["quality"], metrics["snr"])
            metrics["rsq_estimate"] = self._calculate_rsq(metrics["quality"], metrics["snr"])

        return metrics

    def _calculate_readability(self, quality: float) -> int:
        """Calculate R (Readability) component: 1-5"""
        if quality >= 90:
            return 5
        elif quality >= 75:
            return 4
        elif quality >= 50:
            return 3
        elif quality >= 25:
            return 2
        else:
            return 1

    def _calculate_signal(self, quality: float, snr: Optional[float]) -> int:
        """Calculate S (Signal) component: 1-9"""
        if snr is not None:
            if snr >= 40:
                return 9
            elif snr >= 30:
                return 8
            elif snr >= 20:
                return 7
            elif snr >= 10:
                return 6
            elif snr >= 5:
                return 5
            elif snr >= 0:
                return 4
            elif snr >= -5:
                return 3
            elif snr >= -10:
                return 2
            else:
                return 1
        else:
            return max(1, min(9, int(quality / 11) + 1))

    def _calculate_rst(self, quality: float, snr: Optional[float]) -> str:
        """Calculate RST (Readability-Signal-Tone) estimate for CW/phone modes"""
        r = self._calculate_readability(quality)
        s = self._calculate_signal(quality, snr)
        t = 9
        return f"{r}{s}{t}"

    def _calculate_rsq(self, quality: float, snr: Optional[float]) -> str:
        """Calculate RSQ (Readability-Signal-Quality) estimate for digital modes"""
        r = self._calculate_readability(quality)
        s = self._calculate_signal(quality, snr)

        if quality >= 95:
            q = 9
        elif quality >= 85:
            q = 8
        elif quality >= 75:
            q = 7
        elif quality >= 65:
            q = 6
        elif quality >= 50:
            q = 5
        elif quality >= 35:
            q = 4
        elif quality >= 25:
            q = 3
        elif quality >= 15:
            q = 2
        else:
            q = 1

        return f"{r}{s}{q}"

    def get_trx_status(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.main.get_trx_state()
        except Exception as e:
            # Check if this is a connection error
            if self._is_connection_error(e):
                if self._connected:
                    logger.warning("FlDigi connection lost")
                    self._connected = False
            else:
                logger.debug(f"Error getting TRX status: {e}")
            return None

    def tx(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.tx()
            logger.info("Started TX")
            return True
        except Exception as e:
            logger.debug(f"Error starting TX: {e}")
            return False

    def rx(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.rx()
            logger.info("Switched to RX")
            return True
        except Exception as e:
            logger.debug(f"Error switching to RX: {e}")
            return False

    def tune(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.tune()
            logger.info("Started TUNE")
            return True
        except Exception as e:
            logger.debug(f"Error starting TUNE: {e}")
            return False

    def abort(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.abort()
            logger.info("Aborted TX/TUNE")
            return True
        except Exception as e:
            logger.debug(f"Error aborting: {e}")
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
            # Check if this is a connection error
            if self._is_connection_error(e):
                if self._connected:
                    logger.warning("FlDigi connection lost")
                    self._connected = False
            else:
                logger.debug(f"Error getting RX text: {e}")
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
            logger.debug(f"Error getting TX text: {e}")
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
            logger.debug(f"Error transmitting text: {e}")
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
            logger.debug(f"Error starting live TX: {e}")
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
            logger.debug(f"Error adding characters to TX buffer: {e}")
            return False

    def send_backspace(self) -> bool:
        if not self.is_connected():
            return False

        try:
            self.client.client.text.add_tx('\x08')
            return True
        except Exception as e:
            logger.debug(f"Error sending backspace: {e}")
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
            logger.debug(f"Error ending TX: {e}")
            return False

    def clear_rx(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.text.clear_rx()
            logger.info("Cleared RX buffer")
            return True
        except Exception as e:
            logger.debug(f"Error clearing RX: {e}")
            return False

    def clear_tx(self) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.text.clear_tx()
            logger.info("Cleared TX buffer")
            return True
        except Exception as e:
            logger.debug(f"Error clearing TX: {e}")
            return False

    def get_rsid(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return self.client.main.rsid
        except Exception as e:
            logger.debug(f"Error getting RSID: {e}")
            return None

    def set_rsid(self, enabled: bool) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.main.rsid = enabled
            logger.info(f"Set RSID to: {enabled}")
            return True
        except Exception as e:
            logger.debug(f"Error setting RSID: {e}")
            return False

    def get_txid(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return bool(self.client.client.main.get_txid())
        except Exception as e:
            logger.debug(f"Error getting TXID: {e}")
            return None

    def set_txid(self, enabled: bool) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.client.main.set_txid(bool(enabled))
            logger.info(f"Set TXID to: {enabled}")
            return True
        except Exception as e:
            logger.debug(f"Error setting TXID: {e}")
            return False

    def get_rig_name(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.rig.name
        except Exception as e:
            logger.debug(f"Error getting rig name: {e}")
            return None

    def get_rig_frequency(self) -> Optional[float]:
        if not self.is_connected():
            return None
        try:
            return self.client.rig.frequency
        except Exception as e:
            logger.debug(f"Error getting rig frequency: {e}")
            return None

    def set_rig_frequency(self, frequency: float) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.rig.frequency = frequency
            logger.info(f"Set rig frequency to: {frequency} Hz")
            return True
        except Exception as e:
            logger.debug(f"Error setting rig frequency: {e}")
            return False

    def get_rig_mode(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            return self.client.rig.mode
        except Exception as e:
            logger.debug(f"Error getting rig mode: {e}")
            return None

    def set_rig_mode(self, mode: str) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.rig.mode = mode
            logger.info(f"Set rig mode to: {mode}")
            return True
        except Exception as e:
            logger.debug(f"Error setting rig mode: {e}")
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
            logger.debug(f"Error getting squelch status: {e}")
            return None

    def set_squelch(self, enabled: bool) -> bool:
        if not self.is_connected():
            return False
        try:
            self.client.client.main.set_squelch(bool(enabled))
            logger.info(f"Set squelch to: {enabled}")
            return True
        except Exception as e:
            logger.debug(f"Error setting squelch: {e}")
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
            logger.debug(f"Error getting squelch level: {e}")
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
            logger.debug(f"Error setting squelch level: {e}")
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
