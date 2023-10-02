from rdipipe import condorutils
import os
from glue import pipeline
import sys
import numpy as np
import json


ligo_user_name = "davidjay.dzingeleski"
ligo_accounting = "ligo.dev.o4.cbc.pe.bilby"

pipeline_dir = os.path.join(os.getcwd(), "Results")
os.makedirs(pipeline_dir)
logdir = os.path.join(pipeline_dir, "logs")
os.makedirs(logdir)

dag = pipeline.CondorDAG(
    log=os.path.join(pipeline_dir, "dag_{}.log".format(str(sys.argv[2])))
)
dag.set_dag_file(os.path.join(pipeline_dir, "dag_{}".format(str(sys.argv[2]))))

worker_job = condorutils.standard_job_constructor(
    "ringdownfit.py",
    str(sys.argv[2]),
    f"--M $(M) --q $(q) --spin1 $(spin1) --spin2 $(spin2) --snr $(snr) --time $(time)",
    user_name=ligo_user_name,
    accounting=ligo_accounting,
    request_memory="4 Gb",
    initialdir=pipeline_dir,
    logdir=logdir,
    extra_cmds = [["transfer_input_files","/home/davidjay.dzingeleski/config_tests/generate_tests/test_injection.ini, /home/davidjay.dzingeleski/config_tests/generate_tests/acf.csv"],["transfer_executable",True],["should_transfer_files","YES"],["getenv",True]]
)
worker_job.set_executable("/home/davidjay.dzingeleski/config_tests/generate_tests/ringdownfit.py")

t_sun = 5*10**-6
file = str(sys.argv[1])
with open(file,"r") as readfile:
    data = json.load(readfile)
mass = np.array(data["mass"])
mass_ratio = np.array(data["mass_ratio"])
spin_1 = np.array(data["spin_1"])
spin_2 = np.array(data["spin_2"])
time = np.array(data["time"])
SNR = np.array(data["SNR"])
worker_nodes = []
for i in range(len(mass)):
    for j in range(len(mass_ratio)):
        for k in range(len(spin_1)):
            for l in range(len(spin_2)):
                for m in range(len(SNR)):
                    for n in range(len(time)):
                        worker_node = condorutils.standard_node_constructor(
                            worker_job,
                            dag,
                            macros=[("M", mass[i]), ("q", mass_ratio[j]), ("spin1", spin_1[k]), ("spin2", spin_2[l]), ("snr", SNR[m]), ("time", 1126259463.413 + time[n]*mass[i]*t_sun)],
                            )
                        worker_nodes += [worker_node]

# Write sub files and dag
dag.write_sub_files()
dag.write_dag()

# Automatically submit
os.system(
    f"condor_submit_dag {os.path.join(pipeline_dir, 'dag_{}.dag'.format(str(sys.argv[2])))}"
)
