#!/home/rhiannon.udall/.conda/envs/ringdown-nrsur/bin/python3
import os
import numpy as np
import pandas as pd
import json
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
    parser.add_argument("--time",
        type=float                 
    )
    args = parser.parse_args()
    return args

#read arguments from input
args = parse()
t_sun = 5*10**-6
M = args.M
q = args.q
spin_1 = args.spin1
spin_2 = args.spin2
snr = args.snr
time = args.time
time_index = (time - 1126259463.413)/(M*t_sun)
#update config file
config = configparser.ConfigParser()
config.read("test_injection.ini")
#prior for each mass is M/2 to 2M
config['prior']['M_min'] = str(M/2)
config['prior']['M_max'] = str(2*M)
#update analysis start time
config['target']['t0'] = str(time)
#set path to data file
config['data']['path'] = "/home/davidjay.dzingeleski/config_tests/data/Results/{{ifo}}_{}_{}_{}_{}_{}.csv".format(int(M),int(q),int(10*spin_1),int(10*spin_2),int(snr))
#write to config file
with open('test_injection.ini', 'w') as configfile:
  config.write(configfile)
#generate fit from config file, data saved using generate_data is already conditioned, so don't need to condition
fit = ringdown.fit.Fit.from_config("test_injection.ini",no_cond=True)
#run the fit
fit.run()
#save the results to a json file
dataframe = fit.result.to_dataframe()
dataframe.to_json('results{}_{}_{}_{}_{}_{}.json'.format(int(M),int(q),int(10*spin_1),int(10*spin_2),int(snr),int(time_index)))
