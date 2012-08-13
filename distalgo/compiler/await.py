from .consts import *
from .exceptions import InvalidAwaitException

from ast import *

class AwaitTransformer(NodeTransformer):
    """Translates 'await' statements.
    """

    def __init__(self, info):
        NodeTransformer.__init__(self)
        self.counter = 0

    def visit_Expr(self, node):
        if (not (isinstance(node.value, Call) and 
                 isinstance(node.value.func, Name) and
                 node.value.func.id == "await")):
            return node

        self.counter += 1
        timerVar = TIMER_VARNAME + str(self.counter)

        # We only deal with one await cond (plus timeout) for now:
        if (len(node.value.args) > 2):
            raise InvalidAwaitException()

        body = []
        # Invert the await condition
        op = node.value.args[0]
        cond = UnaryOp(Not(), op)

        # _process_event_(_event_patterns, True, timeleft)
        whilebody = [Expr(Call(Name(EVENT_PROC_FUNNAME, Load()),
                               [Name(EVENT_PATTERN_VARNAME, Load()),
                                Name("True", Load()),
                                Name(TIMELEFT_VARNAME, Load()) if len(node.value.args) > 1 else Name("None", Load())],
                               [], None, None))]

        if (len(node.value.args) > 1):
            # __await_timer_N = time.time()
            timerdef = Assign([Name(timerVar, Store())],
                              Call(Attribute(Name("time", Load()),
                                             "time", Load()),
                                   [], [], None, None))

            # timeleft = TIMEOUT
            timeleftdef = Assign([Name(TIMELEFT_VARNAME, Store())],
                                 node.value.args[1])

            # _timeout = False
            timeoutdef = Assign([Name(TIMEOUT_VARNAME, Store())],
                                Name("False", Load()))

            body.append(timerdef)
            body.append(timeleftdef)
            body.append(timeoutdef)
            
            # timeleft = TIMEOUT - (time.time() - __await_timer_N)
            whilebody.extend(
                [Assign([Name(TEMP_VARNAME, Store())],
                        Call(Attribute(Name("time", Load()), "time", Load()),
                             [], [], None, None)),
                 AugAssign(Name(TIMELEFT_VARNAME, Store()), Sub(),
                           Expr(BinOp(Name(TEMP_VARNAME, Load()), Sub(),
                                      Name(timerVar, Load())))),
                 Assign([Name(timerVar, Store())], Name(TEMP_VARNAME, Load()))])

            breakcond = Compare(Name(TIMELEFT_VARNAME, Load()),
                                [Lt()], [Num(0)])
            breakbody = [Assign([Name(TIMEOUT_VARNAME, Store())],
                                Name("True", Load())),
                         Break()]
            whilebody.append(If(breakcond, breakbody, []))

        whilestmt = While(cond, whilebody, [])
        body.append(whilestmt)

        # TODO: clean up message queue here??
        # rsf = AwaitTransformer.RecvStmtFinder()
        # rsf.visit(node)
        # if (len(rsf.recvs) > 0):
        #     cleanup = [Assign([Name(v, Load())],
        #                       Call(Name("set", Load()), [], [], None, None))
        #                for v in rsf.recvs]
        #     body.extend(cleanup)

        return body
