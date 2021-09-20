#!/bin/bash

#SBATCH -J qchain
#SBATCH -p general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:01:00
#SBATCH --mem=1G
#SBATCH -o qchainStatus.txt
#SBATCH -e qchainError.txt
#SBATCH --dependency=afterok:$SUBMITTED_JOB

cd $SLURM_SUBMIT_DIR
python qchain.py -t $TOTAL -id $IDENTIFIER -u $USERNAME -m $MAXJOBS
