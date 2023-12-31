from rdipipe import condorutils
import os
from glue import pipeline
import sys
import numpy as np
import json

def parse():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file",
        type=str                   
    )
    parser.add_argument("--name",
        type=str
    )
    args = parser.parse_args()
    return args

#load arguments
args=parse()
file=args.file
name=args.name

#setting name and accounting tag for job submission
ligo_user_name = "davidjay.dzingeleski"
ligo_accounting = "ligo.dev.o4.cbc.pe.bilby"

#set up directories for result files and log/error files
pipeline_dir = os.path.join(os.getcwd(), "Results")
os.makedirs(pipeline_dir)
logdir = os.path.join(pipeline_dir, "logs")
os.makedirs(logdir)

#set up dag
dag = pipeline.CondorDAG(
    log=os.path.join(pipeline_dir, "dag_{}.log".format(name))
)
dag.set_dag_file(os.path.join(pipeline_dir, "dag_{}".format(name)))

#set up job with extra arguments
worker_job = condorutils.standard_job_constructor(
    "ringdownfit.py",
    name,
    f"--M $(M) --q $(q) --a1 $(a1) --a2 $(a2) --theta1 $(theta1) --theta2 $(theta2) --phi1 $(phi1) --phi2 $(phi2) --snr $(snr) --time $(time) --inclination $(inclination) --modes $(modes)",
    user_name=ligo_user_name,
    accounting=ligo_accounting,
    request_memory="4 Gb",
    initialdir=pipeline_dir,
    logdir=logdir,
    extra_cmds = [["transfer_input_files","/home/davidjay.dzingeleski/config_tests/generate_tests/test_injection.ini, /home/davidjay.dzingeleski/config_tests/generate_tests/acf.csv"],["transfer_executable",True],["should_transfer_files","YES"],["getenv",True]]
)
#set executable for the job
worker_job.set_executable("/home/davidjay.dzingeleski/config_tests/generate_tests/ringdownfit.py")

#read parameter values from input file
t_sun = 5*10**-6
with open(file,"r") as readfile:
    data = json.load(readfile)
mass = np.array(data["mass"])
mass_ratio = np.array(data["mass_ratio"])
a1 = np.array(data["a1"])
a2 = np.array(data["a2"])
theta1 = np.array(data["theta1"])
theta2 = np.array(data["theta2"])
phi1 = np.array(data["phi1"])
phi2 = np.array(data["phi2"])
time = np.array(data["time"])
SNR = np.array(data["SNR"])
inclination = np.array(data["inclination"])
modes = np.array(data["modes"])
#set up list of parameter combinations
worker_nodes = []
for i in range(len(mass)):
    for j in range(len(mass_ratio)):
        for k in range(len(a1)):
            for l in range(len(a2)):
                for m in range(len(theta1)):
                    for n in range(len(theta2)):
                        for o in range(len(phi1)):
                            for p in range(len(phi2)):
                                for q in range(len(SNR)):
                                    for r in range(len(time)):
                                        for s in range(len(inclination)):
                                            for t in range(len(modes)):
                                                #set up job with combination of parameters
                                                worker_node = condorutils.standard_node_constructor(
                                                    worker_job,
                                                    dag,
                                                    macros=[("M", mass[i]), ("q", mass_ratio[j]), ("a1", a1[k]), ("a2", a2[l]), ("theta1", theta1[m]), ("theta2", theta2[n]), ("phi1", phi1[o]), ("phi2", phi2[p]), ("snr", SNR[q]), ("time", 1126259463.413 + time[r]*mass[i]*t_sun), ("inclination", inclination[s]), ("modes", modes[t])],
                                                    )
                                                #add job to the list
                                                worker_nodes += [worker_node]

# Write sub files and dag
dag.write_sub_files()
dag.write_dag()

# Automatically submit
os.system(
    f"condor_submit_dag {os.path.join(pipeline_dir, 'dag_{}.dag'.format(name))}"
)
