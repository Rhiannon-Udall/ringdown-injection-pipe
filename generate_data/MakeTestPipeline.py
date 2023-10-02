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
    "save_data.py",
    str(sys.argv[2]),
    f"--M $(M) --q $(q) --spin1 $(spin1) --spin2 $(spin2) --snr $(snr) --distance $(distance)",
    user_name=ligo_user_name,
    accounting=ligo_accounting,
    request_memory="4 Gb",
    initialdir=pipeline_dir,
    logdir=logdir,
    extra_cmds = [["transfer_input_files","/home/davidjay.dzingeleski/config_tests/generate_data/injection_kws.json, /home/davidjay.dzingeleski/config_tests/generate_data/test_injection.ini"],["transfer_executable",True],["should_transfer_files","YES"],["getenv",True]]
)
worker_job.set_executable("/home/davidjay.dzingeleski/config_tests/generate_data/save_data.py")

file = str(sys.argv[1])
with open(file,"r") as readfile:
    data = json.load(readfile)
mass = np.array(data["mass"])
mass_ratio = np.array(data["mass_ratio"])
spin_1 = np.array(data["spin_1"])
spin_2 = np.array(data["spin_2"])
SNRs_at_1 = np.reshape(np.array(data["SNRs_at_1"]),(len(mass),len(mass_ratio),len(spin_1),len(spin_2)))
SNR = np.array(data["SNR"])
worker_nodes = []
for i in range(len(mass)):
    for j in range(len(mass_ratio)):
        for k in range(len(spin_1)):
            for l in range(len(spin_2)):
                for m in range(len(SNR)):
                    worker_node = condorutils.standard_node_constructor(
                        worker_job,
                        dag,
                        macros=[("M", mass[i]), ("q", mass_ratio[j]), ("spin1", spin_1[k]), ("spin2", spin_2[l]), ("snr", SNR[m]), ("distance", SNRs_at_1[i][j][k][l]/SNR[m])],
                        )
                    worker_nodes += [worker_node]

# Write sub files and dag
dag.write_sub_files()
dag.write_dag()

# Automatically submit
os.system(
    f"condor_submit_dag {os.path.join(pipeline_dir, 'dag_{}.dag'.format(str(sys.argv[2])))}"
)
