#!/bin/bash
sbatch_setup_commands="# Additional setup commands."

## JOB SPECIFICATIONS.
job_name=update_conda
now=$(date +"%FT%H%M%S")
job_directory=${HOME}/job_logs/${now}_${job_name}

## JOB RUNTIME SPECIFICATIONS
time='1:00:00'
partition=shared # Default partition.
gpu_count=0
mempercpu='4G'

## GET INPUTS.
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

## OVERRIDE DEFAULTS WITH PASSED PARAMETERS
case $key in
    -h|-\?|--help)
        Help.
    ;;
    -n|--job_name)
        if [ ! -z "$2" ]; then
            job_name=$2
            shift
        else
        echo 'ERROR: "--job_name" requires a non-empty option argument.'
        exit 1
        fi
    ;;
    -n|--job_name)
        if [ ! -z "$2" ]; then
            job_name=$2
            shift
        else
        echo 'ERROR: "--job_name" requires a non-empty option argument.'
        exit 1
        fi
    ;;
    -t|--time)
        if [ ! -z "$2" ]; then
            time=$2
            shift
        else
        echo 'ERROR: "--time" requires a non-empty option argument.'
        exit 1
        fi
    ;;
    -m|--mempercpu)
        if [ ! -z "$2" ]; then
            mempercpu=$2
            shift
        else
        echo 'ERROR: "--mempercpu" requires a non-empty option argument.'
        exit 1
        fi
    ;;
    --env_name)
        if [ ! -z "$2" ]; then
            ENV_NAME=$2
            shift
        else
            echo 'ERROR: "--env_name" requires a non-empty option argument.'
            exit 1
        fi
    ;;
esac
shift
done

if [ $gpu_count -gt 0 ]; then
    partition='gpu'
    sbatch_setup_commands+=$'\n'"#SBATCH --gres gpu:${gpu_count}"
fi

## SET UP JOB DIRECTORIES.
if [ ! -d ${job_directory} ]; then
  # If directory does not exist, then creates it.
  echo "Job directory does not exist. Making: ${job_directory}"
  mkdir -p ${job_directory}
fi

export JOB_DIRECTORY=${job_directory}

SBATCH_FILE="${job_directory}/sbatch_file.txt"

## CONSTRUCT SBATCH FILE
/bin/cat <<EOT >${SBATCH_FILE}
#!/bin/bash
## JOB SUBMITTED AT ${now}
## NAME
#SBATCH --job-name=${job_name}
## NOTIFICATION
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=toyonaga@g.harvard.edu
# A file for STDOUT from job.
#SBATCH --output="${job_directory}/%a_output.txt"
# A file for STDERR from job.
#SBATCH --error="${job_directory}/%a_error.txt"
##  RUNTIME RESOURCES.
# Note that if gpu's are requested, the call to gres is included in
# the appended 'sbatch_setup_commands'.
#SBATCH --partition=${partition}
#SBATCH --time=${time}
#SBATCH -n 1
#SBATCH --mem-per-cpu ${mempercpu}
$sbatch_setup_commands
echo "JOB ID \${SLURM_JOB_ID}"
echo "Current directory"
echo \$PWD
## SETTING UP CONDA ENVIRONMENT
module load Anaconda3
# Confirm python loading.
echo python: \$(which python)
echo "finished loading"
# Activate conda environment.
eval "\$(conda shell.bash hook)"

conda update -y -n base -c defaults conda

echo "Finished."
srun hostname
EOT

## SUBMIT SBATCH.
sbatch ${SBATCH_FILE}
