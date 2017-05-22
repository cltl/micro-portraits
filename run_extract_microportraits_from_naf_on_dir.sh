#!/bin/bash

for f in $1*
do
bn=$(basename $f)
echo $bn
python extract_mps_from_naf.py $f $2/${bn%.naf}.csv
done
