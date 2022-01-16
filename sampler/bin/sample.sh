#!/bin/bash

err() {
  echo "Error: $*" >&2
}

float_le_op() {
    echo "$(echo "$1 <= $2" | bc)"
}

yaml() {
    python -c "import yaml; print(yaml.safe_load(open('$1'))$2)"
}

dflag=''
n1flag=''
l1flag=''
u1flag=''
n2flag=0
l2flag=-1
u2flag=-1
rflag=0
eflag=0
mflag=0

while :; do
  case $1 in
    -d)
        dflag=$2
        shift
        ;;
    -n1)
        n1flag=$2
        shift
        ;;
    -l1)
        l1flag=$2
        shift
        ;;
    -u1)
        u1flag=$2
        shift
        ;;
    -n2)
        n2flag=$2
        shift
        ;;
    -l2)
        l2flag=$2
        shift
        ;;
    -u2)
        u2flag=$2
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
echo "d: ${dflag}"
echo "n1: ${n1flag}"
echo "l1: ${l1flag}"
echo "u1: ${u1flag}"
echo "n2: ${n2flag}"
echo "l2: ${l2flag}"
echo "u2: ${u2flag}"
echo "r: ${rflag}"
echo "e: ${eflag}"
echo "m: ${mflag}"
# Check if all arguments are given.
if (( "${#dflag}" <= 0 || "${#n1flag}" <= 0 || "${#l1flag}" <= 0 || "${#u1flag}" <= 0 )); then
    err "App directory name (flag: -d), number of traces (flag: -n1), lower bound (flag: -l1), or upper bound (flag: -u1) is missing."
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
if ! python run.py -d "${dflag}" -n1 "${n1flag}" -l1 "${l1flag}" -u1 "${u1flag}" -n2 "${n2flag}" -l2 "${l2flag}" -u2 "${u2flag}" -m "${mflag}" -e "${eflag}" -r "${rflag}"; then
    err "Unable to run requests."
    exit 1
fi
cd "${APP_DIR}"
if ! serverless remove; then
    err "Unable to remove app."
    exit 1
fi
echo "Success!"