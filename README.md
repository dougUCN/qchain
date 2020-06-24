qchain  
===============  

A workaround for per-user limits for a TORQUE queue on a PBS array job.
Say a cluster limits me to MAXJOBS jobs in the queue at a time. qchain.py will 
check your queue for actively running/queued jobs, and then submit as many PBS
t-array jobs as possible + a qchain job. The qchain job will run after the completion
of the last t array job, and keep submitting properly labeled t-array 
jobs until it reaches your specified TOTAL jobs 

Getting started
--------------------

Edit settings in `template.pbs` to fit your desired job. You can also change
any of the default parameters USERNAME, JOBNUM, or MAXJOBS by editing the variables in qchain.py.

Usage  
----------------

```
usage: qchain.py [-h] -t TOTAL [-u USERNAME] [-j JOBNUM] [-m MAXJOBS]
                 [-id IDENTIFIER]

Continually submit jobs to TORQUE system

optional arguments:
  -h, --help            show this help message and exit
  -t TOTAL, --total TOTAL
                        Total jobs you want to run (default: None)
  -u USERNAME, --username USERNAME
                        Username on cluster acct (default: ucntau)
  -j JOBNUM, --jobNum JOBNUM
                        Starting job number (default: 0)
  -m MAXJOBS, --maxJobs MAXJOBS
                        Max jobs allowed in queue at once (default: 351)
  -id IDENTIFIER, --identifier IDENTIFIER
```

chain.pbs
-----------

Contains settings for when qchain.py is run by the cluster. I have things currently
configured so that cluster output gets written to `qchainError.txt` and  `qchainStatus.txt`.
You can use these to see how many jobs qchain has left to submit

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
