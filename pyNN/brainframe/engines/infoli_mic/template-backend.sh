#!/bin/bash

echo ""
echo "Running job with the infoli simulator on Xeon Phi KNC..."

USER=georgec
MIC_IP=172.31.1.1

# Check for card detection
if ! ping -c 1 -w 5 "${MIC_IP}" &>/dev/null ; then 

  echo "MIC card nowhere to be found. (tried IP ${MIC_IP})"
  exit 1

else 

  echo "MIC found!"

fi

# Get the Directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIN_DIR=${SCRIPT_DIR}
CUR_DIR=$(pwd)
BASE_DIR=$(dirname $SCRIPT_DIR)
HOME="$(getent passwd $USER | awk -F ':' '{print $6}')"
DOCKER_HOME=/app

mkdir -p "$CUR_DIR/brainframe-res"
cd brainframe-res
CUR_DIR="$CUR_DIR/brainframe-res"

DATE=`date +%T`
DNAME="exp"_$DATE

echo $BIN_DIR

# Thread options
THREADSNUM=200

# Experiment variables
SIZE=100
PROB=0.2
STIME=10

while [[ $# -gt 1 ]]
do
    key="$1"

    case $key in
        -dir|-working_dir)
            DNAME="$2"
            shift # past argument
            ;;
        -ns|-net_size)
            SIZE="$2"
            shift # past argument
            ;;
        -pb|-probability)
            PROB="$2"
            shift # past argument
            ;;
        -st|-sim_time)
            STIME="$2"
            shift # past argument
            ;;
        -th|-threads)
            THREADSNUM="$2"
            shift # past argument
            ;;

        *)
            # unknown option
            echo "Invalid argument: $1"
            exit 1
    esac
    shift # past argument or value
done

# Set Up MIC for conducting the experiment
ssh -oStrictHostKeyChecking=no -i ${SCRIPT_DIR}/mic.key $USER@${MIC_IP} "mkdir $DNAME"
scp -oStrictHostKeyChecking=no -i ${SCRIPT_DIR}/mic.key ${SCRIPT_DIR}/default.conf ${SCRIPT_DIR}/infoli.x ${SCRIPT_DIR}/libiomp5.so $USER@${MIC_IP}:~/$DNAME

# Create a folder to receive results on host
echo ""
echo "SIZE= ${SIZE}|Density= ${PROB}|Simtime= ${STIME}|DNameP:$DNAME"
mkdir -p $CUR_DIR/$DNAME

# Prepare the Job's Command
MYJOB="ssh -oStrictHostKeyChecking=no -i ${SCRIPT_DIR}/mic.key $USER@${MIC_IP} \"export LD_LIBRARY_PATH=~/$DNAME:${LD_LIBRARY_PATH}; export OMP_NUM_THREADS=$THREADSNUM; export KMP_AFFINITY=balanced; export KMP_PLACE_THREADS=57c,4t; cd $DNAME; ./infoli.x -n ${SIZE} -p ${PROB} -t ${STIME};\""
echo $MYJOB
cd ${DNAME}

# Execute the Command and Retrieve Results
#${MYJOB}
ssh -oStrictHostKeyChecking=no -i ${SCRIPT_DIR}/mic.key $USER@${MIC_IP} "export LD_LIBRARY_PATH=~/$DNAME:${LD_LIBRARY_PATH}; export OMP_NUM_THREADS=$THREADSNUM; export KMP_AFFINITY=balanced; export KMP_PLACE_THREADS=57c,4t; cd $DNAME; ./infoli.x -n ${SIZE} -p ${PROB} -t ${STIME};"
echo "Job Finished on MIC, retrieving results..."
scp -i ${SCRIPT_DIR}/mic.key $USER@${MIC_IP}:~/$DNAME/InferiorOlive_Output.txt .

echo ""
echo "Simulation Finished, results in \"$CUR_DIR/$DNAME/\" folder."
echo "-----------------------------------"

echo "Everything ok!"

