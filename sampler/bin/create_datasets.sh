#!/bin/bash

apps_large=("fanout_large" "parallel_large" "tree_large")
apps_small=("fanout_small" "parallel_small" "sequence" "tree_small")

echo "1. LESS LOAD datasets"
echo "1.1 create traces for LARGE apps"
echo "1.1.1 WITHOUT randomization"
n=1000
l=0.9
u=1.4

for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u}"
    bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u}
done

echo "1.1.2 WITH randomization"

for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -r"
    bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -r
done

echo "1.2 create traces for SMALL apps"
echo "1.2.1 WITHOUT randomization"
l=0.3
u=0.6

for app in "${apps_small[@]}"; do
    echo "bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u}"
    bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u}
done

echo "1.2.2 WITH randomization"

for app in "${apps_small[@]}"; do
    echo "bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -r"
    bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -r
done

############################
echo "2. HIGH LOAD datasets"
echo "2.1 create traces for LARGE apps"
echo "2.1.1 WITHOUT randomization"
n=400
l=0.01
u=0.01
b=50
w=120

for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -b ${b} -w ${w}"
    bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -b ${b} -w ${w}
done

echo "2.1.2 WITH randomization"

for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -b ${b} -w ${w} -r"
    bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -b ${b} -w ${w} -r
done

echo "2.2 create traces for SMALL apps"
echo "2.2.1 WITHOUT randomization"
l=0.0001
u=0.0001

for app in "${apps_small[@]}"; do
    echo "bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -b ${b} -w ${w}"
    bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -b ${b} -w ${w}
done

echo "2.2.2 WITH randomization"

for app in "${apps_small[@]}"; do
    echo "bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -b ${b} -w ${w} -r"
    bash sample.sh -d ${app} -n ${n} -l ${l} -u ${u} -b ${b} -w ${w} -r
done

echo "FINISHED CREATING ALL DATASETS"