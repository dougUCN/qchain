qchain  
===============  

A workaround for per-user job limits for a TORQUE or SLURM computing cluster queue.
Say a cluster limits me to MAXJOBS jobs in the queue at a time. qchain.py will 
check your queue for actively running/queued jobs, and then submit as many
t-array jobs as possible + a qchain job. The qchain job will run after the completion
of the last t array job, and keep submitting properly labeled t-array 
jobs until it reaches your specified TOTAL jobs 

Getting started
--------------------

Edit settings in `template.pbs` or `template.slurm` (depending on your cluster) to fit your desired job. 

Usage  
----------------

```
usage: qchain.py [-h] -t TOTAL [-u USERNAME] [-j JOBNUM] [-m MAXJOBS]
                 [-id IDENTIFIER] [-pbs PBS]

Continually submit jobs to TORQUE/SLURM system

optional arguments:
  -h, --help            show this help message and exit
  -t TOTAL, --total TOTAL
                        Total jobs you want to run (default: None)
  -u USERNAME, --username USERNAME
                        Username on cluster acct (default: ucntau)
  -j JOBNUM, --jobNum JOBNUM
                        Starting job number (default: 0)
  -m MAXJOBS, --maxJobs MAXJOBS
                        Max jobs allowed in queue at once (default: 380)
  -id IDENTIFIER, --identifier IDENTIFIER
  -temp TEMPLATE, --template TEMPLATE
                        submission script template
  -c {slurm,torque}, --cluster {slurm,torque}
                        Cluster queue version (default: slurm)
```

progress.json
--------------

This is the file that qchain.py uses to keep track of jobs that have been submitted.
Do not delete this, qchain will delete this file on its own if everything runs smoothly.
progress.json contains an identifying integer to prevent multiple instances of qchain.py from
overriding each other. If you want to spoof an instance of qchain.py to resume from
an existing progress.json file, you can use the `[-id] [--identifier]` flag

runtime warning
----------------

If you get some warning along the lines of 

```
perl: warning: Setting locale failed.
perl: warning: Please check that your locale settings:
        LANGUAGE = (unset),
        LC_ALL = (unset),
        LANG = "C.UTF-8"
    are supported and installed on your system.
perl: warning: Falling back to the standard locale ("C").
```

this can be solved by adding `export LC_ALL=C` to your .bashrc
