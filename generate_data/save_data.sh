#!/bin/bash
cd ..
mkdir $1
cp generate_data/input_file.json $1/
cd $1
python /home/davidjay.dzingeleski/config_tests/generate_data/Compute_SNRs.py input_file.json
python /home/davidjay.dzingeleski/config_tests/generate_data/MakeTestPipeline.py input_file.json $1
