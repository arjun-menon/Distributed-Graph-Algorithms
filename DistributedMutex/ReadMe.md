Distributed Mutex (DMX) algorithms
----------------------------------
This is an implementation of two token-based DMX algorithms in DistAlgo: Ricart-Agrawala's token-based algorithm and Suzuki-Kasami's token-based algorithm.

* `RAtoken.dis` contains Ricart-Agrawala's algorithm. For this algorithm, I followed the pseudocode which can be found in the top-level comment in `RAtoken.dis`.

* `SKtoken.dis` contains Suzuki-Kasami's algorithm. For this algorithm, I followed [a description of the algorithm by Mikhail Nesterenko](http://vega.cs.kent.edu/~mikhail/classes/aos.f01/l17tokenDMX.pdf) of Kent State.

Both DistAlgo programs accept a single integer command-line argument specifying the number of processes to start. The default value for this for both is `5`.

You can ignore `lamport.dis`, `mutex2n.dis` and `main.dis`.
