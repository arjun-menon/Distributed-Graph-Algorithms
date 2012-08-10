import multiprocessing
import time
import sys
import types
import traceback
import os
import stat
import signal
import time
import logging
import threading
import warnings

if not __name__ == "__main__":
    from .udp import UdpEndPoint
    from .tcp import TcpEndPoint
    from .sim import DistProcess
    from .event import *

class Null(object):
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def __getattribute__(self, attr): return self
    def __setattr__(self, attr, value): pass
    def __delattr__(self, attr): pass

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc

PerformanceCounters = {}
CounterLock = threading.Lock()
RootProcess = None
RootLock = threading.Lock()
EndPointType = UdpEndPoint
PrintProcStats = False
TotalUnits = None
ProcessIds = []
Log = logging.getLogger("runtime")

def dist_source(dir, filename):
    if not filename.endswith(".dis"):
        die("DistAlgo source file should end with '.dis'")

    purename = filename[:-4]
    distsource = filename
    pysource = purename + ".py"

    eval_source(os.path.join(dir, distsource),
                os.path.join(dir, pysource))

def eval_source(distsrc, pysrc):
    from ..compiler import dist_compile_to_file

    distmode, pymode, codeobj = None, None, None
    try:
        distmode = os.stat(distsrc)
    except OSError:
        die("DistAlgo source not found.")

    try:
        pymode = os.stat(pysrc)
    except OSError:
        pymode = None

    if pymode == None or pymode[stat.ST_MTIME] < distmode[stat.ST_MTIME]:
        distfd = open(distsrc, 'r')
        pyfd = open(pysrc, 'w+')
        dist_compile_to_file(distfd, pyfd)
        distfd.close()
        pyfd.close()

    pyfd = open(pysrc, 'r')
    code = compile(''.join(pyfd.readlines()), pysrc, 'exec')
    exec(code, globals())
    pyfd.close()


def maximum(iterable):
    if (len(iterable) == 0): return -1
    else: return max(iterable)

def use_channel(endpoint):
    if RootProcess is not None:
        Log.error("Can not change channel type after creating child processes.")
        return

    global EndPointType
    if endpoint == "udp":
        EndPointType = UdpEndPoint
    elif endpoint == "tcp":
        EndPointType = TcpEndPoint
    else:
        Log.error("Unknown channel type %s", endpoint)

def get_channel_type():
    return EndPointType

def create_root_logger(options, logfile, logdir):
    global Log

    if not options.nolog:
        Log.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(asctime)s]%(name)s:%(levelname)s: %(message)s')
        Log._formatter = formatter

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)

        try:
            ch.setLevel(options.logconsolelevel)
            Log._consolelvl = options.logconsolelevel
        except ValueError:
            sys.stderr.write("Unknown logging level %s. Defaulting to INFO.\n" %
                             options.loglevel)
            ch.setLevel(logging.INFO)
            Log._consolelvl = logging.INFO

        fh = logging.FileHandler(logfile)
        fh.setFormatter(formatter)

        try:
            fh.setLevel(options.logfilelevel)
            Log._filelvl = options.logfilelevel
        except ValueError:
            sys.stderr.write("Unknown logging level %s. Defaulting to INFO.\n" %
                             options.loglevel)
            fh.setLevel(logging.INFO)
            Log._filelvl = logging.INFO

        if logdir is not None:
            os.makedirs(logdir, exist_ok=True)
            Log._logdir = logdir
        else:
            Log._logdir = None

        Log.addHandler(fh)
        Log.addHandler(ch)

    else:
        Log = Null()

def entrypoint(options, args, cmdl):
    target = args[0]
    source_dir = os.path.dirname(target)
    purename = os.path.basename(target)[:-4]

    if not os.access(target, os.R_OK):
        die("Can not access source file %s" % target)

    create_root_logger(options,
                       os.path.join(source_dir, purename + ".log"),
                       os.path.join(source_dir, options.logdir)
                       if options.logdir is not None else None)

    if target.endswith(".dis"):
        dist_source(source_dir, os.path.basename(target))
    elif target.endswith(".py") or target.endswith(".run"):
        targetfd = open(target, "r")
        exec(targetfd.read(), globals())
        targetfd.close()
    else:
        die("No DistAlgo source specified.")

    sys.argv = cmdl

    # Start the background statistics thread:
    RootLock.acquire()
    stat_th = threading.Thread(target=collect_statistics,
                               name="Stat Thread")
    stat_th.daemon = True
    stat_th.start()

    # Start main program
    if 'main' in globals() and isinstance(main, types.FunctionType):

        try:
            main()

        except KeyboardInterrupt as e:
            Log.info("Received keyboard interrupt.")
        except Exception as e:
            err_info = sys.exc_info()
            Log.error("Caught unexpected global exception: %r", e)
            traceback.print_tb(err_info[2])

    else:
        die("'main' function not defined!")

    perffd = None
    if options.perffile is not None:
        perffd = open(options.perffile, "w")

    dumpfd = None
    if options.dumpfile is not None:
        dumpfd = open(options.dumpfile, "wb")

    log_performance_statistics()

    if perffd is not None:
        print_simple_statistics(perffd)
        perffd.close()

    if dumpfd is not None:
        store_statistics(dumpfd)
        dumpfd.close()

    global ProcessIds
    for pid in ProcessIds:      # Make sure we kill all sub procs
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass

    Log.info("Terminating...")


def createprocs(pcls, power, args=None):
    if not issubclass(pcls, DistProcess):
        Log.error("Can not create non-DistProcess.")
        return set()

    global RootProcess
    if RootProcess is None:
        if type(EndPointType) == type:
            RootProcess = EndPointType()
            RootLock.release()
        else:
            Log.error("EndPoint not defined")
            return
    Log.debug("RootProcess is %s" % str(RootProcess))

    Log.info("Creating instances of %s..", pcls.__name__)
    pipes = []
    iterator = []
    if isinstance(power, int):
        iterator = range(power)
    elif isinstance(power, set):
        iterator = power
    else:
        Log.error("Unrecognised parameter %r", n)
        return set()

    procs = set()
    for i in iterator:
        (childp, ownp) = multiprocessing.Pipe()
        p = pcls(RootProcess, childp, EndPointType, Log)
        if isinstance(i, str):
            p.set_name(i)
        pipes.append((i, childp, ownp, p))      # Buffer the pipe
        p.start()               # We need to start proc right away to obtain
                                # EndPoint and pid for p
        ProcessIds.append(p.pid)
        procs.add(p)

    Log.info("%d instances of %s created.", len(procs), pcls.__name__)
    result = dict()
    for i, childp, ownp, p in pipes:
        childp.close()
        cid = ownp.recv()
        cid._initpipe = ownp    # Tuck the pipe here
        cid._proc = p           # Set the process object
        result[i] = cid

    if (args != None):
        setupprocs(result, args)

    if isinstance(power, int):
        return set(result.values())
    else:
        return result

@deprecated
def createnamedprocs(pcls, names, args=None):
    if not issubclass(pcls, DistProcess):
        Log.error("Can not create non-DistProcess.")
        return set()

    global RootProcess
    if RootProcess == None:
        if type(EndPointType) == type:
            RootProcess = EndPointType()
            RootLock.release()
        else:
            sys.stderr.write("Error: EndPoint not defined.\n")
    Log.debug("RootProcess is %s" % str(RootProcess))

    Log.info("Creating procs %s.." % pcls.__name__)
    pipes = []
    for n in names:
        (childp, ownp) = multiprocessing.Pipe()
        p = pcls(RootProcess, childp, EndPointType, Log)
        p.set_name(n)
        pipes.append((n, childp, ownp))      # Buffer the pipe
        p.start()               # We need to start proc right away to obtain
                                # EndPoint and pid for p
        ProcessIds.append(p.pid)

    Log.info("%d instances of %s created."%(len(names), pcls.__name__))
    result = dict()
    for name, childp, ownp in pipes:
        childp.close()
        cid = ownp.recv()
        cid._initpipe = ownp    # Tuck the pipe here
        result[name] = cid
    if (args != None):
        setupprocs(result.values(), args)

    return result

def setupprocs(pids, args):
    if isinstance(pids, dict):
        pset = pids.values()
    else:
        pset = pids

    for p in pset:
        p._initpipe.send(("setup", args))

def startprocs(procs):
    global PerformanceCounters

    if isinstance(procs, dict):
        ps = procs.values()
    else:
        ps = procs

    init_performance_counters(ps)
    Log.info("Starting procs...")
    for p in ps:
        p._initpipe.send("start")
        del p._initpipe

def collect_statistics():
    global PerformanceCounters
    global CounterLock

    completed = 0
    try:
        RootLock.acquire()
        for mesg in RootProcess.recvmesgs():
            src, tstamp, tup = mesg
            event_type, count = tup

            CounterLock.acquire()
            if PerformanceCounters.get(src) is not None:
                if PerformanceCounters[src].get(event_type) is None:
                    PerformanceCounters[src][event_type] = count
                else:
                    PerformanceCounters[src][event_type] += count

                if event_type == 'totaltime':
                    completed += 1
                    if TotalUnits != None and completed == TotalUnits:
                        raise KeyboardInterrupt()

            else:
                Log.debug("Unknown proc: " + str(src))
            CounterLock.release()

    except KeyboardInterrupt:
        pass

    except Exception as e:
        err_info = sys.exc_info()
        Log.debug("Caught unexpected global exception: %r", e)
        traceback.print_tb(err_info[2])

def config_print_individual_proc_stats(p):
    global PrintProcStats
    PrintProcStats = p

def init_performance_counters(procs):
    global PerformanceCounters
    global CounterLock
    for p in procs:
        CounterLock.acquire()
        PerformanceCounters[p] = dict()
        CounterLock.release()

def log_performance_statistics():
    global PerformanceCounters
    global CounterLock

    statstr = "***** Statistics *****\n"
    tot_sent = 0
    tot_usrtime = 0
    tot_systime = 0
    tot_time = 0
    tot_units = 0
    total = dict()

    CounterLock.acquire()
    for proc, data in PerformanceCounters.items():
        for key, val in data.items():
            if total.get(key) is not None:
                total[key] += val
            else:
                total[key] = val

    statstr += ("* Total procs: %d\n" % len(PerformanceCounters))
    CounterLock.release()

    if total.get('totalusrtime') is not None:
        statstr += ("** Total usertime: %f\n" % total['totalusrtime'])
        if TotalUnits is not None:
            statstr += ("*** Average usertime: %f\n" %
                        (total['totalusrtime']/TotalUnits))

    if total.get('totalsystime') is not None:
        statstr += ("** Total systemtime: %f\n" % total['totalsystime'])

    if total.get('totaltime') is not None:
        statstr += ("** Total time: %f\n" % total['totaltime'])
        if TotalUnits is not None:
            statstr += ("*** Average time: %f\n" %
                        (total['totaltime'] / TotalUnits))

    if total.get('mem') is not None:
        statstr += ("** Total memory: %d\n" % total['mem'])
        if TotalUnits is not None:
            statstr += ("*** Average memory: %f\n" % (total['mem'] / TotalUnits))

    Log.info(statstr)

def print_simple_statistics(outfd):
    st = aggregate_statistics()
    statstr = str(st['usrtime']) + '\t' + str(st['time']) + '\t' + str(st['mem'])
    outfd.write(statstr)

def aggregate_statistics():
    global PerformanceCounters
    global CounterLock

    result = {'sent' : 0, 'usrtime': 0, 'systime' : 0, 'time' : 0,
              'units' : 0, 'mem' : 0}

    CounterLock.acquire()
    for key, val in PerformanceCounters.items():
        if val.get('sent') is not None:
            result['sent'] += val['sent']
        if val.get('totalusrtime') is not None:
            result['usrtime'] += val['totalusrtime']
        if val.get('totalsystime') is not None:
            result['systime'] += val['totalsystime']
        if val.get('totaltime') is not None:
            result['time'] += val['totaltime']
        if val.get('mem') is not None:
            result['mem'] += val['mem']
    CounterLock.release()

    if TotalUnits is not None:
        for key, val in result.items():
            result[key] /= TotalUnits

    return result

def store_statistics(fd):
    import pickle

    pickle.dump(aggregate_statistics(), fd)

def config_total_units(num):
    global TotalUnits
    TotalUnits = num

def set_proc_attribute(procs, attr, values):
    if isinstance(procs, dict):
        ps = procs.values()
    else:
        ps = procs

    for p in ps:
        p._initpipe.send((attr, values))

def die(mesg = None):
    if mesg != None:
        sys.stderr.write(mesg + "\n")
    sys.exit(1)
