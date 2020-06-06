# Windows implementation of PyAutoGUI functions using Direct Input.
# BSD license
# Al Sweigart al@inventwithpython.com

import ctypes
import ctypes.wintypes
import pyautogui
from pyautogui import LEFT, MIDDLE, RIGHT

import sys
if sys.platform != 'win32':
    raise Exception('The pyautogui_win module should only be loaded on a Windows system.')


# Fixes the scaling issues where PyAutoGUI was reporting the wrong resolution:
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass  # Windows XP doesn't support this, so just do nothing.


"""
A lot of this code is probably repeated from win32 extensions module, but I didn't want to have that dependency.

Note: According to http://msdn.microsoft.com/en-us/library/windows/desktop/ms646260(v=vs.85).aspx
the ctypes.windll.user32.mouse_event() function has been superceded by SendInput.

SendInput() is documented here: http://msdn.microsoft.com/en-us/library/windows/desktop/ms646310(v=vs.85).aspx

UPDATE: SendInput() doesn't seem to be working for me. I've switched back to mouse_event()."""


# Event codes to be passed to the mouse_event() win32 function.
# Documented here: http://msdn.microsoft.com/en-us/library/windows/desktop/ms646273(v=vs.85).aspx
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_LEFTCLICK = MOUSEEVENTF_LEFTDOWN+MOUSEEVENTF_LEFTUP
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_RIGHTCLICK = MOUSEEVENTF_RIGHTDOWN+MOUSEEVENTF_RIGHTUP
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_MIDDLECLICK = MOUSEEVENTF_MIDDLEDOWN+MOUSEEVENTF_MIDDLEUP

MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x01000
WHEEL_DELTA = 120

# Documented here: http://msdn.microsoft.com/en-us/library/windows/desktop/ms646304(v=vs.85).aspx
KEYEVENTF_KEYDOWN = 0x0000  # Technically this constant doesn't exist in the MS documentation. It's the lack of KEYEVENTF_KEYUP that means pressing the key down.
KEYEVENTF_KEYUP = 0x0002

# Documented here: http://msdn.microsoft.com/en-us/library/windows/desktop/ms646270(v=vs.85).aspx
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1


# This ctypes structure is for a Win32 POINT structure,
# which is documented here: http://msdn.microsoft.com/en-us/library/windows/desktop/dd162805(v=vs.85).aspx
# The POINT structure is used by GetCursorPos().
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

# These ctypes structures are for Win32 INPUT, MOUSEINPUT, KEYBDINPUT, and HARDWAREINPUT structures,
# used by SendInput and documented here: http://msdn.microsoft.com/en-us/library/windows/desktop/ms646270(v=vs.85).aspx
# Thanks to BSH for this StackOverflow answer: https://stackoverflow.com/questions/18566289/how-would-you-recreate-this-windows-api-structure-with-ctypes
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ('dx', ctypes.wintypes.LONG),
        ('dy', ctypes.wintypes.LONG),
        ('mouseData', ctypes.wintypes.DWORD),
        ('dwFlags', ctypes.wintypes.DWORD),
        ('time', ctypes.wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.wintypes.ULONG)),
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ('wVk', ctypes.wintypes.WORD),
        ('wScan', ctypes.wintypes.WORD),
        ('dwFlags', ctypes.wintypes.DWORD),
        ('time', ctypes.wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.wintypes.ULONG)),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ('uMsg', ctypes.wintypes.DWORD),
        ('wParamL', ctypes.wintypes.WORD),
        ('wParamH', ctypes.wintypes.DWORD)
    ]

class INPUT_I(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT),
                ("mi", MOUSEINPUT),
                ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", INPUT_I)]
# End of the SendInput win32 data structures.



""" Keyboard key mapping for pyautogui:
Documented at http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731(v=vs.85).aspx

The *KB dictionaries in pyautogui map a string that can be passed to keyDown(),
keyUp(), or press() into the code used for the OS-specific keyboard function.

They should always be lowercase, and the same keys should be used across all OSes."""
keyboardMapping = dict([(key, None) for key in pyautogui.KEY_NAMES])
keyboardMapping.update({
    'backspace': 0x0E,  # SC_BACK
    '\b': 0x0E,  # SC_BACK
    'super': 0xDB + 1024,  # SC_LWIN
    'tab': 0x0F,  # SC_TAB
    '\t': 0x0F,  # SC_TAB
    'enter': 0x1C,  # SC_RETURN
    '\n': 0x1C,  # SC_RETURN
    'return': 0x1C,  # SC_RETURN
    'shift': 0x2A,  # SC_SHIFT
    'ctrl': 0x1D,  # SC_CONTROL
    'alt': 0x38,  # SC_MENU
    'capslock': 0x3A,  # SC_CAPITAL
    'esc': 0x01,  # SC_ESCAPE
    'escape': 0x01,  # SC_ESCAPE
    'convert': 0x79,  # SC_CONVERT
    'nonconvert': 0x7B,  # SC_NONCONVERT
    ' ': 0x39,  # SC_SPACE
    'space': 0x39,  # SC_SPACE
    'pgup': 0xC9 + 1024,  # SC_PRIOR
    'pgdn': 0xD1 + 1024,  # SC_NEXT
    'pageup': 0xC9 + 1024,  # SC_PRIOR
    'pagedown': 0xD1 + 1024,  # SC_NEXT
    'end': 0xCF + 1024,  # SC_END
    'home': 0xC7 + 1024,  # SC_HOME
    'left': 0xCB + 1024,  # SC_LEFT
    'up': 0xC8 + 1024,  # SC_UP
    'right': 0xCD + 1024,  # SC_RIGHT
    'down': 0xD0 + 1024,  # SC_DOWN
    'prtsc': 0xB7 + 1024,  # SC_SNAPSHOT
    'prtscr': 0xB7 + 1024,  # SC_SNAPSHOT
    'prntscrn': 0xB7 + 1024,  # SC_SNAPSHOT
    'printscreen': 0xB7 + 1024,  # SC_SNAPSHOT
    'insert': 0xD2 + 1024,  # SC_INSERT
    'del': 0xD3 + 1024,  # SC_DELETE
    'delete': 0xD3 + 1024,  # SC_DELETE
    'help': 0x63,  # SC_HELP
    'win': 0xDB + 1024,  # SC_LWIN
    'winleft': 0xDB + 1024,  # SC_LWIN
    'winright': 0xDC + 1024,  # SC_RWIN
    'apps': 0xDD + 1024, # SC_APPS
    'sleep': 0xDF + 1024, # SC_SLEEP
    'num0': 0x52,  # SC_NUMPAD0
    'num1': 0x4F,  # SC_NUMPAD1
    'num2': 0x50,  # SC_NUMPAD2
    'num3': 0x51,  # SC_NUMPAD3
    'num4': 0x4B,  # SC_NUMPAD4
    'num5': 0x4C,  # SC_NUMPAD5
    'num6': 0x4D,  # SC_NUMPAD6
    'num7': 0x47,  # SC_NUMPAD7
    'num8': 0x48,  # SC_NUMPAD8
    'num9': 0x49,  # SC_NUMPAD9
    'multiply': 0x37,  # SC_MULTIPLY numpad *
    'add': 0x4E,  # SC_ADD numpad +
    'subtract': 0x4A,  # SC_SUBTRACT numpad -
    'decimal': 0x53,  # SC_DECIMAL
    'divide': 0xB5 + 1024,  # SC_DIVIDE
    'numenter': 0x9C + 1024,  # SC_NUMPADENTER
    'f1': 0x3B,  # SC_F1
    'f2': 0x3C,  # SC_F2
    'f3': 0x3D,  # SC_F3
    'f4': 0x3E,  # SC_F4
    'f5': 0x3F,  # SC_F5
    'f6': 0x40,  # SC_F6
    'f7': 0x41,  # SC_F7
    'f8': 0x42,  # SC_F8
    'f9': 0x43,  # SC_F9
    'f10': 0x44,  # SC_F10
    'f11': 0x57,  # SC_F11
    'f12': 0x58,  # SC_F12
    'f13': 0x64,  # SC_F13
    'f14': 0x65,  # SC_F14
    'f15': 0x66,  # SC_F15
    'f16': 0x67,  # SC_F16
    'f17': 0x68,  # SC_F17
    'f18': 0x69,  # SC_F18
    'f19': 0x6a,  # SC_F19
    'f20': 0x6b,  # SC_F20
    'f21': 0x6c,  # SC_F21
    'f22': 0x6d,  # SC_F22
    'f23': 0x6e,  # SC_F23
    'f24': 0x76,  # SC_F24
    'numlock': 0x45,  # SC_NUMLOCK
    'scrolllock': 0x46,  # SC_SCROLL
    'shiftleft': 0x2A,  # SC_LSHIFT
    'shiftright': 0x36,  # SC_RSHIFT
    'ctrlleft': 0x1D,  # SC_LCONTROL
    'ctrlright': 0x9D + 1024,  # SC_RCONTROL
    'altleft': 0x38,  # SC_LMENU
    'altright': 0xB8 + 1024,  # SC_RMENU
    'browserback': 0xEA + 1024,  # SC_BROWSER_BACK
    'browserforward': 0xE9 + 1024,  # SC_BROWSER_FORWARD
    'browserrefresh': 0xE7 + 1024,  # SC_BROWSER_REFRESH
    'browserstop': 0xE8 + 1024,  # SC_BROWSER_STOP
    'browsersearch': 0xE5 + 1024,  # SC_BROWSER_SEARCH
    'browserfavorites': 0xE6 + 1024,  # SC_BROWSER_FAVORITES
    'browserhome': 0xB2 + 1024,  # SC_BROWSER_HOME
    'volumemute': 0xA0 + 1024,  # SC_VOLUME_MUTE
    'volumedown': 0xAE + 1024,  # SC_VOLUME_DOWN
    'volumeup': 0xB0 + 1024,  # SC_VOLUME_UP
    'nexttrack': 0x99 + 1024,  # SC_MEDIA_NEXT_TRACK
    'prevtrack': 0x90 + 1024,  # SC_MEDIA_PREV_TRACK
    'stop': 0xA4 + 1024,  # SC_MEDIA_STOP
    'playpause': 0xA2 + 1024,  # SC_MEDIA_PLAY_PAUSE
    'launchmail': 0xEC + 1024,  # SC_LAUNCH_MAIL
    'launchmediaselect': 0xED + 1024,  # SC_LAUNCH_MEDIA_SELECT
    'launchapp1': 0xEB + 1024,  # SC_LAUNCH_APP1
    'launchapp2': 0xA1 + 1024,  # SC_LAUNCH_APP2
    "'": 0x28,
    '-': 0x0C,
    ',': 0x33,
    '.': 0x34,
    '/': 0x35,
    ';': 0x27,
    '[': 0x1A,
    '\\': 0x2B,
    ']': 0x1B,
    '`': 0x29,
    '=': 0x0D,
    '0': 0x0B,
    '1': 0x02,
    '2': 0x03,
    '3': 0x04,
    '4': 0x05,
    '5': 0x06,
    '6': 0x07,
    '7': 0x08,
    '8': 0x09,
    '9': 0x0A,
    'a': 0x1E,
    'b': 0x30,
    'c': 0x2E,
    'd': 0x20,
    'e': 0x12,
    'f': 0x21,
    'g': 0x22,
    'h': 0x23,
    'i': 0x17,
    'j': 0x24,
    'k': 0x25,
    'l': 0x26,
    'm': 0x32,
    'n': 0x31,
    'o': 0x18,
    'p': 0x19,
    'q': 0x10,
    'r': 0x13,
    's': 0x1F,
    't': 0x14,
    'u': 0x16,
    'v': 0x2F,
    'w': 0x11,
    'x': 0x2D,
    'y': 0x15,
    'z': 0x2C,
    '"': 0x28,
    '_': 0x0C,
    '<': 0x33,
    '>': 0x34,
    '?': 0x35,
    ':': 0x27,
    '{': 0x1A,
    '|': 0x2B,
    '}': 0x1B,
    '~': 0x29,
    '+': 0x0D,
    ')': 0x0B,
    '!': 0x02,
    '@': 0x03,
    '#': 0x04,
    '$': 0x05,
    '%': 0x06,
    '^': 0x07,
    '&': 0x08,
    '*': 0x09,
    '(': 0x0A,
    'A': 0x1E,
    'B': 0x30,
    'C': 0x2E,
    'D': 0x20,
    'E': 0x12,
    'F': 0x21,
    'G': 0x22,
    'H': 0x23,
    'I': 0x17,
    'J': 0x24,
    'K': 0x25,
    'L': 0x26,
    'M': 0x32,
    'N': 0x31,
    'O': 0x18,
    'P': 0x19,
    'Q': 0x10,
    'R': 0x13,
    'S': 0x1F,
    'T': 0x14,
    'U': 0x16,
    'V': 0x2F,
    'W': 0x11,
    'X': 0x2D,
    'Y': 0x15,
    'Z': 0x2C,
})


def _keyDown(key):
    """Performs a keyboard key press without the release. This will put that
    key in a held down state.

    NOTE: For some reason, this does not seem to cause key repeats like would
    happen if a keyboard key was held down on a text field.

    Args:
      key (str): The key to be pressed down. The valid names are listed in
      pyautogui.KEY_NAMES.

    Returns:
      None
    """
    if key not in keyboardMapping or keyboardMapping[key] is None:
        return

    needsShift = pyautogui.isShiftCharacter(key)

    keyCode = keyboardMapping[key]

    if keyCode >= 1024:
        keyCode = keyCode-1024
        flags = 0x0008 | 0x0001
    else:
        flags = 0x0008

    if needsShift:
        _keyDown('shift')

    extra = ctypes.c_ulong(0)
    ii_ = INPUT_I()
    ii_.ki = KEYBDINPUT(0, keyCode, flags, 0, ctypes.pointer(extra))
    x = INPUT(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    if needsShift:
        _keyUp('shift')


def _keyUp(key):
    """Performs a keyboard key release (without the press down beforehand).

    Args:
      key (str): The key to be released up. The valid names are listed in
      pyautogui.KEY_NAMES.

    Returns:
      None
    """
    if key not in keyboardMapping or keyboardMapping[key] is None:
        return

    needsShift = pyautogui.isShiftCharacter(key)

    keyCode = keyboardMapping[key]

    if keyCode >= 1024:
        keyCode = keyCode-1024
        flags = 0x0008 | 0x0001 | 0x0002
    else:
        flags = 0x0008 | 0x0002

    extra = ctypes.c_ulong(0)
    ii_ = INPUT_I()

    ii_.ki = KEYBDINPUT(0, keyCode, flags, 0, ctypes.pointer(extra))
    x = INPUT(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def _position():
    """Returns the current xy coordinates of the mouse cursor as a two-integer
    tuple by calling the GetCursorPos() win32 function.

    Returns:
      (x, y) tuple of the current xy coordinates of the mouse cursor.
    """

    cursor = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
    return (cursor.x, cursor.y)


def _size():
    """Returns the width and height of the screen as a two-integer tuple.

    Returns:
      (width, height) tuple of the screen size, in pixels.
    """
    return (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))


def _moveTo(x, y):
    """Send the mouse move event to Windows by calling SetCursorPos() win32
    function.

    Args:
      button (str): The mouse button, either 'left', 'middle', or 'right'
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.

    Returns:
      None
    """
    extra = ctypes.c_ulong(0)
    ii_ = INPUT_I()
    ii_.mi = MOUSEINPUT(x, y, 0, (MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE), 0, ctypes.pointer(extra))
    command = INPUT(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

    # ctypes.windll.user32.SetCursorPos(x, y)
    # This was a possible solution to issue #314 https://github.com/asweigart/pyautogui/issues/314
    # but I'd like to hang on to SetCursorPos because mouse_event() has been superceded.
    # _sendMouseEvent(MOUSEEVENTF_MOVE + MOUSEEVENTF_ABSOLUTE, x, y)


def _mouseDown(x, y, button):
    """Send the mouse down event to Windows by calling the mouse_event() win32
    function.

    Args:
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.
      button (str): The mouse button, either 'left', 'middle', or 'right'

    Returns:
      None
    """
    if button not in (LEFT, MIDDLE, RIGHT):
        raise ValueError('button arg to _click() must be one of "left", "middle", or "right", not %s'%button)

    if button == LEFT:
        EV = MOUSEEVENTF_LEFTDOWN
    elif button == MIDDLE:
        EV = MOUSEEVENTF_MIDDLEDOWN
    elif button == RIGHT:
        EV = MOUSEEVENTF_RIGHTDOWN

    try:
        _sendMouseEvent(EV, x, y)
    except (PermissionError, OSError):
        # TODO: We need to figure out how to prevent these errors, see https://github.com/asweigart/pyautogui/issues/60
        pass


def _mouseUp(x, y, button):
    """Send the mouse up event to Windows by calling the mouse_event() win32
    function.

    Args:
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.
      button (str): The mouse button, either 'left', 'middle', or 'right'

    Returns:
      None
    """
    if button not in (LEFT, MIDDLE, RIGHT):
        raise ValueError('button arg to _click() must be one of "left", "middle", or "right", not %s'%button)

    if button == LEFT:
        EV = MOUSEEVENTF_LEFTUP
    elif button == MIDDLE:
        EV = MOUSEEVENTF_MIDDLEUP
    elif button == RIGHT:
        EV = MOUSEEVENTF_RIGHTUP

    try:
        _sendMouseEvent(EV, x, y)
    except (PermissionError, OSError):  # TODO: We need to figure out how to prevent these errors, see https://github.com/asweigart/pyautogui/issues/60
        pass


def _click(x, y, button):
    """Send the mouse click event to Windows by calling the mouse_event() win32
    function.

    Args:
      button (str): The mouse button, either 'left', 'middle', or 'right'
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.

    Returns:
      None
    """
    if button not in (LEFT, MIDDLE, RIGHT):
        raise ValueError('button arg to _click() must be one of "left", "middle", or "right", not %s'%button)

    if button == LEFT:
        EV = MOUSEEVENTF_LEFTCLICK
    elif button == MIDDLE:
        EV = MOUSEEVENTF_MIDDLECLICK
    elif button == RIGHT:
        EV = MOUSEEVENTF_RIGHTCLICK

    try:
        _sendMouseEvent(EV, x, y)
    except (PermissionError, OSError):
        # TODO: We need to figure out how to prevent these errors, see https://github.com/asweigart/pyautogui/issues/60
        pass


def _sendMouseEvent(ev, x, y, dwData=0):
    """The helper function that actually makes the call to the mouse_event()
    win32 function.

    Args:
      ev (int): The win32 code for the mouse event. Use one of the MOUSEEVENTF_*
      constants for this argument.
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.
      dwData (int): The argument for mouse_event()'s dwData parameter. So far
        this is only used by mouse scrolling.

    Returns:
      None
    """
    assert x != None and y != None, 'x and y cannot be set to None'
    # TODO: ARG! For some reason, SendInput isn't working for mouse events. I'm switching to using the older mouse_event win32 function.
    # mouseStruct = MOUSEINPUT()
    # mouseStruct.dx = x
    # mouseStruct.dy = y
    # mouseStruct.mouseData = ev
    # mouseStruct.time = 0
    # mouseStruct.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0)) # according to https://stackoverflow.com/questions/13564851/generate-keyboard-events I can just set this. I don't really care about this value.
    # inputStruct = INPUT()
    # inputStruct.mi = mouseStruct
    # inputStruct.type = INPUT_MOUSE
    # ctypes.windll.user32.SendInput(1, ctypes.pointer(inputStruct), ctypes.sizeof(inputStruct))

    # TODO Note: We need to handle additional buttons, which I believe is documented here:
    # https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-mouse_event

    extra = ctypes.c_ulong(0)
    ii_ = INPUT_I()
    ii_.mi = MOUSEINPUT(x, y, dwData, ev, 0, ctypes.pointer(extra))
    x = INPUT(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    #width, height = _size()
    #convertedX = 65536*x//width+1
    #convertedY = 65536*y//height+1
    #ctypes.windll.user32.mouse_event(ev, ctypes.c_long(convertedX), ctypes.c_long(convertedY), dwData, 0)

    # TODO: Too many false positives with this code: See: https://github.com/asweigart/pyautogui/issues/108
    # if ctypes.windll.kernel32.GetLastError() != 0:
    #    raise ctypes.WinError()


def _scroll(clicks, x=None, y=None):
    """Send the mouse vertical scroll event to Windows by calling the
    mouse_event() win32 function.

    Args:
      clicks (int): The amount of scrolling to do. A positive value is the mouse
      wheel moving forward (scrolling up), a negative value is backwards (down).
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.

    Returns:
      None
    """
    startx, starty = _position()
    width, height = _size()

    if x is None:
        x = startx
    else:
        if x < 0:
            x = 0
        elif x >= width:
            x = width-1
    if y is None:
        y = starty
    else:
        if y < 0:
            y = 0
        elif y >= height:
            y = height-1

    try:
        _sendMouseEvent(MOUSEEVENTF_WHEEL, x, y, dwData=clicks * WHEEL_DELTA)
    except (PermissionError, OSError):  # TODO: We need to figure out how to prevent these errors, see https://github.com/asweigart/pyautogui/issues/60
        pass


def _hscroll(clicks, x, y):
    """Send the mouse horizontal scroll event to Windows by calling the
    mouse_event() win32 function.

    Args:
      clicks (int): The amount of scrolling to do. A positive value is the mouse
      wheel moving right, a negative value is moving left.
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.

    Returns:
      None
    """
    startx, starty = _position()
    width, height = _size()

    if x is None:
        x = startx
    else:
        if x < 0:
            x = 0
        elif x >= width:
            x = width-1
    if y is None:
        y = starty
    else:
        if y < 0:
            y = 0
        elif y >= height:
            y = height-1

    try:
        _sendMouseEvent(MOUSEEVENTF_HWHEEL, x, y, dwData=clicks*WHEEL_DELTA)
    except (PermissionError, OSError):  # TODO: We need to figure out how to prevent these errors, see https://github.com/asweigart/pyautogui/issues/60
        pass


def _vscroll(clicks, x, y):
    """A wrapper for _scroll(), which does vertical scrolling.

    Args:
      clicks (int): The amount of scrolling to do. A positive value is the mouse
      wheel moving forward (scrolling up), a negative value is backwards (down).
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.

    Returns:
      None
    """
    return _scroll(clicks, x, y)

