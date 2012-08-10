"""Main entry point"""

import sys,os
import time
if sys.argv[0].endswith("__main__.py"):
    sys.argv[0] = "python -m distalgo"

RUNTIMEPKG = "runtime"
RUNTIMEFILES = ["event.py", "endpoint.py", "udp.py", "tcp.py", "sim.py", "util.py"]

def parseArgs(argv):

    import optparse
    p = optparse.OptionParser()

    p.add_option("-p", action="store_true", dest='printsource')
    p.add_option("-F", action="store_true", dest='genfull')
    p.add_option("--full", action="store_true", dest='genfull')
    p.add_option("-O", action="store_true", dest='optimize')
    p.add_option("-D", action="store", dest='rootdir')
    p.add_option("-o", action="store", dest="outfile")

    p.set_defaults(printsource=False,
                   genfull=False,
                   optimize=False,
                   outfile=None,
                   rootdir=os.getcwd())

    return p.parse_args()


def printUsage(name):
    usage = """
Usage: %s [-p] [-o outfile] <infile>
     where <infile> is the file name of the distalgo source
"""
    sys.stderr.write(usage % name)

from .codegen import to_source
from .compiler import dist_compile

def main():
    opts, args = parseArgs(sys.argv)
    print("rootdir is %s" % opts.rootdir)

    start = time.time()
    runtime = []
    if opts.genfull:
        for f in RUNTIMEFILES:
            p = os.path.join(opts.rootdir, RUNTIMEPKG, f)
            if not os.path.isfile(p):
                sys.stderr.write("File %s not found. Please specify root directory using -D.\n"%p)
                sys.exit(1)
            else:
                pfd = open(p, "r")
                runtime.extend(pfd.readlines())
                pfd.close()
    postamble = ["\nif __name__ == \"__main__\":\n",
                 "    main()\n"]

    for f in args:
        infd = open(f, 'r')
        pytree = dist_compile(infd)
        infd.close()

        pysource = to_source(pytree)

        if opts.printsource:
            sys.stdout.write(pysource)
        else:
            outfile = f[:-4] + ".py"
            outfd = open(outfile, 'w')
            if opts.genfull:
                outfd.writelines(runtime)
            outfd.write(pysource)
            if opts.genfull:
                outfd.writelines(postamble)
            outfd.close()
            sys.stderr.write("Written %s.\n"%outfile)

    elapsed = time.time() - start
    sys.stderr.write("\nTotal compilation time: %f second(s).\n" % elapsed)
    return 0

if __name__ == '__main__':
    main()
