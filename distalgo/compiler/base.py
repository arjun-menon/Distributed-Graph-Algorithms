from .consts import DISTALGO_BASE_CLASSNAME
from ast import *

class InsertSelf(NodeTransformer):
    """ Inserts 'self' quantifier to class member variables and methods, adds
    'self' as first argument to member methods, and transforms 'self' into
    'self._id'. Should be the last step in the entire transformation.
    """
    def __init__(self, info):
        self.info = info
        self.selfName = Name("self", Load())
        self.localargs = set()
        self.isInAttr = False

    def visit_Name(self, node):
        if ((node.id in self.info.membervars or
               node.id in self.info.memberfuncs) and
              ((not node.id in self.localargs) or
               type(node.ctx) == Store)):
            return copy_location(Attribute(self.selfName, node.id, node.ctx),
                                 node)
        if (not self.isInAttr and node.id == "self" and type(node.ctx) == Load):
            return copy_location(Attribute(node, "_id", node.ctx), node)
        else:
            return node

    def visit_Attribute(self, node):
        self.isInAttr = True
        node = self.generic_visit(node)
        self.isInAttr = False
        return node

    def visit_FunctionDef(self, node):
        self.localargs = {a.arg for a in node.args.args}
        node = self.generic_visit(node)
        self.localargs = set()
        if (node.name in self.info.memberfuncs):
            node.args.args.insert(0, arg("self", None))
        return node

class ProcessMembers(NodeTransformer):
    """Extracts process local variable info from the 'setup' method.
    """

    def __init__(self, info):
        self.info = info

    class VarCollector(NodeVisitor):
        def __init__(self):
            self.vars = set()
            self.in_assign = False

        def visit_Name(self, node):
            if (self.in_assign):
                if (type(node.ctx) == Store or type(node.ctx) == AugStore):
                    self.vars.add(node.id)

        def visit_Assign(self, node):
            self.in_assign = True
            for n in node.targets:
                self.visit(n)
            self.in_assign = False

    def visit_FunctionDef(self, node):
        self.info.memberfuncs.add(node.name)
        if (node.name == "setup"):
            argnames = {a.arg for a in node.args.args}
            vc = ProcessMembers.VarCollector()
            vc.visit(node)
            self.info.membervars |= vc.vars
            self.info.membervars |= argnames

            node.body.extend([Assign([Name(n, Store())], Name(n, Load()))
                              for n in argnames])
        return node


class ProcessRun(NodeTransformer):
    def __init__(self):
        self.stmt = Expr(Call
                         (Attribute(Name(DISTALGO_BASE_CLASSNAME, Load()),
                                    "run", Load()),
                          [Name("self", Load())],
                          [], None, None));

    def visit_FunctionDef(self, node):
        if (node.name == "run"):
            node.body.insert(0, self.stmt)
        return node             # We don't recurse down into FunctionDefs

