#!/bin/bash

#SBATCH -N 1
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -J "Produce PSF Grids"
#SBATCH --mail-user=keith.buckholz@yale.edu
#SBATCH --mail-type=ALL
#SBATCH -A m4943
#SBATCH -t 0:45:0
#SBATCH -L cfs

srun python /global/common/software/m4943/grizli0/psf_grids/scripts/mk_all_grids.py
