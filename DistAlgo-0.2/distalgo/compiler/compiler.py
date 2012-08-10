from ast import *
from .dist import DistalgoTransformer
from .codegen import to_source

def dist_compile(fd):
    distree = parse(fd.read())
    pytree = DistalgoTransformer().visit(distree)

    return pytree

def dist_compile_to_string(fd):
    distree = parse(fd.read())
    pytree = DistalgoTransformer().visit(distree)

    return to_source(pytree)

def dist_compile_to_file(fd, outfd):
    distree = parse(fd.read())
    pytree = DistalgoTransformer().visit(distree)
    source = to_source(pytree)
    outfd.write(source)

    return pytree

