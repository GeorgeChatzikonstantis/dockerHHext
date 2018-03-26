#!/bin/bash

echo "Runs a job with the infoli simulator from current Directory."
echo "It creates a new folder or a given folder outputs the results there"
echo "Parameters: -dir <dir to put results> -net_size <network size>" 
echo "-probability <network density> -sim_time <simulation time> -threads <threads num>"
echo "If no argument is given it runs on default values!"

# Get the Directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIN_DIR=${SCRIPT_DIR}
CUR_DIR=$(pwd)
BASE_DIR=$(dirname $SCRIPT_DIR)
HOME="$(getent passwd $USER | awk -F ':' '{print $6}')"

if [ "$CUR_DIR" == "$HOME" ]
then
    mkdir -p "$CUR_DIR/brainframe-res"
    cd brainframe-res
    CUR_DIR="$CUR_DIR/brainframe-res"
fi

DATE=`date +%T`
DNAME="exp"_$DATE

echo $SCRIPT_DIR
echo $BIN_DIR
echo $CUR_DIR
echo $HOME
echo $DNAME

# Thread options
THREADSNUM=4

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

echo "SIZE= ${SIZE}|Density= ${PROB}|Simtime= ${STIME}|Threads=$THREADSNUM DNameP:$DNAME"
mkdir -p $CUR_DIR/$DNAME

MYJOB="${BIN_DIR}/infoli.x -n ${SIZE} -p ${PROB} -t ${STIME}"
echo $MYJOB

export KMP_AFFINITY=balanced;
export KMP_PLACE_THREADS=4c,1t;
export OMP_NUM_THREADS=$THREADSNUM;
cd ${DNAME}
${MYJOB}

echo "Simulation Finished, results in \"$CUR_DIR/$DNAME/\" folder."
echo "-----------------------------------"

echo "Everything ok!"

