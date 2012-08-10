import multiprocessing, threading, random, time, queue, sys, traceback, os, signal

class DistProcess(multiprocessing.Process):
    class Comm(threading.Thread):
        def __init__(self, parent):
            threading.Thread.__init__(self)
            self._parent = parent

        def run(self):
            try:
                while True:
                    msg = self._parent.receive()
                    (src, clock, data) = msg
                    e = Event(Event.receive, src, clock, data)
                    self._parent._eventq.put(e)
            except KeyboardInterrupt:
                pass

    def __init__(self, parent, initpipe):
        multiprocessing.Process.__init__(self)
        self._running = False
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
        self._current_units = 0

        self._trace = False

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
                m = getattr(self, inst)
                m(*args)

    def _start_comm_thread(self):
        self._eventq = queue.Queue()
        self._comm = DistProcess.Comm(self)
        self._comm.start()

    def run(self):
        try:
            self._id = EndPoint()
            self._start_comm_thread()
            self._wait_for_go()

            self._totusrtime_start, self._totsystime_start, _, _, _ = os.times()
            self._tottime_start = time.clock()
            self.main()
        except Exception as e:
            print("Unexpected error at process %s:%r"% (str(self), e))
            traceback.print_tb(e.__traceback__)
        except KeyboardInterrupt as e:
            pass
        self.output("Exiting.")

    def exit(self, code):
        raise SystemExit(code)

    def output(self, message):
        print("%s[%s]: %s"%(self.__class__.__name__, str(self._id), message))

    def spawn(self, pcls, args):
        childp, ownp = multiprocessing.Pipe()
        p = pcls(self._id, childp)
        p._trace = self._trace
        p.start()
        childp.close()
        cid = ownp.recv()
        ownp.send(("setup", args))
        ownp.send("start")
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

        if (self._trace):
            self.output("Sent %s -> %r"%(str(data), to))
        self._eventq.put(Event(Event.send, self._id, self._logical_clock,data))
        self._parent.send(('sent', 1), self._id)
        return True

    def receive(self):
        while (self._fails('receive')):
            self._id.recv(True) # This only makes sense for blocking recvs
        return self._id.recv(True)

    # This simulates the controlled "label" mechanism. Currently we simply
    # handle one event on one label call:
    def _label_(self, name, block=False):
        if (name.endswith("start")):
            self._begin_work_unit()
        elif (name.endswith("end")):
            self._end_work_unit()
        if (self._fails('crash')):
            self.output("Stuck in label: %s" % name)
            exit(10)
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
    def _process_event(self, patterns, block):
        try:
            event = self._eventq.get(block, self._evtimeout)

            # The following loop does a "prematch" for this new event. If it
            # matches something then we keep it. Otherwise we know there is no
            # handler for this event and thus we simply discard it.
            for p in self._event_patterns:
                if (p.match(event)):
                    self._event_backlog.append(event)
                    break

        except queue.Empty:
            pass

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
        if (self._current_units == self._total_units):
            self.output("Reached designated work unit count.")
            usrtime, systime, _, _, _ = os.times()
            self._parent.send(('totalusrtime',
                                 usrtime - self._totusrtime_start), self._id)
            self._parent.send(('totalsystime',
                                 systime - self._totsystime_start), self._id)
            self._parent.send(('totaltime',
                                 time.clock() - self._tottime_start), self._id)
            self._forever_message_loop()

        self._time_unit_start = (os.times(), time.clock())

    def _end_work_unit(self):
        usrtime_end, systime_end, _, _ ,_ = os.times()
        tottime_end = time.clock()
        ((usrtime_start, systime_start, _, _, _), tottime_start) = \
            self._time_unit_start

        self._current_units += 1
        self._parent.send(('unitsdone', 1), self._id)
        self._parent.send(('usertime',
                             usrtime_end - usrtime_start), self._id)
        self._parent.send(('systemtime',
                             systime_end - systime_start), self._id)
        self._parent.send(('elapsedtime',
                             tottime_end - tottime_start), self._id)

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
        return self.__class__.__name__ + str(self._id)

    def set_trace(self, trace):
        self._trace = trace

    def set_failure_rate(self, failtype, rate):
        self._failures[failtype] = rate

    def set_total_units_to_run(self, nunits):
        self._total_units = nunits

    def set_event_timeout(self, time):
        self._evtimeout = time

    # Simulate work, waste some random amount of time:
    def work(self):
        time.sleep(random.randint(1, 3))
        pass

    def logical_clock(self):
        return self._logical_clock

    def incr_logical_clock(self):
        self._logical_clock += 1
