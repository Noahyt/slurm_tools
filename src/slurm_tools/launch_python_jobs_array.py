"""Launches a set of jobs parameterized by csv arrays."""

import argparse
import json
from pathlib import Path
import time

from slurm_tools import launch_python_job
from slurm_tools import csv_util


def launch_conda_jobs_csv(
    job_name, job_output_directory, env_name, script, script_args, slurm_args, test
):
    """Launches a set of slurm jobs parameterized by csv files for script args and slurm parameters."""
    # Load args.
    script_args = csv_util.parse_csv(script_args)

    # If `test` run only two.
    if test:
        script_args = script_args[:2]

    # TODO: replace this with a nicer scheme that incorporates the subfolders as a fn of `JobLauncher`
    # We want to put all the output logs under a single folder.
    # To do this, set the `job_output_folder` to include the `job_name` and then 
    # have `JobLauncher` create subdirectories associated with `experiment_id`.
    t = time.time()
    output_folder_name = f"{time.strftime('%Y_%m_%d_%H_%M_%Z', time.localtime(t))}_{job_name}"
    job_output_directory = job_output_directory.joinpath(output_folder_name)

    # Iterate over jobs.
    for script_arg_job in script_args:
        # We want to set the `job_name` to be associated with the given experiment.
        experiment_id = script_arg_job.pop("experiment_id")
        job_name_ex = f"{job_name}_id_{experiment_id}"

        launch_python_job.launch_conda_job(
            job_name=job_name_ex,
            job_output_directory=job_output_directory,
            env_name=env_name,
            script=script,
            script_args=script_arg_job,
            slurm_args=slurm_args,
            test=test,
        )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_name", default=None)
    parser.add_argument(
        "--job_output_directory", default=Path.home().joinpath("job_logs")
    )
    parser.add_argument("--env_name")
    parser.add_argument("--script", type=str)
    parser.add_argument("--script_args", type=str)
    # Create set of option for `slurm_args`.
    slurm_args_group = parser.add_mutually_exclusive_group()
    slurm_args_group.add_argument("--slurm_args", type=json.loads)
    slurm_args_group.add_argument("--slurm_args_file", type=str)
    parser.add_argument("--test", action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


def main():
    """Launches script using configuration files for slurm configuration and arguments."""
    args = parse_args()
    script = Path(args.script)
    script_args = Path(args.script_args)

    if args.job_name is None:
        job_name=f"{script.suffix[1:]}_{script_args.stem}"
    else:
        job_name = args.job_name

    # Parse slurm args.
    if args.slurm_args_file is not None:
        # The output of the csv parser is a list of dictionaries. we take the first entry as the
        # args for all experiments in this job.
        slurm_args = csv_util.parse_csv(args.slurm_args_file)[0]
    else:
        slurm_args = args.slurm_args

    if args.test:
        print(f"slurm args: {slurm_args}")

    job_output_directory = Path(args.job_output_directory)
    launch_conda_jobs_csv(
        job_name=job_name,
        job_output_directory=job_output_directory,
        env_name=args.env_name,
        script=script,
        script_args=script_args,
        slurm_args=slurm_args,
        test=args.test,
    )


if __name__ == "__main__":
    main()
