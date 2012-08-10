from ast import *
from .exceptions import InvalidSendException
from .consts import SENDMSG_FUNNAME

class SendTransformer(NodeTransformer):
    """Translates 'send' arguments into Tuples.
    """

    def __init__(self, info):
        self.info = info

    def visit_Expr(self, node):
        if (not (isinstance(node.value, Call) and 
                 isinstance(node.value.func, Name) and
                 (node.value.func.id == SENDMSG_FUNNAME))):
            return node

        if (len(node.value.args) != 2):
            raise InvalidSendException()

        if (not isinstance(node.value.args[0], Call)):
            return node

        messCall = node.value.args[0]
        messTuple = Tuple([Str(messCall.func.id)] + messCall.args, Load())
        node.value.args[0] = messTuple
        return node
