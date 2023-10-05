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
    parser.add_argument("--a1",
        type=float                 
    )
    parser.add_argument("--a2",
        type=float                 
    )
    parser.add_argument("--theta1",
        type=float                 
    )
    parser.add_argument("--theta2",
        type=float                 
    )
    parser.add_argument("--phi1",
        type=float                 
    )
    parser.add_argument("--phi2",
        type=float                 
    )
    parser.add_argument("--snr",
        type=float                 
    )
    parser.add_argument("--time",
        type=float                 
    )
    parser.add_argument("--inclination",
        type=float                 
    )
    parser.add_argument("--modes",
        type=float                 
    )
    args = parser.parse_args()
    return args

#dictionary of modes
modes_dict = {
    0:"(1, -2, 2, 2, 0),(1, -2, 2, 2, 1)"
}
#read off arguments from input
args = parse()
t_sun = 5*10**-6
M = args.M
q = args.q
a1 = args.a1
a2 = args.a2
theta1 = args.theta1
theta2 = args.theta2
phi1 = args.phi1
phi2 = args.phi2
snr = args.snr
time = args.time
time_index = (time - 1126259463.413)/(M*t_sun)
inclination_index = args.inclination
modes_index = args.modes
#update the config file
config = configparser.ConfigParser()
config.read("test_injection.ini")
#mass prior goes from M/2 to 2M
config['prior']['M_min'] = str(M/2)
config['prior']['M_max'] = str(2*M)
#set target time
config['target']['t0'] = str(time)
#set modes to detect
config['model']['modes'] = modes_dict[modes_index]
#set path to data file
config['data']['path'] = "/home/davidjay.dzingeleski/config_tests/data/Results/{{ifo}}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}.csv".format(int(M),int(q),int(10*a1),int(10*a2),int(theta1),int(theta2),int(phi1),int(phi2),int(snr),int(inclination_index))
#write updates to config file
with open('test_injection.ini', 'w') as configfile:
  config.write(configfile)
#create fit object
fit = ringdown.fit.Fit.from_config("test_injection.ini",no_cond=True)
#run the fit
fit.run()
#save the results
dataframe = fit.result.to_dataframe()
dataframe.to_json('results{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}.json'.format(int(M),int(q),int(10*a1),int(10*a2),int(theta1),int(theta2),int(phi1),int(phi2),int(snr),int(time_index),int(inclination_index),int(modes_index)))