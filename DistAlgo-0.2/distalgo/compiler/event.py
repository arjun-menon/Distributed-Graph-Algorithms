import ast
from ast import *
from .exceptions import InvalidEventException
from .consts import LOGICAL_TIMESTAMP_VARNAME, MSG_SRCNODE_VARNAME

class EventObject:
    """Encapsulates info about events.
    """

    def __init__(self, etype, mtype, node):
        self.evttype = etype
        self.msgtype = mtype

        self.consts = []
        self.vars = []

        self.hname = ""         # Name of handler function
        self.pname = ""         # Name of predicate function
        self.vname = ""         # Name of member variable to store buffered
                                # messages
        self.pred_funcs = []
        self._parse(node)

    def toNode(self):
        cl = []
        vl = []
        for (i, c) in self.consts:
            if (isinstance(c, str)):
                cl.append(Tuple([Num(i), Str(c)], Load()))
            elif (isinstance(c, int) or
                  isinstance(c, float)):
                cl.append(Tuple([Num(i), Num(c)], Load()))
        for (i, v) in self.vars:
            vl.append((Tuple([Num(i), Str(v)], Load())))

        return Call(Name("EventPattern", Load()),
                    [Attribute(Name("Event", Load()), self.evttype, Load()),
                     Str(self.msgtype),
                     List(cl, Load()), List(vl, Load()),
                     List([Attribute(Name("self", Load()), self.hname, Load())],
                          Load())],
                    [], None, None)

    def matches(self, target):
        return (self.evttype == target.evttype and 
                self.msgtype == target.msgtype and
                self.consts == target.consts and
                all(any(i1 == i2 for (i2, n2) in target.vars)
                    for (i1, n1) in self.vars) and
                all(any(i1 == i2 for (i2, n2) in self.vars)
                    for (i1, n1) in target.vars))

    def _parse(self, node):
        if not isinstance(node, Tuple):
            raise InvalidEventException()

        i = 1
        v = []
        c = []

        for thing in node.elts:
            if (isinstance(thing, Name)):
                if (thing.id == "_"):     # Wildcard
                    pass
                else:       # Variable
                    v.append((i, thing.id))
            elif (isinstance(thing, Num)): # Constant
                c.append((i, thing.n))
            elif (isinstance(thing, Str)):
                c.append((i, thing.s))
            else:
                raise InvalidEventException()
            i += 1

        self.consts = c
        self.vars = v


class EventTransformer(NodeTransformer):
    """Transforms event blocks into function defs.
    """

    def __init__(self, info):
        self.info = info
        self.hasEventAst = hasattr(ast, "Event")

#        self.labels = {l: set() for l in labels}

    def visit_Event(self, node):
        etype = "receive"
        mtype = node.name
        name = self.genEventHandlerName()
        event = EventObject(etype, mtype, node.arg)
        event.hname = name
        self.info.events.append(event)
        self.info.memberfuncs.add(name)
        return copy_location(self.genFuncDef(name, event.vars, node.body),
                             node)

    def visit_FunctionDef(self, node):
        if self.hasEventAst:
            return node
        if (not node.name.startswith("On")):
            return node

        msgtype = node.name[2:]
        if len(msgtype) == 0:
            raise InvalidEventException()

        arglist = [Name(arg.arg, Load()) for arg in node.args.args]
        event = EventObject("receive", msgtype, Tuple(arglist, Load()))
        event.hname = self.genEventHandlerName()
        self.info.events.append(event)
        self.info.memberfuncs.add(event.hname)
        return copy_location(self.genFuncDef(event.hname, event.vars,
                                             node.body), node)

    def genFuncDef(self, name, vlist, body):
        arglist = [arg(v, None) for (i, v) in vlist]
        arglist.append(arg(LOGICAL_TIMESTAMP_VARNAME, None))
        arglist.append(arg(MSG_SRCNODE_VARNAME, None))
        args = arguments(arglist, None, None, [], None,
                         None, [], None)
        return FunctionDef(name, args, body, [], None)

    def genEventHandlerName(self):
        return "_event_handler_%d" % len(self.info.events)
