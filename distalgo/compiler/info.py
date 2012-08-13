from .consts import *
from ast import *

class ClassInfo:
    """ A structure to hold info about classes.
    """
    def __init__(self, name, isp = True):
        self.name = name        # Obvious
        self.isp = isp          # Is this class a process class?
        self.membervars = set() # Set of member variables names
        self.memberfuncs = set() # Set of member function names
        self.labels = set()      # Set of label names
        self.events = []
        self.sent_patterns = []
        self.newstmts = []      # Stmts that need to be added to __init__
        self.newdefs = []      # New func defs that need to be added to the
                                # class

        self.memberfuncs.add(EVENT_PROC_FUNNAME)
        self.membervars.add(EVENT_PATTERN_VARNAME)


    def genSentPatternStmt(self):
        left = Attribute(Name("self", Load()), SENT_PATTERN_VARNAME, Store())
        right = List([p.toNode() for p in self.sent_patterns], Load())
        return Assign([left], right)

    def genEventPatternStmt(self):
        left = Attribute(Name("self", Load()), EVENT_PATTERN_VARNAME, Store())
        right = List([e.toNode() for e in self.events], Load())
        return Assign([left], right)

    def genLabelEventsStmt(self):
        left = Attribute(Name("self", Load()), LABEL_EVENTS_VARNAME, Store())
        right = Dict([Str(l) for l in self.labels],
                     [Attribute(Name("self", Load()), EVENT_PATTERN_VARNAME,
                                Load())
                      for l in self.labels])
        return Assign([left], right)
