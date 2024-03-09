# rebound-simulations

This repository contains the simulations made with rebound for my project at IRF. 

# Dependencies & setup instructions

The rebound library is required for the simulations, its C version can be found at: https://github.com/hannorein/rebound. Once cloned, typing 'make' in a terminal within the 'src' folder will compile the shared library. On linux, the library can then be added to the path by editing the ~/.bashrc file. THe line to be added is 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/path/to/rebound/src'.

# Compile and run instructions

The simulations can be compiled with the following command: gcc simulation.c -o simulation -lrebound -I/home/path/to/rebound/src -L/home/path/to/rebound/src -lm 

The math library is necessary for the compilation.
