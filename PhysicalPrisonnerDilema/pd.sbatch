#!/bin/bash
# Reza Torbati
#
# Reasonable partitions: debug_5min, debug_30min, normal
#

#SBATCH --partition=debug_5min
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
# memory in MB
#SBATCH --mem=2000
# The %04a is translated into a 4-digit number that encodes the SLURM_ARRAY_TASK_ID
#SBATCH --output=slurmOut/tunerV4Model4_%a_stdout.txt
#SBATCH --error=slurmOut/tunerV4Model4_%a_stderr.txt
#SBATCH --time=00:05:00
#SBATCH --job-name=PhysicalPrisonersDilema
#SBATCH --mail-user=kofcrotmgiv@gmail.com
#SBATCH --mail-type=ALL
#SBATCH --chdir=/home/rtorbati/MutliRobotSystemsProject/PhysicalPrisonnerDilema
#################################################


python3 train_v2.py


