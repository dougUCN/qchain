#!/usr/bin/env python
# Doug Wong
# 4/18/2021 -- Updated from TORQUE to SLURM 

import argparse
import os, subprocess, sys
import time, collections, json
import numpy as np
from datetime import datetime

RESUBMIT = 'chain.sbatch'          # Name of resubmission script
TEMPLATE = 'template.sbatch'       # Template job script
PROGRESSFILE = 'progress.json'  # Name of job progress tracker file
USERNAME = 'ucntau'             # Username on cluster account

def main():
    parser = argparse.ArgumentParser(description='Continually submit jobs to TORQUE/SLURM system',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", "--total", required=True, type=int, help="Total jobs you want to run")
    parser.add_argument("-u", "--username", type=str, default=USERNAME, help="Username on cluster acct")
    parser.add_argument("-j", "--jobNum", type=int, default=0, help="Starting job number")
    parser.add_argument("-m", "--maxJobs", type=int, default=380, help="Max jobs allowed in queue at once")
    parser.add_argument("-id", "--identifier", type=int, default=np.random.default_rng().integers(1000))
    parser.add_argument("-pbs", "--pbs", type=str, default=TEMPLATE, help='submission script template')
    args = parser.parse_args()

    print('Starting qchain.py ', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Check for existence of progress file
    if os.path.isfile(PROGRESSFILE):
        print(f'Found file {PROGRESSFILE}')
        with open(PROGRESSFILE,'r') as infile:
            progress = json.load(infile)
        if args.identifier != progress['identifier']:
            print(f'Error: "identifier" in {PROGRESSFILE} does not match this instance of qchain.py!')
            print('There may already be an instance of qchain.py running!')
            sys.exit()
        print(f'{progress["N_submitted"]} jobs have been submitted')
    else:
        progress = {'identifier' : int(args.identifier),
                    'total'      : args.total,
                    'N_submitted': 0,
                    'last_jobNum': args.jobNum - 1}

    # Check current number of jobs in queue/ currently running
    # inQueue = int( subprocess.check_output(f'qselect -u {args.username} -s QR | wc -l', shell=True) )
    inQueue = int( subprocess.check_output(f'squeue -h -u {args.username} | wc -l', shell=True) )


    print(f'Detected {inQueue} jobs in queue')

    # Figure out how many jobs you can submit
    allowedSubmit = args.maxJobs - inQueue
    jobsLeft = progress['total'] - progress['N_submitted']
    if allowedSubmit <= 0:
        print(f'Error: Too many jobs currently in queue. Max allowed {args.maxJobs}')
        sys.exit()
    elif jobsLeft == 0:  # In case qchain is called on accident when jobs are already submitted
        print(f'No jobs left needed to be submitted. Removing {PROGRESSFILE}')
        os.remove(PROGRESSFILE)
        sys.exit()
    elif allowedSubmit > jobsLeft:
        toSubmit = jobsLeft
        jobsLeft = 0
    else:
        toSubmit = allowedSubmit - 1 # Need to submit qchain.py job
        jobsLeft = jobsLeft - toSubmit

    print(f'Submitting {toSubmit} jobs to queue. {jobsLeft} jobs left')
    jobStart = progress['last_jobNum'] + 1
    jobEnd = progress['last_jobNum'] + toSubmit
    replacements = {'$JOB_START': str(jobStart),
                    '$JOB_END': str(jobEnd),
                    '$TOTAL'  : str(progress['total']),
                    '$IDENTIFIER': str(progress['identifier']),
                    '$USERNAME': str(args.username),
                    '$MAXJOBS': str(args.maxJobs)}

    # Submit PBS job array to torque queue
    jobNum = submitToQueue(args.pbs, replacements)
    print(f'Job ID: {jobNum}')
    # jobNum = jobNum[:-2] # Get rid of the [] characters at the end of the string

    # submit chaining job to torque queue if needed
    if jobsLeft > 0:
        # replacements.update( {'$SUBMITTED_JOB': f'{jobNum}[{jobEnd}]'} ) # retrigger qchain after last t array job
        replacements.update( {'$SUBMITTED_JOB': f'{jobNum}_{jobEnd}'} ) # retrigger qchain after last t array job
        resubmitJobNum = submitToQueue(RESUBMIT, replacements)
        print(f'Cluster will rerun qchain.py to submit more jobs later (Job ID: {resubmitJobNum})')

        # Update/create progress file
        print(f'Updating file "{PROGRESSFILE}"')
        progress['N_submitted'] += toSubmit
        progress['last_jobNum'] = jobEnd
        with open(PROGRESSFILE, 'w') as outfile:
            outfile.write( json.dumps(progress, indent=4) )

    else:
        print('All jobs have now been submitted')
        if os.path.isfile(PROGRESSFILE):
            print(f'Removing file {PROGRESSFILE}')
            os.remove(PROGRESSFILE)
        sys.exit()

    return

def noExt(filename, extensionName):
    '''Removes the extension name from a filename if present'''
    for ext in get_iterable(extensionName):
        if filename[-len(ext):].find(ext) != -1:
            return filename[:-len(ext)]
    return filename

def get_iterable(x):
    if isinstance(x, collections.Iterable):
        return x
    else:
        return (x,)

def copyReplace(inName, outName, replacements):
    '''Creates "outfile". Words from "infile" are replaced according to the dictionary, "replacements"'''
    with open(inName) as infile, open(outName, 'w') as outfile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            outfile.write(line)
    return

def submitToQueue(template, replacements, submitName='submitMe.pbs', removePBS=True):
    '''
    Creates a submission pbs script from the template, and submits to queue
    Returns string jobID
    '''
    if not os.path.isfile(template):
        print(f"Error: Cannot find {template}" + template)
        sys.exit()

    # Make new file submission PBS script from template file
    copyReplace(template, submitName, replacements)

    # Submit job and get jobID
    # The last 4 characters are ".s1\n", I just want the job ID
    # stdout = subprocess.check_output(["qsub", submitName]).decode('ascii')[:-4]

    # sbatch submission returns "Submitted batch job JOB_ID\n"
    stdout = subprocess.check_output(["sbatch", submitName]).decode('ascii')[20:-1]

    if removePBS:
        os.remove( submitName )

    return stdout

if ( __name__ == '__main__' ):
    main()
