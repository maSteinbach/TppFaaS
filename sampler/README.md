# Sampler

The Sampler is an automated pipeline for generating trace datasets used to train and evaluate TPP models. It creates the datasets by sending n requests to the FaaS application's main function at irregular time intervals. The time intervals between requests are drawn from a continuous uniform distribution with an interval specified by the lower (-l) and upper bound (-u) arguments. The arguments are set by the user, who thus determines the load on OpenWisk and, indirectly, the number of cold starts. Another feature of the Sampler is performing requests in batches, pausing requesting after each batch for a user-specified duration. The batch size and the pause duration are specified with the -b and -w arguments, respectively. To simplify the trace dataset generation process, the Sampler is an end-to-end pipeline that contains all the necessary steps for data generation, such as deploying the application. The result is a dataset consisting of n traces whose format is compatible with training a TPP model.

## Prerequisites

* Python 3.9
* Serverless Framework 2.19.0
* Node.js

## Usage

`pip install --file ../requirements.txt`

`bash sample.sh -d sequence -n 1000 -l 2.0 -u 6.0`

`bash sample.sh -d sequence -n 1000 -l 2.0 -u 6.0 -b 50 -w 120 -e 2 -m 3 -r`

Run it as a background process and write the error & info logs to a file:

`bash sample.sh -d sequence -n 1000 -l 2.0 -u 6.0 &> run.log &`

* -d = directory name of the Serverless app
* -n = number of traces to sample
* -l = lower bound of inter-request duration in seconds
* -u = upper bound of inter-request duration in seconds
* -b = batch size
* -w = pause duration after each batch in seconds
* -r = randomized function duration
* -e = number of function duration anomalies in each trace
* -m = number of missing function anomalies in each trace
