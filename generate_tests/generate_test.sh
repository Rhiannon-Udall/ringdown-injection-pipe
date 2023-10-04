#!/bin/bash
cd ..
mkdir $1
cp generate_tests/input_file.json $1/
cd $1
python /home/davidjay.dzingeleski/config_tests/generate_tests/MakeTestPipeline.py --file "input_file.json" --name "$1"
