#!/bin/bash

#SBATCH -N 1
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -J "Produce PSF Grids"
#SBATCH --mail-user=keith.buckholz@yale.edu
#SBATCH --mail-type=ALL
#SBATCH -A m4943
#SBATCH -t 0:90:0
#SBATCH -L cfs

srun -n 1 -c 90 --cpu_bind=cores python /global/cfs/cdirs/m4943/grismsim/psf_grids/scripts/mk_all_grids.py
