# slurm_tools
Basic tools for running slurm jobs.


## Launch Python Job from Script.

To launch a python job using a set of different parameters use `launch-python-job-csv`.

Explicitly:

```
   # Launch a interactive job.
   $ salloc -p test --mem 4000 -t 4:00:00 
   # Load Python and an enviroment in which this tool is installed.
   $ ml Anaconda3
   $ source activate CONDA_ENV
   # Launch job.
   $ launch-python-job-array \
      --env_name ENV_NAME \
      --script PATH_TO_SCRIPT \
      --slurm_args_file PATH_TO_SLURM_ARGS \
      --script_args PATH_TO_SCRIPT_ARGS
```

The `--test` flag will write an `sbatch` file but not submit it to the queue.

## Random notes on `slurm`.

  - When the `sbatch` script is run, slurm invokes a new non-interactive bash instance to handle input. This instance is associated with the user, such that [`.bashrc`](https://linuxize.com/post/bashrc-vs-bash-profile/) is loaded and the script will have access to any aliases/etc. that are created by the user.
