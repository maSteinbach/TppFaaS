#!/bin/bash

apps_large=("fanout_large" "parallel_large" "tree_large")
apps_small=("fanout_small" "parallel_small" "sequence" "tree_small")

echo "1. LESS LOAD datasets"
echo "1.1 create traces for LARGE apps"
echo "1.1.1 WITHOUT randomization"
n1=1000
l1=0.9
u1=1.4

for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1}"
    bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1}
done

echo "1.1.2 WITH randomization"

for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -r"
    bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -r
done

echo "1.2 create traces for SMALL apps"
echo "1.2.1 WITHOUT randomization"
l1=0.3
u1=0.6

for app in "${apps_small[@]}"; do
    echo "bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1}"
    bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1}
done

echo "1.2.2 WITH randomization"

for app in "${apps_small[@]}"; do
    echo "bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -r"
    bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -r
done

############################
echo "2. HIGH LOAD datasets"
echo "2.1 create traces for LARGE apps"
echo "2.1.1 WITHOUT randomization"
n1=100
n2=300
l1=0.9
u1=1.4
l2=0.01
u2=0.01

for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -n2 ${n2} -l2 ${l2} -u2 ${u2}"
    bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -n2 ${n2} -l2 ${l2} -u2 ${u2}
done

echo "2.1.2 WITH randomization"

for app in "${apps_large[@]}"; do
    echo "bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -n2 ${n2} -l2 ${l2} -u2 ${u2} -r"
    bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -n2 ${n2} -l2 ${l2} -u2 ${u2} -r
done

echo "2.2 create traces for SMALL apps"
echo "2.2.1 WITHOUT randomization"
l1=0.3
u1=0.6
l2=0.0001
u2=0.0001

for app in "${apps_small[@]}"; do
    echo "bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -n2 ${n2} -l2 ${l2} -u2 ${u2}"
    bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -n2 ${n2} -l2 ${l2} -u2 ${u2}
done

echo "2.2.2 WITH randomization"

for app in "${apps_small[@]}"; do
    echo "bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -n2 ${n2} -l2 ${l2} -u2 ${u2} -r"
    bash sample.sh -d ${app} -n1 ${n1} -l1 ${l1} -u1 ${u1} -n2 ${n2} -l2 ${l2} -u2 ${u2} -r
done

echo "FINISHED CREATING ALL DATASETS"