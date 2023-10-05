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
#read value of mass, mass ratio, and component spins from input file
f_low=20
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
#create array for SNRs at 1 Mpc to be stored in so the distance of the injected signal can be calculated
SNRs_at_1 = np.zeros((len(mass),len(mass_ratio),len(a1),len(a2),len(theta1),len(theta2),len(phi1),len(phi2)))
#load in psd
psd = rd.PowerSpectrum.from_lalsimulation("SimNoisePSDaLIGOZeroDetHighPower",np.arange(0,2048.5,0.5),f_low)
#convert psd to acf
acf = psd.to_acf()
#will calculate SNR at 1 Mpc for each combination of mass, mass ratio, and component spins
for i in range(len(mass)):
    for j in range(len(mass_ratio)):
        for k in range(len(a1)):
            for l in range(len(a2)):
                for m in range(len(theta1)):
                    for n in range(len(theta2)):
                        for o in range(len(phi1)):
                            for p in range(len(phi2)):
                                #load injection file
                                with open("/home/davidjay.dzingeleski/config_tests/generate_data/injection_kws.json","r") as file_object:
                                    json_data = json.load(file_object)
                                #extract sky location from injection file
                                ra = json_data["ra"]
                                dec = json_data["dec"]
                                #set masses, spins, and distance
                                json_data["mass_1"] = mass_ratio[j]*mass[i]/(1+mass_ratio[j])
                                json_data["mass_2"] = mass[i]/(1+mass_ratio[j])
                                json_data["spin_1z"] = a1[k]*np.cos(theta1[m])
                                json_data["spin_2z"] = a2[l]*np.cos(theta2[n])
                                json_data["spin_1x"] = a1[k]*np.sin(theta1[m])*np.cos(phi1[o])
                                json_data["spin_2x"] = a2[l]*np.sin(theta2[n])*np.cos(phi2[p])
                                json_data["spin_1y"] = a1[k]*np.sin(theta1[m])*np.sin(phi1[o])
                                json_data["spin_2y"] = a2[l]*np.sin(theta2[n])*np.sin(phi2[p])
                                json_data["luminosity_distance"] = 1
                                #extract trigger time
                                time = json_data["trigger_time"]
                                #update injection file
                                with open("/home/davidjay.dzingeleski/config_tests/generate_data/injection_kws.json","w") as file_object:
                                    json.dump(json_data,file_object,indent=2)
                                #calculate delays for the detectors given sky location and time
                                delayh = lal.TimeDelayFromEarthCenter(lal.cached_detector_by_prefix["H1"].location,ra,dec,time)
                                delayl = lal.TimeDelayFromEarthCenter(lal.cached_detector_by_prefix["L1"].location,ra,dec,time)
                                #set up fit
                                fit = rd.fit.Fit.from_config("/home/davidjay.dzingeleski/config_tests/generate_data/test_injection.ini")
                                #select data after the merger
                                datah = fit.data["H1"][time+delayh:time+delayh+0.5]
                                datal = fit.data["L1"][time+delayl:time+delayl+0.5]
                                #calculate snrs for each detector
                                snrh = acf.compute_snr(datah)
                                snrl = acf.compute_snr(datal)
                                #calculate total snr
                                SNR_at_1 = np.sqrt(snrh**2 + snrl**2)
                                #store snr in array
                                SNRs_at_1[i][j][k][l][m][n][o][p] = SNR_at_1
#reshape array to store in input json file
SNRs_at_1 = list(np.reshape(SNRs_at_1,(len(mass)*len(mass_ratio)*len(a1)*len(a2)*len(theta1)*len(theta2)*len(phi1)*len(phi2))))
#add SNRs at 1 to input file
data["SNRs_at_1"] = SNRs_at_1
with open(file,"w") as writefile:
    json.dump(data,writefile,indent=2)