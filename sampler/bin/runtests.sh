#!/bin/bash

# positive tests
# without batching
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -r

# with batching
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 20 -w 60 -r

# with anomalies
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 20 -w 60 -r -e 2 -m 2

# negative tests
# upper bound missing
bash sample.sh -d sequence -n 100 -l 1.0

# lower bound larger than upper bound
bash sample.sh -d sequence -n 100 -l 2.0 -u 1.0

# batch size missing
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -w 60

# pause duration missing
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 20

# batch size 0
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 0 -w 60

# pause duration 0
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -b 20 -w 0

# anomaly flags negative
bash sample.sh -d sequence -n 100 -l 1.0 -u 2.0 -e -1 -m -1