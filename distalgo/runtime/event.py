class EventPattern:
    """ Describes an event "pattern" that can be used to match against Event
    instances.
    """
    def __init__(self, etype, mtype, consts, var, handlers=[]):
        self.etype = etype       # Event type
        self.mtype = mtype       # Message type 
        self.consts = consts     # Constants in pattern
        self.var = var           # Variables in pattern
        self.handlers = handlers # Handlers for this kind of events

    def match(self, event):
        if (not ((self.etype == event.etype) and
                 (self.mtype == event.mtype))):
            return False

        for (index, value) in self.consts:
            if (index >= len(event.data) or 
                event.data[index] != value):
                return False
        for (index, name) in self.var:
            if (index >= len(event.data)):
                return False

        return True

class Event:
    """ Describes a single event.

    Instances of Event are created by the backend thread and passed to the
    front end.
    """
    # Event types:
    receive = 0                 # A message was received
    send = 1                    # A message was sent
    user = 2                    # User defined
    peerjoin = 3                # A new peer joined the network
    peerdown = 4                # Connection to a peer is lost

    def __init__(self, etype, source, timestamp, message):
        self.etype = etype
        self.source = source
        self.timestamp = timestamp
        self.mtype = message[0]
        self.data = message
