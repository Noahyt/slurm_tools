#!/bin/bash

EXPERIMENT_NAME=${1}
shift

READ_OUTPUT=false
READ_ERROR=false
READ_SBATCH=false


while [[ $# -gt 0 ]]
do
key="$1"
echo key
case $key in
	-o|--output)
		READ_OUTPUT=true
	;;
	-e|--error)
		READ_ERROR=true
	;;
	-s|--sbatch)
		READ_SBATCH=true
	;;
esac
shift
done

JOB_FOLDER=${JOB_LOGS}/${EXPERIMENT_NAME}

if [ "$READ_OUTPUT" = true ]; then
	cat ${JOB_FOLDER}/*output.txt
fi

if [ "$READ_ERROR" = true ]; then
	cat ${JOB_FOLDER}/*error.txt
fi

if [ "$READ_SBATCH" = true ]; then
	cat ${JOB_FOLDER}/sbatch_file.txt 
fi
