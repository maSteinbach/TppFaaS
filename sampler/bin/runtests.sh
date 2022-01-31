#!/bin/bash

# positive tests
# without batching
printf "Run postive test: should run script without batching\n"
bash sample.sh -d sequence -n 10 -l 0.1 -u 0.5 -r

# with batching
printf "\nRun postive test: should run script with batching\n"
bash sample.sh -d sequence -n 10 -l 0.1 -u 0.5 -b 5 -w 6 -r

# with anomalies
printf "\nRun postive test: should run script with anomalies\n"
bash sample.sh -d sequence -n 10 -l 0.1 -u 0.5 -b 5 -w 6 -r -e 1 -m 2

# negative tests
# upper bound missing
printf "\nRun negative test: should exit with 'Upper bound (flag: -u) is missing.'\n"
bash sample.sh -d sequence -n 10 -l 1.0

# lower bound larger than upper bound
printf "\nRun negative test: should exit with 'Lower bound is larger than upper bound.'\n"
bash sample.sh -d sequence -n 10 -l 2.0 -u 1.0

# batch size missing
printf "\nRun negative test: should exit with 'Either batch size (flag: -b) or pause duration (flag: -w) argument is missing.'\n"
bash sample.sh -d sequence -n 10 -l 0.1 -u 0.5 -w 60

# pause duration missing
printf "\nRun negative test: should exit with 'Either batch size (flag: -b) or pause duration (flag: -w) argument is missing.'\n"
bash sample.sh -d sequence -n 10 -l 0.1 -u 0.5 -b 20

# batch size 0
printf "\nRun negative test: should exit with 'Batch size (flag: -b) and pause duration (flag: -w) must be larger than 0.'\n"
bash sample.sh -d sequence -n 10 -l 0.1 -u 0.5 -b 0 -w 60

# pause duration 0
printf "\nRun negative test: should exit with 'Batch size (flag: -b) and pause duration (flag: -w) must be larger than 0.'\n"
bash sample.sh -d sequence -n 10 -l 0.1 -u 0.5 -b 20 -w 0

# anomaly flags negative
printf "\nRun negative test: should exit with 'Anomalie flags -e and -m must be non-negative.'\n"
bash sample.sh -d sequence -n 10 -l 0.1 -u 0.5 -e -1 -m -1