import multiprocessing
import threading
import random
import time
import queue
import sys
import traceback
import os
import logging

if not __name__ == "__main__":
    from .event import *

class Null(object):
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def __getattribute__(self, attr): return self
    def __setattr__(self, attr, value): pass
    def __delattr__(self, attr): pass

RuntimeLog = Null()

class DistProcess(multiprocessing.Process):
    """Base class for DistAlgo processes.
    """

    class Comm(threading.Thread):
        """The background communications thread.

        Creates an event object for each incoming message, and appends the
        event object to the main process' event queue.
        """

        def __init__(self, parent):
            threading.Thread.__init__(self)
            self._parent = parent
            self._log = Null()

        def run(self):
            try:
                for msg in self._parent._recvmesgs():
                    (src, clock, data) = msg
                    e = Event(Event.receive, src, clock, data)
                    self._parent._eventq.put(e)
            except KeyboardInterrupt:
                pass

    def __init__(self, parent, initpipe, channel, log, name=None):
        multiprocessing.Process.__init__(self)

        global RuntimeLog
        RuntimeLog = log

        self._running = False
        self._channel = channel

        self._logical_clock = 0

        self._event_patterns = []
        self._received_q = []
        self._label_events = {}
        self._event_backlog = []
        self._failures = {'send': 0,
                          'receive': 0,
                          'crash': 0}
        self._evtimeout = None

        # Performance counters:
        self._total_units = -1
        self._completed_units = 0
        self._usrtime_st = 0
        self._systime_st = 0
        self._waltime_st = 0

        self._loglevel = False
        self._name = name
        self._log = Null()

        self._parent = parent
        self._initpipe = initpipe
        self._child_procs = []

    def _wait_for_go(self):
        self._initpipe.send(self._id)
        while True:
            act = self._initpipe.recv()

            if act == "start":
                self._running = True
                del self._initpipe
                return
            else:
                inst, args = act
                if inst == "setup":
                    self.setup(*args)
                else:
                    m = getattr(self, "set_" + inst)
                    m(*args)

    def _start_comm_thread(self):
        self._eventq = queue.Queue()
        self._comm = DistProcess.Comm(self)
        self._comm.start()

    def _sighandler(self, signum, frame):
        import os
        import signal
        for cpid, _ in self._child_procs:
            os.kill(cpid, signal.SIGTERM)
        sys.exit(0)

    def run(self):
        global RuntimeLog
        try:
            import signal
            signal.signal(signal.SIGTERM, self._sighandler)

            self._id = self._channel(self._name)
            self._start_comm_thread()
            if not isinstance(RuntimeLog, Null):
                self._log = logging.getLogger(str(self))
                self._log.setLevel(logging.DEBUG)
                formatter = RuntimeLog._formatter

                ch = logging.StreamHandler()
                ch.setLevel(RuntimeLog._consolelvl)
                ch.setFormatter(formatter)
                self._log.addHandler(ch)

                if RuntimeLog._logdir is not None:
                    logfile = os.path.join(RuntimeLog._logdir,
                                           self._id.getlogname())
                    fh = logging.FileHandler(logfile)
                    fh.setLevel(RuntimeLog._filelvl)
                    fh.setFormatter(formatter)
                    self._log.addHandler(fh)

            self._wait_for_go()

            self._usrtime_st, self._systime_st, _, _, _ = os.times()
            self._waltime_st = time.clock()

            self.main()

        except Exception as e:
            sys.stderr.write("Unexpected error at process %s:%r"% (str(self), e))
            traceback.print_tb(e.__traceback__)

        except KeyboardInterrupt as e:
            self._log.debug("Received KeyboardInterrupt, exiting")
            pass

    def exit(self, code):
        raise SystemExit(10)

    def output(self, message, level=logging.INFO):
        self._log.log(level, message)

    def spawn(self, pcls, args):
        """Spawns a child process"""

        childp, ownp = multiprocessing.Pipe()
        p = pcls(self._id, childp)
        p._loglevel = self._loglevel
        p.start()

        childp.close()
        cid = ownp.recv()
        ownp.send(("setup", args))
        ownp.send("start")

        self._child_procs.append((p.pid, cid))

        return cid

    # Wrapper functions for message passing:
    def send(self, data, to):
        if (self._fails('send')):
            return False

        if (hasattr(to, '__iter__')):
            for t in to:
                t.send(data, self._id, self._logical_clock)
        else:
            to.send(data, self._id, self._logical_clock)

        if (self._loglevel):
            self.output("Sent %s -> %r"%(str(data), to))
        self._eventq.put(Event(Event.send, self._id, self._logical_clock,data))
        self._parent.send(('sent', 1), self._id)
        return True

    def _recvmesgs(self):
        for mesg in self._id.recvmesgs():
            if not (self._fails('receive')):
                yield mesg

    # This simulates the controlled "label" mechanism. Currently we simply
    # handle one event on one label call:
    def _label_(self, name, block=False):
        if (name.endswith("start")):
            self._begin_work_unit()
        elif (name.endswith("end")):
            self._end_work_unit()
        if (self._fails('crash')):
            self.output("Stuck in label: %s" % name)
            self.exit(10)
        if not name in self._label_events:
            # Error: invalid label name
            return
        self._process_event(self._label_events[name], block)

    def _fails(self, failtype):
        if not failtype in self._failures.keys():
            return False
        if (random.randint(0, 100) < self._failures[failtype]):
            return True
        return False

    # Retrieves one message, then process the backlog event queue. 'block'
    # indicates whether to block waiting for next message to come in if the
    # queue is currently empty:
    def _process_event(self, patterns, block, timeout = None):
        if timeout != None and timeout < 0: timeout = 0
        try:
            event = self._eventq.get(block, timeout)

            # The following loop does a "prematch" for this new event. If it
            # matches something then we keep it. Otherwise we know there is no
            # handler for this event and thus we simply discard it.
            for p in self._event_patterns:
                if (p.match(event)):
                    self._event_backlog.append(event)
                    break

        except queue.Empty:
            pass
        except Exception as e:
            self._log.debug("Caught exception while waiting for events: %r", e)
            return

        unhandled = []
        for e in self._event_backlog:
            ishandled = False
            for p in patterns:
                if (p.match(e)): # Match and handle
                    # Match success, update logical clock, call handlers
                    self._logical_clock = \
                        max(self._logical_clock, e.timestamp) + 1

                    args = []
                    for (index, name) in p.var:
                        args.append(e.data[index])
                    args.append(e.timestamp)
                    args.append(e.source)
                    for h in p.handlers:
                        h(*args)
                    ishandled = True

            if (not ishandled):
                unhandled.append(e)
        self._event_backlog = unhandled

    def _begin_work_unit(self):
        if (self._completed_units == self._total_units):
            self.output("Reached designated work unit count.")

            import pympler.asizeof
            memusage = pympler.asizeof.asizeof(self) / 1024
            self._parent.send(('mem', memusage), self._id)

            usrtime, systime, _, _, _ = os.times()
            self._parent.send(('totalusrtime',
                                 usrtime - self._usrtime_st), self._id)
            self._parent.send(('totalsystime',
                                 systime - self._systime_st), self._id)
            self._parent.send(('totaltime',
                                 time.clock() - self._waltime_st), self._id)

            self._forever_message_loop()


    def _end_work_unit(self):
        self._completed_units += 1

    def _forever_message_loop(self):
        while (True):
            self._process_event(self._event_patterns, True)

    def _has_received(self, mess):
        try:
            self._received_q.remove(mess)
            return True
        except ValueError:
            return False

    def __str__(self):
        s = self.__class__.__name__
        if self._name is not None:
            s += "(" + self._name + ")"
        else:
            s += str(self._id)
        return s

    def work(self):
        """Waste some random amount of time."""
        time.sleep(random.randint(0, 200) / 100)
        pass

    def logical_clock(self):
        """Returns the current value of Lamport clock."""
        return self._logical_clock

    def incr_logical_clock(self):
        """Increment Lamport clock by 1."""
        self._logical_clock += 1


    ### Various attribute setters:
    def set_loglevel(self, level):
        self._loglevel = level

    def set_send_fail_rate(self, rate):
        self._failures['send'] = rate

    def set_receive_fail_rate(self, rate):
        self._failures['receive'] = rate

    def set_crash_rate(self, rate):
        self._failures['crash'] = rate

    def set_iterations_to_run(self, nunits):
        self._total_units = nunits

    def set_event_timeout(self, time):
        self._evtimeout = time

    def set_name(self, name):
        self._name = name
