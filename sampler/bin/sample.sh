#!/bin/bash

err() {
  echo "Error: $*" >&2
}

float_le() {
    echo "$(echo "$1 <= $2" | bc)"
}

float_less() {
    echo "$(echo "$1 < $2" | bc)"
}

float_larger() {
    echo "$(echo "$1 > $2" | bc)"
}

yaml() {
    python -c "import yaml; print(yaml.safe_load(open('$1'))$2)"
}

dflag=
nflag=
lflag=
uflag=
bflag=
wflag=
rflag=0
eflag=0
mflag=0

while :; do
  case $1 in
    -d)
        dflag=$2
        shift
        ;;
    -n)
        nflag=$2
        shift
        ;;
    -l)
        lflag=$2
        shift
        ;;
    -u)
        uflag=$2
        shift
        ;;
    -b)
        bflag=$2
        shift
        ;;
    -w)
        wflag=$2
        shift
        ;;
    -r)
        rflag=1
        ;;
    -e)
        eflag=$2
        shift
        ;;
    -m)
        mflag=$2
        shift
        ;;
    --)         # End of all options.
        shift
        break
        ;;
    *)          # Default case: No more options, so break out of the loop.
        break
  esac
  shift
done
# Check if all arguments are given and valid.
echo "d: ${dflag:?App directory name (flag: -d) is missing.}"
echo "n: ${nflag:?Number of traces (flag: -n) is missing.}"
echo "l: ${lflag:?Lower bound (flag: -l) is missing.}"
echo "u: ${uflag:?Upper bound (flag: -u) is missing.}"
if [[ -n ${bflag} || ${wflag} ]]; then
    echo "b: ${bflag}"
    echo "w: ${wflag}"
fi
echo "r: ${rflag}"
if [[ $eflag -ne 0 || $mflag -ne 0 ]]; then
    echo "e: ${eflag}"
    echo "m: ${mflag}"
fi
if (( $(float_larger ${lflag} ${uflag}) )); then
    err "Lower bound is larger than upper bound."
    exit 1
fi
if [[ -z ${bflag} && -n ${wflag} || -n ${bflag} && -z ${wflag} ]]; then
    err "Either batch size (flag: -b) or pause duration (flag: -w) argument is missing."
    exit 1
fi
if [[ -n ${bflag} && $(float_le ${bflag} 0) -eq 1 || -n ${wflag} && $(float_le ${wflag} 0) -eq 1 ]]; then
    err "Batch size (flag: -b) and pause duration (flag: -w) must be larger than 0."
    exit 1
fi
if (( $(float_less ${eflag} 0) || $(float_less ${mflag} 0) )); then
    err "Anomalie flags -e and -m must be non-negative."
    exit 1
fi
# Check if valid Serverless app directory.
readonly REL_APP_DIR="../../apps/${dflag}"
if [[ ! -d "${REL_APP_DIR}" ]]; then
    err "${dflag} is not an app directory name in ../../apps/."
    exit 1
fi
cd "${REL_APP_DIR}"
readonly APP_DIR="$(pwd)"
if [[ ! ( -e "serverless.yaml" ) ]]; then
    err "$(pwd) is missing serverless.yaml."
    exit 1
fi
# Check if Serverless CLI is installed.
if ! command -v serverless &> /dev/null; then
    err "Serverless Framework CLI is not installed (https://www.serverless.com/)."
    exit 1
fi
# Check if app dependencies are installed and install if necessary.
if ! command -v npm &> /dev/null; then
    err "npm is not installed (https://nodejs.org/en/)."
    exit 1
fi
#if ! npm ls --silent &> /dev/null; then 
#    echo "Dependencies in ${APP_DIR} not found. Installing ..."
if ! npm install; then
    echo "Unable to install dependencies in ${APP_DIR}."
    exit 1
fi
#fi
# Read OpenWhisk config and set respective environment variables.
cd ../../sampler
export OW_APIHOST="$(yaml config.yaml "['openwhisk']['host']")"
export OW_AUTH="$(yaml config.yaml "['openwhisk']['auth']")"
# Deploy app.
cd "${APP_DIR}"
if ! serverless deploy; then
    err "Unable to deploy app."
    exit 1
fi
# Send n requests to Serverless app.
cd ../../sampler
if ! python run.py -d "${dflag}" -n "${nflag}" -l "${lflag}" -u "${uflag}" -b "${bflag}" -w "${wflag}" -m "${mflag}" -e "${eflag}" -r "${rflag}"; then
    err "Unable to run requests."
    exit 1
fi
cd "${APP_DIR}"
if ! serverless remove; then
    err "Unable to remove app."
    exit 1
fi
echo "Success!"