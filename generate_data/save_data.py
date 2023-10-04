#!/home/rhiannon.udall/.conda/envs/ringdown-nrsur/bin/python3
import os
import numpy as np
import arviz as az
import pandas as pd
import seaborn as sns
import json
import sys
import configparser
import ringdown

os.environ["LAL_DATA_PATH"] = "/home/rhiannon.udall/.conda/envs/ringdown-nrsur/opt/lalsuite-extra/share/lalsimulation"

def parse():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--M",
        type=float                   
    )
    parser.add_argument("--q",
        type=float
    )
    parser.add_argument("--spin1",
        type=float                 
    )
    parser.add_argument("--spin2",
        type=float                 
    )
    parser.add_argument("--snr",
        type=float                 
    )
    parser.add_argument("--distance",
        type=float                 
    )
    parser.add_argument("--inclination",
        type=float                 
    )
    args = parser.parse_args()
    return args

inclinations_dict= {0:0,
                1:np.pi/6,
                2:np.pi/4,
                3:np.pi/3,
                4:np.pi/2}
#load variables from input arguments
args = parse()
M = args.M
q = args.q
spin_1 = args.spin1
spin_2 = args.spin2
snr = args.snr
dist_mpc = args.distance
inclination_index = args.inclination
inclination = inclinations_dict[inclination_index]
#update injection file with new values
with open("injection_kws.json","r") as file_object:
    json_data = json.load(file_object)
json_data["mass_1"] = q*M/(1+q)
json_data["mass_2"] = M/(1+q)
json_data["spin_1z"] = spin_1
json_data["spin_2z"] = spin_2
json_data["luminosity_distance"] = dist_mpc
json_data["inclination"] = inclination
with open("injection_kws.json","w") as file_object:
    json.dump(json_data,file_object,indent=2)
#update config file with path to injection file
config = configparser.ConfigParser()
config.read("test_injection.ini")
config['injection']['path'] = "injection_kws.json"
with open('test_injection.ini', 'w') as configfile:
  config.write(configfile)
#create fit object from config file with injected data
fit = ringdown.fit.Fit.from_config("test_injection.ini")
#save injection data for each ifo to csv files
fit.data["H1"].to_csv("H1_{}_{}_{}_{}_{}_{}.csv".format(int(M),int(q),int(10*spin_1),int(10*spin_2),int(snr),int(inclination_index)))
fit.data["L1"].to_csv("L1_{}_{}_{}_{}_{}_{}.csv".format(int(M),int(q),int(10*spin_1),int(10*spin_2),int(snr),int(inclination_index)))