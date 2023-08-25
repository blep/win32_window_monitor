from queue import Queue
from threading import Lock
from libc.stddef cimport wchar_t
from cpython.pythread cimport PyThread_acquire_lock, PyThread_release_lock, PyThread_type_lock

cdef extern from "pythread.h":
    cdef const int WAIT_LOCK

cdef extern from "stdint.h":
    ctypedef int intptr_t

cdef extern from "windows.h":
    ctypedef unsigned long DWORD
    ctypedef unsigned long LONG
    ctypedef unsigned int UINT
    ctypedef wchar_t WCHAR
    ctypedef wchar_t* LPWCHAR
    ctypedef unsigned int WPARAM
    ctypedef long LPARAM
    ctypedef long LRESULT
    ctypedef int BOOL
    ctypedef long HRESULT
    ctypedef void *HWND
    ctypedef void *HMODULE
    ctypedef void *HWINEVENTHOOK


    const UINT WINEVENT_OUTOFCONTEXT
    const UINT EVENT_SYSTEM_FOREGROUND
    const WPARAM WINEVENT_SKIPOWNPROCESS

    ctypedef void (__stdcall *WINEVENTPROC)(
        HWINEVENTHOOK hWinEventHook,
        DWORD event,
        HWND hwnd,
        LONG idObject,
        LONG idChild,
        DWORD dwEventThread,
        DWORD dwmsEventTime
    )

    HWINEVENTHOOK SetWinEventHook(
        DWORD eventMin,
        DWORD eventMax,
        HMODULE hmodWinEventProc,
        WINEVENTPROC pfnWinEventProc,
        DWORD idProcess,
        DWORD idThread,
        DWORD dwFlags
    )

    BOOL UnhookWinEvent(HWINEVENTHOOK hWinEventHook)

    HWND GetForegroundWindow()
    BOOL GetWindowThreadProcessId(HWND hwnd, DWORD * lpdwProcessId)
    int GetWindowTextW(HWND hWnd, LPWCHAR lpString, int nMaxCount)

    ctypedef struct POINT:
        LONG x
        LONG y

    ctypedef struct MSG:
        HWND hwnd
        UINT message
        WPARAM wParam
        LPARAM lParam
        DWORD time
        POINT pt

    BOOL GetMessageW(MSG* lpMsg, HWND hWnd, UINT wMsgFilterMin, UINT wMsgFilterMax)
    BOOL TranslateMessage(const MSG* lpMsg)
    LRESULT DispatchMessageW(const MSG* lpMsg)
    BOOL PostQuitMessage(int nExitCode)
    cdef HRESULT CoInitialize(void *pvReserved)
    cdef void CoUninitialize()

# cdef extern from "queue":
#     cdef class Queue
#
# cdef extern from "threading":
#     cdef class Thread
#     cdef class Lock

# cdef struct WindowEvent:
#     HWND hwnd
#     DWORD pid
#     str title

cdef class WindowEvent:
    cdef intptr_t hwnd
    cdef DWORD pid
    cdef str title

    def __init__(self, intptr_t hwnd, DWORD pid, str title):
        self.hwnd: intptr_t = hwnd
        self.pid: DWORD = pid
        self.title: str = title


# It is not possible to pass a callback parameter to SetWinEventHook().
# As a work-around, we associate those data with the hWinEventHook
# that was returned by SetWinEventHook(). As event are only dispatched
# by the Windows message loop, it is guaranteed to be initialized.
cdef PyThread_type_lock listeners_lock
cdef dict listeners_by_hook = {}

cdef LRESULT win_event_proc(HWINEVENTHOOK hWinEventHook, DWORD event, HWND hwnd,
                            LONG idObject, LONG idChild, DWORD dwEventThread, DWORD dwmsEventTime):
    print('In win_event_proc')

    # Get process id
    cdef DWORD pid
    GetWindowThreadProcessId(hwnd, &pid)

    # Get the window title
    cdef WCHAR title[512]
    title[0] = 0    # Makes sure we have empty string in case of error
    GetWindowTextW(hwnd, title, <int>(sizeof(title)//sizeof(WCHAR)))
    title[sizeof(title)//sizeof(WCHAR)-1] = 0    # Makes sure it is zero terminated

    # Create a WindowEvent object with hwnd, pid, and title
    cdef WindowEvent event_data = WindowEvent(hwnd = <intptr_t>hwnd, pid=pid, title=title)
    # event_data.hwnd = hwnd
    # event_data.pid = pid
    # event_data.title = title

    cdef WindowFocusListener listener
    PyThread_acquire_lock(listeners_lock, WAIT_LOCK)
    try:
        listener = listeners_by_hook.get(<intptr_t>hWinEventHook)
    finally:
        PyThread_release_lock(listeners_lock)

    if listener:
        listener.event_queue.put(event_data)
    return 0


cdef class WindowFocusListener:
    cdef object event_queue
    cdef WINEVENTPROC win_event_proc_ptr
    cdef HWINEVENTHOOK hook

    def __init__(self, object event_queue: Queue):
        self.event_queue : Queue = event_queue
        self.hook = NULL
        self.win_event_proc_ptr = <WINEVENTPROC> win_event_proc

        CoInitialize(NULL)

    def start(self):
        self.hook = SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND,
            NULL, # WINEVENT_OUTOFCONTEXT + NULL => callback func in same Cython extension
            self.win_event_proc_ptr,
            0, 0, WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS
        )
        print('SetWinEventHook called')

        # Store the WindowFocusListener instance in the dict
        PyThread_acquire_lock(listeners_lock, WAIT_LOCK)
        try:
            listeners_by_hook[<intptr_t>self.hook] = self
        finally:
            PyThread_release_lock(listeners_lock)
        print('listeners_by_hook populated')

    def run(self):
        """
        Runs the message loop in the current thread until self.stop() is called.
        """
        cdef MSG msg
        # GetMessageW() returns 0 on WM_QUIT
        while GetMessageW(&msg, NULL, 0, 0) != 0:
            TranslateMessage(&msg)
            DispatchMessageW(&msg)

    def stop(self):
        if self.hook:
            UnhookWinEvent(self.hook)

            PyThread_acquire_lock(listeners_lock, WAIT_LOCK)
            try:
                del listeners_by_hook[<intptr_t>self.hook]
            finally:
                PyThread_release_lock(listeners_lock)

            PostQuitMessage(0)
        CoUninitialize()
