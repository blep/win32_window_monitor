"""
Events constant for use with set_win_event_hook().
"""


class NamedInt(int):
    """
    Kind of a enum that allows wrapping of any integer value, but report the name when matching
    a declared class constant field.

    See https://docs.python.org/3/reference/datamodel.html#customizing-class-creation for an
    example of the logic used to convert integer constant to actual instance of the class.
    """

    _value2member_map_ = None

    def __new__(cls, value):
        if not isinstance(value, int):
            raise ValueError(f'expected value to be a int, but was {value!r}')
        named_int = cls._value2member_map_.get(value) if cls._value2member_map_ else None
        if named_int is None:
            named_int = int.__new__(cls, value)
            named_int._name = None
        return named_int

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return int(self)

    @classmethod
    def __init_subclass__(cls):
        """Maps the integer class field to actual instance of the class."""
        cls._value2member_map_ = {}
        for name, value in cls.__dict__.items():
            if isinstance(value, int):
                member = cls(value)
                member._name = name
                setattr(cls, name, member)
                cls._value2member_map_[value] = member

    @classmethod
    def names(cls):
        return (value.name for value in cls._value2member_map_.values())

    @classmethod
    def values(cls):
        return iter(cls._value2member_map_.values())

    def __repr__(self):
        class_name = self.__class__.__name__
        if self._name is not None:
            return f'{class_name}.{self._name}'
        else:
            return f'{class_name}(0x{int(self):x})'

    def __str__(self):
        if self._name is not None:
            return self._name
        else:
            return '0x%x' % int(self)

    def __eq__(self, other):
        return int(self) == other

    def __hash__(self):
        return super().__hash__()


class HookEvent(NamedInt):
    """
    Event constants for set_event_hook() and its callback.
    Names are identical to Windows SDK, with EVENT_ prefix stripped.

    See https://learn.microsoft.com/en-us/windows/win32/winauto/event-constants for a detailed
    and accurate description of each event.

    Extends int to allow wrapping of any event id: HookEvent(0x1234), even if it is missing in the constant declared below.
    """

    # Lowest possible event id.
    MIN = 0x00000001
    # highest possible event id.
    MAX = 0x7FFFFFFF

    # Start of the range for Accessibility Interoperability Alliance (AIA) WinEvent
    AIA_START = 0xA000
    # End of the range for Accessibility Interoperability Alliance (AIA) WinEvent
    AIA_END = 0xAFFF

    # An object's KeyboardShortcut property changed.
    OBJECT_ACCELERATORCHANGE = 0x8012

    # Sent when a window is cloaked. A cloaked window still exists but is invisible to the user.
    OBJECT_CLOAKED = 0x8017

    # A window object's scrolling has ended.
    OBJECT_CONTENTSCROLLED = 0x8015

    # An object has been created.
    OBJECT_CREATE = 0x8000

    # An object's DefaultAction property has changed.
    OBJECT_DEFACTIONCHANGE = 0x8011

    # An object's Description property has changed.
    OBJECT_DESCRIPTIONCHANGE = 0x800D

    # An object has been destroyed.
    OBJECT_DESTROY = 0x8001

    # The user started to drag an element.
    OBJECT_DRAGSTART = 0x8021

    # The user has ended a drag operation before dropping the dragged element on a drop target.
    OBJECT_DRAGCANCEL = 0x8022

    # The user dropped an element on a drop target.
    OBJECT_DRAGCOMPLETE = 0x8023

    # The user dragged an element into a drop target's boundary.
    OBJECT_DRAGENTER = 0x8024

    # The user dragged an element out of a drop target's boundary.
    OBJECT_DRAGLEAVE = 0x8025

    # The user dropped an element on a drop target.
    OBJECT_DRAGDROPPED = 0x8026

    # The highest object event value.
    OBJECT_END = 0x80FF

    # An object has received the keyboard focus.
    OBJECT_FOCUS = 0x8005

    # An object's Help property has changed.
    OBJECT_HELPCHANGE = 0x8010

    # An object is hidden.
    OBJECT_HIDE = 0x8003

    # A window that hosts other accessible objects has changed the hosted objects.
    OBJECT_HOSTEDOBJECTSINVALIDATED = 0x8020

    # An IME window has become hidden.
    OBJECT_IME_HIDE = 0x8028

    # An IME window has become visible.
    OBJECT_IME_SHOW = 0x8027

    # The size or position of an IME window has changed.
    OBJECT_IME_CHANGE = 0x8029

    # An object has been invoked; for example, the user has clicked a button.
    OBJECT_INVOKED = 0x8013

    # An object that is part of a live region has changed.
    OBJECT_LIVEREGIONCHANGED = 0x8019

    # An object has changed location, shape, or size.
    OBJECT_LOCATIONCHANGE = 0x800B

    # An object's Name property has changed.
    OBJECT_NAMECHANGE = 0x800C

    # An object has a new parent object.
    OBJECT_PARENTCHANGE = 0x800F

    # A container object has added, removed, or reordered its children.
    OBJECT_REORDER = 0x8004

    # The selection within a container object has changed.
    OBJECT_SELECTION = 0x8006

    # A child within a container object has been added to an existing selection.
    OBJECT_SELECTIONADD = 0x8007

    # An item within a container object has been removed from the selection.
    OBJECT_SELECTIONREMOVE = 0x8008

    # Numerous selection changes have occurred within a container object.
    OBJECT_SELECTIONWITHIN = 0x8009

    # A hidden object is shown.
    OBJECT_SHOW = 0x8002

    # An object's state has changed.
    OBJECT_STATECHANGE = 0x800A

    # The conversion target within an IME composition has changed.
    OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED = 0x8030

    # An object's text selection has changed.
    OBJECT_TEXTSELECTIONCHANGED = 0x8014

    # Sent when a window is uncloaked.
    OBJECT_UNCLOAKED = 0x8018

    # An object's Value property has changed.
    OBJECT_VALUECHANGE = 0x800E

    # Range of event constant values reserved for OEMs.
    OEM_DEFINED_START = 0x0101
    OEM_DEFINED_END = 0x01FF

    # An alert has been generated.
    SYSTEM_ALERT = 0x0002

    # A preview rectangle is being displayed.
    SYSTEM_ARRANGMENTPREVIEW = 0x8016

    # A window has lost mouse capture.
    SYSTEM_CAPTUREEND = 0x0009

    # A window has received mouse capture.
    SYSTEM_CAPTURESTART = 0x0008

    # A window has exited context-sensitive Help mode.
    SYSTEM_CONTEXTHELPEND = 0x000D

    # A window has entered context-sensitive Help mode.
    SYSTEM_CONTEXTHELPSTART = 0x000C

    # The active desktop has been switched.
    SYSTEM_DESKTOPSWITCH = 0x0020

    # A dialog box has been closed.
    SYSTEM_DIALOGEND = 0x0011

    # A dialog box has been displayed.
    SYSTEM_DIALOGSTART = 0x0010

    # An application is about to exit drag-and-drop mode.
    SYSTEM_DRAGDROPEND = 0x000F

    # An application is about to enter drag-and-drop mode.
    SYSTEM_DRAGDROPSTART = 0x000E

    # The highest system event value.
    SYSTEM_END = 0x00FF

    # The foreground window has changed.
    SYSTEM_FOREGROUND = 0x0003

    # A pop-up menu has been closed.
    SYSTEM_MENUPOPUPEND = 0x0007

    # A pop-up menu has been displayed.
    SYSTEM_MENUPOPUPSTART = 0x0006

    # A menu from the menu bar has been closed.
    SYSTEM_MENUEND = 0x0005

    # A menu item on the menu bar has been selected.
    SYSTEM_MENUSTART = 0x0004

    # A window object is about to be restored.
    SYSTEM_MINIMIZEEND = 0x0017

    # A window object is about to be minimized.
    SYSTEM_MINIMIZESTART = 0x0016

    # The movement or resizing of a window has finished.
    SYSTEM_MOVESIZEEND = 0x000B

    # A window is being moved or resized.
    SYSTEM_MOVESIZESTART = 0x000A

    # Scrolling has ended on a scroll bar.
    SYSTEM_SCROLLINGEND = 0x0013

    # Scrolling has started on a scroll bar.
    SYSTEM_SCROLLINGSTART = 0x0012

    # A sound has been played.
    SYSTEM_SOUND = 0x0001

    # The user has released ALT+TAB.
    SYSTEM_SWITCHEND = 0x0015

    # The user has pressed ALT+TAB, which activates the switch window.
    SYSTEM_SWITCHSTART = 0x0014

    # Start of range reserved for UI Automation event identifiers.
    UIA_EVENTID_START = 0x4E00
    # End of range reserved for UI Automation event identifiers.
    UIA_EVENTID_END = 0x4EFF

    # Start of range reserved for UI Automation property-changed event identifiers.
    UIA_PROPID_START = 0x7500
    # End of range reserved for UI Automation property-changed event identifiers.
    UIA_PROPID_END = 0x75FF


class ObjectId(NamedInt):
    """Object ids constants for set_event_hook() callback id_object parameter.
    Names are identical to Windows SDK, with OBJID_ prefix stripped.

    See https://learn.microsoft.com/en-us/windows/win32/winauto/object-identifiers for a detailed
    and accurate description of each events.

    Extends int to allow wrapping of any event id: ObjectId(0x1234),
    even if it is missing in the constant declared below.
    """
    ALERT = 0xFFFFFFF6  #: An alert associated with a window or an application.
    CARET = 0xFFFFFFF8  #: The text insertion bar (caret) in the window.
    CLIENT = 0xFFFFFFFC  #: The window's client area.
    CURSOR = 0xFFFFFFF7  #: The mouse pointer.
    HSCROLL = 0xFFFFFFFA  #: The window's horizontal scroll bar.
    NATIVEOM = 0xFFFFFFF0  #: Third-party applications expose their object model.
    MENU = 0xFFFFFFFD  #: The window's menu bar.
    QUERYCLASSNAMEIDX = 0xFFFFFFF4  #: Oleacc.dll uses this internally.
    SIZEGRIP = 0xFFFFFFF9  #: The window's size grip.
    SOUND = 0xFFFFFFF5  #: A sound object.
    SYSMENU = 0xFFFFFFFF  #: The window's system menu.
    TITLEBAR = 0xFFFFFFFE  #: The window's title bar.
    VSCROLL = 0xFFFFFFFB  #: The window's vertical scroll bar.
    WINDOW = 0x00000000  #: The window itself.
