
import threading
from auxiliary import *

class Fast(threading.Thread):
    """ Lamport's fast mutual exclusion algorithm """
    
    # These are shared (static class) variables:
    
    threads = None
    thread_count = 0
    req_count = 0
    
    go = False # used to delay run() until all threads have started.
    
    choosing = []
    x, y = 0, 0
    
    def __init__(self, i):
        super().__init__()
        self.i = i
        #print('Constructed Process', i, 'Thread object (%s).' % self.getName())
    
    def cs(self, task = default_task):
        
        print('Process', self.i, 'requesting CS')
        
        def can_i_enter_cs():
            Fast.choosing[self.i] = 1
            Fast.x = self.i
            
            if Fast.y != 0:
                Fast.choosing[self.i] = 0
                
                # await y == 0:
                await(lambda: Fast.y == 0)
                
                return False
            
            Fast.y = self.i
            
            if Fast.x != self.i:
                Fast.choosing[self.i] = 0
                
                # for j:=1..thread_count+1: await b[j] == 0:
                [await(lambda: Fast.choosing[j] == 0) for j in range(1, Fast.thread_count + 1)]
                
                if Fast.y != self.i:
                    # await y == 0:
                    await(lambda: Fast.y == 0)
                    return False
            
            return True
        
        while not can_i_enter_cs():
            pass
        
        print('Process', self.i, 'entering CS')
        
        task()
        
        print('Process', self.i, 'exiting CS')
        
        Fast.y = 0
        Fast.choosing[self.i] = 0
    
    def run(self):
        # wait until all threads have started:
        while not Fast.go:
            pass
        
        # call cs() req_count times:
        for _ in range(Fast.req_count[self.i]):
            self.cs()
    

def setup(threads, req_count):
    Fast.threads = threads
    Fast.thread_count = len(threads)
    Fast.req_count = random_distribution(req_count, Fast.thread_count)
    
    Fast.choosing = [0] * (Fast.thread_count + 1)

def start():
    for thread in Fast.threads:
        thread.start()
    Fast.go = True
