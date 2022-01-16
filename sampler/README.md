# Sampler

Requests the FaaS application to create a tracing dataset.

## Prerequisites

* Python 3.9
* Serverless Framework 2.19.0
* Node.js

## Usage

`conda install --file requirements.txt`

`bash sample.sh -d sequence -n1 1000 -l1 2.0 -u1 6.0`

`bash sample.sh -d sequence_short -n1 1000 -l1 2.0 -u1 6.0 -n2 1000 -l2 1.0 -u2 3.0 -e 2 -m 3 -r`

`bash sample.sh -d sequence_short -n1 1000 -l1 2.0 -u1 6.0 -e 2 -m 3 -r`

Run it as a background process and write the error & info logs to a file:

`bash sample.sh -d sequence -n1 1000 -l1 2.0 -u1 6.0 &> run.log &`

* -d = directory name of the Serverless app
* -n1 = number of traces to sample (uses l1 and u1)
* -l1 = lower bound of inter-request duration used for traces of n1
* -u1 = upper bound of inter-request duration used for traces of n1
* -n2 = number of traces to sample in the middle of n1 (uses l2 and u2)
* -l2 = lower bound of inter-request duration used for traces of n2
* -u2 = upper bound of inter-request duration used for traces of n2
* -r = randomized function duration
* -e = number of function duration anomalies in each trace
* -m = number of missing function anomalies in each trace
