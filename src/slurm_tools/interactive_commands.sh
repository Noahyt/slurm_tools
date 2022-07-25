#!/bin/bash


RequestBasicInstance() {
	TIME='4:00:00'
	MEMORY='4000'
	PARTITION='test'
	salloc -p ${PARTITION} --mem ${MEMORY} -t ${TIME}
}


PrepareToLaunchJobs() {
	module load Anaconda3
	source activate ${JOB_LAUNCH_ENV}
}
