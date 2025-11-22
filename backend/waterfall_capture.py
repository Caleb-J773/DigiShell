"""
FlDigi Waterfall Window Capture Service

This module captures the FlDigi waterfall window and streams it to web clients.
Only works on Linux with X11. This is a BETA feature and disabled by default.
"""

import asyncio
import base64
import io
import sys
import time
from typing import Optional, Tuple
from pathlib import Path

# Only import X11 libraries if on Linux
if sys.platform == "linux":
    try:
        from Xlib import X, display as xdisplay
        from Xlib.error import DisplayConnectionError
        XLIB_AVAILABLE = True
    except ImportError:
        XLIB_AVAILABLE = False
else:
    XLIB_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class WaterfallCaptureService:
    """
    Service to capture FlDigi waterfall window and stream it as JPEG images.

    This is disabled by default and only runs when explicitly enabled by user
    in the beta features settings.
    """

    def __init__(self):
        self.enabled = False
        self.running = False
        self.display = None
        self.window = None
        self.window_id = None
        self.capture_task = None
        self.subscribers = set()  # WebSocket connections to stream to
        self.fps = 15  # Target frames per second (conservative for waterfall)
        self.jpeg_quality = 75  # Balance between quality and bandwidth

    def is_available(self) -> bool:
        """Check if waterfall capture is available on this system."""
        return XLIB_AVAILABLE and PIL_AVAILABLE and sys.platform == "linux"

    def get_status(self) -> dict:
        """Get current status of the waterfall capture service."""
        return {
            "available": self.is_available(),
            "enabled": self.enabled,
            "running": self.running,
            "window_found": self.window is not None,
            "subscribers": len(self.subscribers),
            "platform": sys.platform
        }

    async def enable(self):
        """Enable the waterfall capture service."""
        if not self.is_available():
            raise RuntimeError(
                "Waterfall capture not available. "
                "Requires Linux with X11, python-xlib, and Pillow."
            )

        self.enabled = True

        # Start capture loop if not already running
        if not self.running:
            self.capture_task = asyncio.create_task(self._capture_loop())

    async def disable(self):
        """Disable the waterfall capture service."""
        self.enabled = False

        # Stop capture loop
        if self.capture_task:
            self.capture_task.cancel()
            try:
                await self.capture_task
            except asyncio.CancelledError:
                pass
            self.capture_task = None

        # Close X11 connection
        if self.display:
            self.display.close()
            self.display = None
            self.window = None
            self.window_id = None

        self.running = False

    def add_subscriber(self, websocket):
        """Add a WebSocket subscriber to receive frames."""
        self.subscribers.add(websocket)

    def remove_subscriber(self, websocket):
        """Remove a WebSocket subscriber."""
        self.subscribers.discard(websocket)

    def _find_fldigi_window(self) -> Optional[int]:
        """
        Find the FlDigi window by searching for window titles.
        Returns the window ID if found, None otherwise.
        """
        try:
            if not self.display:
                self.display = xdisplay.Display()

            root = self.display.screen().root

            # Get list of all windows using _NET_CLIENT_LIST
            try:
                window_list_atom = self.display.intern_atom('_NET_CLIENT_LIST')
                window_list = root.get_full_property(
                    window_list_atom,
                    X.AnyPropertyType
                )

                if window_list:
                    for window_id in window_list.value:
                        try:
                            window = self.display.create_resource_object('window', window_id)
                            window_name = window.get_wm_name()

                            # Look for FlDigi in window title
                            if window_name and 'fldigi' in window_name.lower():
                                return window_id
                        except Exception:
                            continue
            except Exception:
                pass

            # Fallback: Try to find by iterating through windows
            def search_windows(win):
                try:
                    window_name = win.get_wm_name()
                    if window_name and 'fldigi' in window_name.lower():
                        return win.id

                    # Search children
                    children = win.query_tree().children
                    for child in children:
                        result = search_windows(child)
                        if result:
                            return result
                except Exception:
                    pass
                return None

            return search_windows(root)

        except Exception as e:
            print(f"Error finding FlDigi window: {e}")
            return None

    def _capture_window(self) -> Optional[bytes]:
        """
        Capture the FlDigi window and return as JPEG bytes.
        Returns None if capture fails.
        """
        try:
            # Find window if not already found
            if not self.window:
                self.window_id = self._find_fldigi_window()
                if not self.window_id:
                    return None

                self.window = self.display.create_resource_object('window', self.window_id)

            # Get window geometry
            geom = self.window.get_geometry()
            width, height = geom.width, geom.height

            # Capture window image
            raw_image = self.window.get_image(
                0, 0, width, height,
                X.ZPixmap,
                0xffffffff
            )

            # Convert to PIL Image
            # X11 returns BGRX format (32-bit with padding)
            image = Image.frombytes(
                "RGB",
                (width, height),
                raw_image.data,
                "raw",
                "BGRX"
            )

            # Encode as JPEG
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=self.jpeg_quality, optimize=True)

            return buffer.getvalue()

        except Exception as e:
            # Window might have been closed or moved
            print(f"Error capturing window: {e}")
            self.window = None
            self.window_id = None
            return None

    async def _capture_loop(self):
        """
        Main capture loop. Captures frames and sends to all subscribers.
        """
        self.running = True
        frame_delay = 1.0 / self.fps

        try:
            while self.enabled:
                start_time = time.time()

                # Only capture if we have subscribers
                if self.subscribers:
                    # Run blocking capture in thread pool to avoid blocking event loop
                    loop = asyncio.get_event_loop()
                    jpeg_bytes = await loop.run_in_executor(None, self._capture_window)

                    if jpeg_bytes:
                        # Encode as base64 for WebSocket transmission
                        b64_image = base64.b64encode(jpeg_bytes).decode('utf-8')

                        # Send to all subscribers
                        dead_subs = set()
                        for subscriber in self.subscribers:
                            try:
                                await subscriber.send_json({
                                    "type": "waterfall_frame",
                                    "image": b64_image,
                                    "timestamp": time.time()
                                })
                            except Exception:
                                # Mark dead connections for removal
                                dead_subs.add(subscriber)

                        # Remove dead subscribers
                        self.subscribers -= dead_subs

                # Sleep to maintain target FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_delay - elapsed)
                await asyncio.sleep(sleep_time)

        except asyncio.CancelledError:
            pass
        finally:
            self.running = False


# Global singleton instance
waterfall_service = WaterfallCaptureService()
