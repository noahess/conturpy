# Hypersonic Nozzle Design (Sivells' CONTUR)
Some scripts for a full design space search of low hypersonic nozzles. Largely relies on Sivells' CONTUR code ported to 
modern Fortran by F.-L. Zavalan [here](https://github.com/aldorona/contur).

S. Schneider notes in [NASA CR 197286](https://ntrs.nasa.gov/api/citations/19950015019/downloads/19950015019.pdf) that 
Sivells' code does not produce streamlines when ETAD is not 60. The fix is not implemented but under investigation for 
this repository.