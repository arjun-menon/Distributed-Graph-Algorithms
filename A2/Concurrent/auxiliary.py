
import random

def random_distribution(total_requests, num_threads):
    """
    Return a list with a random distribution of
    requests per thread. For returned list L and
    thread index i, L[i] represents the number
    of requests (randomly assigned) to thread i.
    """
    
    requests_per_thread = [0] * num_threads

    while total_requests > 0:
        for i in range(num_threads):
            if random.choice( (True, False) ):
                requests_per_thread[i] += 1
                total_requests -=  1
    return requests_per_thread

def await(func):
    while not func():
        pass

def default_task():
    """ Compute primes up to a specified value """
    
    def primes(n):
        # http://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/3035188#3035188
        """ Returns  a list of primes < n """
        sieve = [True] * n
        for i in range(3,int(n**0.5)+1,2):
            if sieve[i]:
                sieve[i*i::2*i]=[False]* int((n-i*i-1)/(2*i)+1)
        return [2] + [i for i in range(3,n,2) if sieve[i]]    
        
    # change this to a lower value to speed things up:     
    primes(185 * 1000)
