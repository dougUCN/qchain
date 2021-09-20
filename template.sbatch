#!/bin/bash
### This is a sample job submission script
### Variables JOB_START, JOB_END, and USERNAME will be modified by qchain.py

#SBATCH -J PENTrack
#SBATCH -p general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH --mem=1G
#SBATCH --array $JOB_START-$JOB_END
#SBATCH -o /N/slate/$USERNAME/PENTrack_output/output_%a.txt
#SBATCH -e /N/slate/$USERNAME/PENTrack_output/error_%a.txt

cd /N/u/$USERNAME/Carbonate/PENTrack/
echo "Current working directory is `pwd`"
echo "Starting run at: `date`"
./PENTrack ${SLURM_ARRAY_TASK_ID} "./in/config.in" "/N/slate/$USERNAME/PENTrack_output"
echo "Program diffuse finished with exit code $? at: `date`"
