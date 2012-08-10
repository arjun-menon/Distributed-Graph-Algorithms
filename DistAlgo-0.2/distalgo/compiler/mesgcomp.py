from ast import *
from .event import EventObject
from .exceptions import InvalidReceivedException, InvalidSentException
from .consts import LOGICAL_TIMESTAMP_VARNAME, MSG_SRCNODE_VARNAME, RECEIVED_FUNNAME, SENT_FUNNAME

class SentReceivedTransformer(NodeTransformer):
    """Transforms 'sent' and 'received' statements.
    """

    def __init__(self, info):
        self.info = info
        self.addAllNames  = False
        self.vars = set(self.info.membervars) # This collects the 'bound'
                                              # vars. Anything not in this set
                                              # is considered 'free'.

    def visit_FunctionDef(self, node):
        self.vars = set(self.info.membervars)
        return self.generic_visit(node)

    def visit_Event(self, node):
        self.vars = set(self.info.membervars)
        self.addAllNames = True
        self.visit(node.arg)
        self.addAllNames = False
        return self.generic_visit(node)

    def visit_arg(self, node):
        self.vars.add(node.arg)
        return node

    def visit_Name(self, node):
        if (type(node.ctx) == Store or type(node.ctx) == AugStore or self.addAllNames):
            self.vars.add(node.id)
        return self.generic_visit(node)

    # We need to alter the order of child nodes when visiting GeneratorExps:
    def visit_GeneratorExp(self, node):
        node.generators = [self.visit(c) for c in node.generators]
        node.elt = self.visit(node.elt)
        return node

    visit_ListComp = visit_GeneratorExp
    visit_SetComp = visit_GeneratorExp
    visit_DictComp = visit_GeneratorExp

    def visit_comprehension(self, node):
        node.iter = self.visit(node.iter)
        node.target = self.visit(node.target)
        node.ifs = [self.visit(i) for i in node.ifs]
        return node


    def visit_Call(self, node):
        if (isinstance(node.func, Name) and node.func.id == RECEIVED_FUNNAME):
            if (len(node.args) != 1 or (not isinstance(node.args[0], Call))):
                raise InvalidReceivedException()
            etype = "receive"
            mtype = node.args[0].func.id
            return self._visit_call_main(EventObject(
                    etype, mtype, Tuple(node.args[0].args, Load())))

        elif (isinstance(node.func, Name) and node.func.id == SENT_FUNNAME):
            if (len(node.args) != 1 or (not isinstance(node.args[0], Call))):
                raise InvalidSentException()
            etype = "send"
            mtype = node.args[0].func.id
            return self._visit_call_main(EventObject(
                    etype, mtype, Tuple(node.args[0].args, Load())))

        else:
            return self.generic_visit(node)

    def _visit_call_main(self, event):
        bound = [v for (i, v) in event.vars if v in self.vars]
        free = [v for (i, v) in event.vars if not v in self.vars]

        same = self.find_same_event(event)
        if (same == None):
            event.hname = self.genHandlerName(event)
            event.pname = self.genPredicateName(event)
            event.vname = self.genVarName(event)
            self.info.events.append(event)
            self.info.memberfuncs.add(event.hname)
            self.info.memberfuncs.add(event.pname)
            self.info.membervars.add(event.vname)

            self.info.newdefs.append(self.genHandlerFuncDef(event.hname,
                                                            event.vname,
                                                            event.vars))
            self.info.newdefs.append(self.genPredicateFuncDef(event.pname,
                                                              event.vname,
                                                              event.vars,
                                                              bound, free))
            self.info.newstmts.append(self.genVarAssign(event.vname))
            event.pred_funcs.append((bound, free, event.pname))
            return self.genFunCall(event.pname, bound)

        else:
            for (b, f, p) in same.pred_funcs:
                if (bound == b):
                    return self.genFunCall(p, bound)

            pname = same.pname + str(len(same.pred_funcs))
            self.info.newdefs.append(self.genPredicateFuncDef(pname,
                                                              same.vname,
                                                              event.vars,
                                                              bound, free))
            same.pred_funcs.append((bound, free, pname))
            self.info.memberfuncs.add(pname)
            return self.genFunCall(pname, bound)

    def genFunCall(self, name, args):
        return Call(Name(name, Load()),
                    [Name(a, Load()) for a in args], [], None, None)

    def genVarAssign(self, vname):
        return Assign([Attribute(Name("self", Load()), vname, Store())],
                      Call(Name("list", Load()), [], [], None, None))

    def genHandlerFuncDef(self, name, vname, vlist):
        arglist = [arg("_"+v, None) for (i, v) in vlist]
        arglist.append(arg(LOGICAL_TIMESTAMP_VARNAME, None))
        arglist.append(arg(MSG_SRCNODE_VARNAME, None))
        args = arguments(arglist, None, None, [], None, None, [], None)
        m = Attribute(Name(vname, Load()), "append", Load())
        if (len(vlist) > 0):
            a = Tuple([Name("_"+v, Load()) for (i, v) in vlist], Load())
        else:
            a = Name("True", Load())
        exp = Call(m, [a], [], None, None)
        return FunctionDef(name, args, [Expr(exp)], [], None)

    def genPredicateFuncDef(self, name, vname, vlist, bound, free):
        arglist = [arg(v, None) for v in bound]
        args = arguments(arglist, None, None, [], None, None, [], None)

        if (len(free) == 0):    # No free variables
            elt = Name("True", Load())
        elif(len(free) == 1):
            elt = Name(free[0]+"_", Load())
        else:
            elt = Tuple([Name(n+"_", Load()) for n in free], Load())

        if (len(vlist) > 0):
            target = Tuple([Name(v+"_", Store()) for (i, v) in vlist], Store())
        else:
            target = Name("v_", Load())
        iterator = Name(vname, Load())
        ifs = [Compare(Name(v+"_", Load()), [Eq()], [Name(v, Load())])
               for v in bound]

        listnode = ListComp(elt, [comprehension(target, iterator, ifs)])
        retstmt = Return(listnode)

        return FunctionDef(name, args, [retstmt], [] , None)

    def find_same_event(self, ev):
        for t in self.info.events:
            if (t.matches(ev)):
                return t
        return None

    HANDLER_PREFIX = "_received_handler_"
    PREDICATE_PREFIX = "_has_received_"
    VAR_PREFIX = "_received_messages_"

    def genHandlerName(self, event):
        return (("_%s_handler_%d") % (event.evttype, len(self.info.events)))

    def genPredicateName(self, event):
        return (("_has_%s_%d") % (event.evttype, len(self.info.events)))

    def genVarName(self, event):
        return (("_%s_messages_%d") % (event.evttype, len(self.info.events)))
