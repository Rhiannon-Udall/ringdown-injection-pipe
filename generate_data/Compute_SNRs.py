#!/home/rhiannon.udall/.conda/envs/ringdown-nrsur/bin/python3
import os
import numpy as np
import pandas as pd
import json
import ringdown as rd
import lal

def parse():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file",
        type=str                   
    )
    args = parser.parse_args()
    return args

#read file
args = parse()
file = args.file

os.environ["LAL_DATA_PATH"] = "/home/rhiannon.udall/.conda/envs/ringdown-nrsur/opt/lalsuite-extra/share/lalsimulation"
#read values of mass, mass ratio, and component spins from input file
f_low=20
with open(file,"r") as readfile:
    data = json.load(readfile)
mass = np.array(data["mass"])
mass_ratio = np.array(data["mass_ratio"])
spin_1 = np.array(data["spin_1"])
spin_2 = np.array(data["spin_2"])
#create array for SNRs_at_1 to be stored in so that the distance for the injected signal can be calculated
SNRs_at_1 = np.zeros((len(mass),len(mass_ratio),len(spin_1),len(spin_2)))
#load in psd
psd = rd.PowerSpectrum.from_lalsimulation("SimNoisePSDaLIGOZeroDetHighPower",np.arange(0,2048.5,0.5),f_low)
#convert psd to acf
acf = psd.to_acf()
#will calculate SNR at 1 Mpc for each combination of mass, mass ratio, and component spins
for i in range(len(mass)):
    for j in range(len(mass_ratio)):
        for k in range(len(spin_1)):
            for l in range(len(spin_2)):
                #load injection file
                with open("/home/davidjay.dzingeleski/config_tests/generate_data/injection_kws.json","r") as file_object:
                    json_data = json.load(file_object)
                #extract sky location from injection file
                ra = json_data["ra"]
                dec = json_data["dec"]
                #set masses, spins, and distance
                json_data["mass_1"] = mass_ratio[j]*mass[i]/(1+mass_ratio[j])
                json_data["mass_2"] = mass[i]/(1+mass_ratio[j])
                json_data["spin_1z"] = spin_1[k]
                json_data["spin_2z"] = spin_2[l]
                json_data["luminosity_distance"] = 1
                #extract trigger time from injection file
                time = json_data["trigger_time"]
                #update the injection file
                with open("/home/davidjay.dzingeleski/config_tests/generate_data/injection_kws.json","w") as file_object:
                    json.dump(json_data,file_object,indent=2)
                #calculate delays for the detectors given sky location and time
                delayh = lal.TimeDelayFromEarthCenter(lal.cached_detector_by_prefix["H1"].location,ra,dec,time)
                delayl = lal.TimeDelayFromEarthCenter(lal.cached_detector_by_prefix["L1"].location,ra,dec,time)
                #load the fit to create the injection data
                fit = rd.fit.Fit.from_config("/home/davidjay.dzingeleski/config_tests/generate_data/test_injection.ini")
                #select the data after the merger
                datah = fit.data["H1"][time+delayh:time+delayh+0.5]
                datal = fit.data["L1"][time+delayl:time+delayl+0.5]
                #calculate the snrs for each detector
                snrh = acf.compute_snr(datah)
                snrl = acf.compute_snr(datal)
                #calculate total snr
                SNR_at_1 = np.sqrt(snrh**2 + snrl**2)
                #store snr in array
                SNRs_at_1[i][j][k][l] = SNR_at_1
#reshape array to store in input json file
SNRs_at_1 = list(np.reshape(SNRs_at_1,(len(mass)*len(mass_ratio)*len(spin_1)*len(spin_2))))
#add SNRs at 1 to input file
data["SNRs_at_1"] = SNRs_at_1
with open(file,"w") as writefile:
    json.dump(data,writefile,indent=2)
