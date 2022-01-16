#!/bin/bash

apps_large=("fanout_large_short" "parallel_large_short" "sequence_short" "tree_large_short")

echo "1. Create normal datasets with 1000 traces each."
echo "1.1 Without random function duration"
n=1000
for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2"
    bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2
done
echo "1.2 With random function duration"
for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -r"
    bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -r
done

echo "2. Create anomaly datasets with 100 traces each."
echo "2.1 Without random function duration"
n=100
for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -e 2"
    bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -e 2
    echo "bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -m 2"
    bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -m 2
    echo "bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -e 2 -m 2"
    bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -e 2 -m 2
done
echo "2.2 With random function duration"
for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -e 2 -r"
    bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -e 2 -r
    echo "bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -m 2 -r"
    bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -m 2 -r
    echo "bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -e 2 -m 2 -r"
    bash sample.sh -d "${app}" -n1 "${n}" -l1 1.2 -u1 1.2 -e 2 -m 2 -r
done
echo "CREATED ALL DATASETS"