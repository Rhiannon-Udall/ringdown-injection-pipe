#!/home/rhiannon.udall/.conda/envs/ringdown-nrsur/bin/python3
import os
import numpy as np
import arviz as az
import pandas as pd
import seaborn as sns
import json
import sys
import ringdown as rd
import pycbc.detector

os.environ["LAL_DATA_PATH"] = "/home/rhiannon.udall/.conda/envs/ringdown-nrsur/opt/lalsuite-extra/share/lalsimulation"
f_low=20
file = str(sys.argv[1])
with open(file,"r") as readfile:
    data = json.load(readfile)
mass = np.array(data["mass"])
mass_ratio = np.array(data["mass_ratio"])
spin_1 = np.array(data["spin_1"])
spin_2 = np.array(data["spin_2"])
SNRs_at_1 = np.zeros((len(mass),len(mass_ratio),len(spin_1),len(spin_2)))
psd = rd.PowerSpectrum.from_lalsimulation("SimNoisePSDaLIGOZeroDetHighPower",np.arange(0,2048.5,0.5),f_low)
acf = psd.to_acf()
for i in range(len(mass)):
    for j in range(len(mass_ratio)):
        for k in range(len(spin_1)):
            for l in range(len(spin_2)):
                with open("/home/davidjay.dzingeleski/config_tests/generate_data/injection_kws.json","r") as file_object:
                    json_data = json.load(file_object)
                ra = json_data["ra"]
                dec = json_data["dec"]
                json_data["mass_1"] = mass_ratio[j]*mass[i]/(1+mass_ratio[j])
                json_data["mass_2"] = mass[i]/(1+mass_ratio[j])
                json_data["spin_1z"] = spin_1[k]
                json_data["spin_2z"] = spin_2[l]
                json_data["luminosity_distance"] = 1
                time = json_data["trigger_time"]
                with open("/home/davidjay.dzingeleski/config_tests/generate_data/injection_kws.json","w") as file_object:
                    json.dump(json_data,file_object,indent=2)
                dh = pycbc.detector.Detector("H1")
                dl = pycbc.detector.Detector("L1")
                delayh = dh.time_delay_from_earth_center(ra,dec,time)
                delayl = dl.time_delay_from_earth_center(ra,dec,time)
                fit = rd.fit.Fit.from_config("/home/davidjay.dzingeleski/config_tests/generate_data/test_injection.ini")
                datah = fit.data["H1"][time+delayh:time+delayh+0.5]
                datal = fit.data["L1"][time+delayl:time+delayl+0.5]
                snrh = acf.compute_snr(datah)
                snrl = acf.compute_snr(datal)
                SNR_at_1 = np.sqrt(snrh**2 + snrl**2)
                SNRs_at_1[i][j][k][l] = SNR_at_1
SNRs_at_1 = list(np.reshape(SNRs_at_1,(len(mass)*len(mass_ratio)*len(spin_1)*len(spin_2))))
data["SNRs_at_1"] = SNRs_at_1
with open(file,"w") as writefile:
    json.dump(data,writefile,indent=2)