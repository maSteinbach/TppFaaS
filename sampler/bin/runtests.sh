#!/bin/bash

# positive tests
# without batching
echo "Run postive test: should run script without batching"
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -r

# with batching
echo "Run postive test: should run script with batching"
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 20 -w 60 -r

# with anomalies
echo "Run postive test: should run script with anomalies"
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 20 -w 60 -r -e 2 -m 2

# negative tests
# upper bound missing
echo "Run negative test: should exit with 'App directory name (flag: -d), number of traces (flag: -n), lower bound (flag: -l), or upper bound (flag: -u) is missing.'"
bash sample.sh -d sequence -n 100 -l 1.0

# lower bound larger than upper bound
echo "Run negative test: should exit with 'Lower bound is larger than upper bound.'"
bash sample.sh -d sequence -n 100 -l 2.0 -u 1.0

# batch size missing
echo "Run negative test: should exit with 'Either batch size (flag: -b) or pause duration (flag: -w) argument is missing.'"
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -w 60

# pause duration missing
echo "Run negative test: should exit with 'Either batch size (flag: -b) or pause duration (flag: -w) argument is missing.'"
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 20

# batch size 0
echo "Run negative test: should exit with 'Batch size (flag: -b) and pause duration (flag: -w) must be larger than 0.'"
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 0 -w 60

# pause duration 0
echo "Run negative test: should exit with 'Batch size (flag: -b) and pause duration (flag: -w) must be larger than 0.'"
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 20 -w 0

# anomaly flags negative
echo "Run negative test: should exit with 'Anomalie flags -e and -m must be non-negative.'"
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -e -1 -m -1