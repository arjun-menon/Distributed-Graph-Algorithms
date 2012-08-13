import ast
from ast import *
from .exceptions import InvalidLabelException

LABEL_FUNC = "_label_"


# This class generates unique names for all labels, aggregates all the label
# names, and at the same time transforms the labels into function calls
class LabelTransformer(NodeTransformer):
    """ Generate unique names for all labels in class scope. Flattens Label
    blocks and insert self._label_ function calls. Aggregates all label names
    into a set.
    """

    def __init__(self, info):
        self.info = info
        self.hasLabelAst = hasattr(ast, "Label")
        info.memberfuncs.add(LABEL_FUNC)

    def insert_labels(self, body):
        new_body = []
        for stmt in body:
            if isinstance(stmt, Expr):
                if (isinstance(stmt.value, UnaryOp) and
                    isinstance(stmt.value.op, USub) and
                    isinstance(stmt.value.operand, UnaryOp) and
                    isinstance(stmt.value.operand.op, USub) and
                    isinstance(stmt.value.operand.operand, Name)):

                    fullname = stmt.value.operand.operand.id
                    self.info.labels.add(fullname)
                    stmt = self.genLabelCall(stmt, fullname)
            new_body.append(stmt)
        return new_body

    def visit_Block(self, node):
        new_node = self.generic_visit(node)
        if not self.hasLabelAst:
            new_node.body = self.insert_labels(new_node.body)
            if hasattr(new_node, "orelse"):
                new_node.orelse = self.insert_labels(new_node.orelse)
        return new_node

    visit_FunctionDef = visit_Block
    visit_For = visit_Block
    visit_If = visit_Block
    visit_While = visit_Block
    visit_With = visit_Block
    visit_TryExcept = visit_Block
    visit_TryFinally = visit_Block

    def visit_Label(self, node):
        fullname = node.name
        self.info.labels.add(fullname)

        new_node = self.generic_visit(node)
        labelcall = self.genLabelCall(node, fullname)
        new_node.body.insert(0, labelcall)
        return new_node.body

    def genLabelCall(self, node, fullname):
        return copy_location(Call(Name(LABEL_FUNC, Load()),
                                  [Str(fullname)], [], None, None), node)


