#!/bin/bash

for f in $1*
do
bn=$(basename $f)
echo $bn
python -m microportraits $f > $2/${bn%.naf}.csv
done
