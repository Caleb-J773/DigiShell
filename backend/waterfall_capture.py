"""
FlDigi Waterfall Window Capture Service

This module captures the FlDigi waterfall window and streams it to web clients.
Works on both Linux (X11) and Windows. This is a BETA feature and disabled by default.
"""

import asyncio
import base64
import io
import sys
import time
from typing import Optional, Tuple
from pathlib import Path

# Platform-specific imports
if sys.platform == "linux":
    # Linux: Use X11/Xlib
    try:
        from Xlib import X, display as xdisplay
        from Xlib.error import DisplayConnectionError
        XLIB_AVAILABLE = True
    except ImportError:
        XLIB_AVAILABLE = False
else:
    XLIB_AVAILABLE = False

if sys.platform == "win32":
    # Windows: Use pywin32
    try:
        import win32gui
        import win32ui
        import win32con
        from ctypes import windll
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False

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
        if sys.platform == "linux":
            return XLIB_AVAILABLE and PIL_AVAILABLE
        elif sys.platform == "win32":
            return WIN32_AVAILABLE and PIL_AVAILABLE
        else:
            return False

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
            platform_req = "Linux with X11, python-xlib" if sys.platform == "linux" else "Windows with pywin32"
            raise RuntimeError(
                f"Waterfall capture not available. "
                f"Requires {platform_req} and Pillow."
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

    def _find_fldigi_window_windows(self) -> Optional[int]:
        """
        Find the FlDigi window on Windows by searching for window titles.
        Returns the window handle (HWND) if found, None otherwise.
        """
        if sys.platform != "win32" or not WIN32_AVAILABLE:
            return None

        try:
            # List to store found window handles
            found_handles = []

            def enum_windows_callback(hwnd, _):
                """Callback for EnumWindows to find FlDigi window."""
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text and 'fldigi' in window_text.lower():
                        found_handles.append(hwnd)
                return True

            # Enumerate all top-level windows
            win32gui.EnumWindows(enum_windows_callback, None)

            if found_handles:
                return found_handles[0]  # Return first match

            return None

        except Exception as e:
            print(f"Error finding FlDigi window on Windows: {e}")
            return None

    def _capture_window_windows(self) -> Optional[bytes]:
        """
        Capture the FlDigi window on Windows and return as JPEG bytes.
        Returns None if capture fails.
        """
        if sys.platform != "win32" or not WIN32_AVAILABLE:
            return None

        try:
            # Find window if not already found
            if not self.window_id:
                self.window_id = self._find_fldigi_window_windows()
                if not self.window_id:
                    return None

            hwnd = self.window_id

            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            # Create device contexts
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            # Create bitmap
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)

            # Copy window content to bitmap
            # Use PrintWindow for better compatibility with some windows
            windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)  # 2 = PW_RENDERFULLCONTENT

            # Convert bitmap to PIL Image
            bmpinfo = save_bitmap.GetInfo()
            bmpstr = save_bitmap.GetBitmapBits(True)

            image = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr,
                'raw',
                'BGRX',
                0,
                1
            )

            # Cleanup GDI objects
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            # Encode as JPEG
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=self.jpeg_quality, optimize=True)

            return buffer.getvalue()

        except Exception as e:
            # Window might have been closed or moved
            print(f"Error capturing window on Windows: {e}")
            self.window_id = None
            return None

    def _capture_window(self) -> Optional[bytes]:
        """
        Capture the FlDigi window and return as JPEG bytes.
        Platform-agnostic wrapper that calls the appropriate platform-specific method.
        Returns None if capture fails.
        """
        if sys.platform == "linux":
            return self._capture_window_linux()
        elif sys.platform == "win32":
            return self._capture_window_windows()
        else:
            return None

    def _capture_window_linux(self) -> Optional[bytes]:
        """
        Capture the FlDigi window on Linux/X11 and return as JPEG bytes.
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
