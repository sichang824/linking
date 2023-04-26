import os
import time
import unicodedata
from venv import logger
from watchdog.observers.fsevents import FSEventsEmitter, BaseObserver, DEFAULT_OBSERVER_TIMEOUT

from constants import MacEventFlags
from log import logger


class CommonEvent:

    def __init__(self, flag, native_event, dst_event, ovr_event):
        self.flag = flag
        self.native_event = native_event
        self.dst_event = dst_event
        self.ovr_event = ovr_event


class SFTPEvent(CommonEvent):
    pass


class MacFSEventsObserver(BaseObserver):

    def __init__(self, timeout=DEFAULT_OBSERVER_TIMEOUT):
        super().__init__(emitter_class=MacFSEventsEmitter, timeout=timeout)

    def schedule(self, event_handler, path, recursive=False):
        # Fix for issue #26: Trace/BPT error when given a unicode path
        # string. https://github.com/gorakhargosh/watchdog/issues#issue/26
        if isinstance(path, str):
            path = unicodedata.normalize("NFC", path)
        return BaseObserver.schedule(self, event_handler, path, recursive)


class MacFSEventsEmitter(FSEventsEmitter):

    def is_exists(self, path):
        try:
            stat = os.stat(path)
        except OSError:
            stat = None
        return stat is not None

    def queue_events(self, timeout, events):

        if time.monotonic() - self._start_time > 60:
            # Event history is no longer needed, let's free some memory.
            self._starting_state = None

        while events:

            event = events.pop(0)
            flags = event.flags

            dst_event = next(
                iter(e for e in events
                     if e.is_renamed and e.inode == event.inode),
                None,
            )

            if dst_event:
                ovr_event = next(
                    iter(e for e in events
                         if e.is_renamed and e.path == dst_event.path
                         and e.inode != event.inode),
                    None,
                )
            else:
                ovr_event = None

            if dst_event: events.remove(dst_event)
            if ovr_event: events.remove(ovr_event)

            for flag in MacEventFlags:
                if (flags & flag.value == flag.value):
                    self.queue_event(
                        SFTPEvent(flag, event, dst_event, ovr_event))
                    break
