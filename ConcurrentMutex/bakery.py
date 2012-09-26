
import threading
from auxiliary import *

class Bakery(threading.Thread):
    """ Lamport's bakery algorithm """
    
    # These are shared (static class) variables:
    
    threads = None
    thread_count = 0
    req_count = 0
    
    go = False # used to delay run() until all threads have started.
    
    choosing = []
    num = []
    
    x, y = 0, 0
    
    def __init__(self, i):
        super().__init__()
        self.i = i
        #print('Constructed Process', i, 'Thread object (%s).' % self.getName())
       
    def cs(self, task = default_task):
        
        print('Process', self.i, 'requesting CS')
        
        Bakery.choosing[self.i] = 1
        
        Bakery.num[self.i] = 1 + max(Bakery.num)
        
        Bakery.choosing[self.i] = 0
        
        for j in range(1, Bakery.thread_count + 1):
            # await choosing[j] == 0
            await(lambda: Bakery.choosing[j] == 0)
            
            # await num[j] == 0 or (num[j],j) >= (num[i],i)
            await( lambda: Bakery.num[j] == 0 or (Bakery.num[j], j) >= (Bakery.num[self.i], self.i) )
        
        print('Process', self.i, 'entering CS')
        
        task()
        
        print('Process', self.i, 'exiting CS')
        
        Bakery.num[self.i] = 0
    
    def run(self):
        # wait until all threads have started:
        while not Bakery.go:
            pass
        
        # call cs() req_count times:
        for _ in range(Bakery.req_count[self.i]):
            self.cs()
    

def setup(threads, req_count):
    Bakery.threads = threads
    Bakery.thread_count = len(threads)
    Bakery.req_count = random_distribution(req_count, Bakery.thread_count)
    
    Bakery.choosing = [0] * (Bakery.thread_count + 1)
    Bakery.num      = [0] * (Bakery.thread_count + 1)

def start():
    for thread in Bakery.threads:
        thread.start()
    Bakery.go = True
