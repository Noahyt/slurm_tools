"""Launches a set of jobs parameterized by csv arrays."""

import argparse
from pathlib import Path

from slurm_tools import launch_python_job
from slurm_tools import csv_util


def launch_conda_jobs_csv(
    job_name, job_output_directory, env_name, script, script_args, slurm_args, test
):
    """Launches a set of slurm jobs parameterized by csv files for script args and slurm parameters."""
    # Load args.
    script_args = csv_util.parse_csv(script_args)
    slurm_args = csv_util.parse_csv(slurm_args)

    # Check that there are a compatible number of experiments in slurm and script arg files.
    if len(script_args) != len(slurm_args):
        raise ValueError(
            "Must have same number of lines (each coresponding to one experiment) in `script_args` and `slurm_args`."
        )

    # Iterate over jobs.
    for slurm_arg_job, script_arg_job in zip(script_args, slurm_args):
        launch_python_job.launch_conda_job(
            job_name=job_name,
            job_output_directory=job_output_directory,
            env_name=env_name,
            script=script,
            script_args=script_arg_job,
            slurm_args=slurm_arg_job,
            test=test,
        )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_name", default="sbatch-job")
    parser.add_argument(
        "--job_output_directory", default=Path.home().joinpath("job_logs")
    )
    parser.add_argument("--env_name")
    parser.add_argument("--script", type=str)
    parser.add_argument("--script_args", type=str)
    parser.add_argument("--slurm_args", type=str)
    parser.add_argument("--test", action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


def main():
    """Launches script using configuration files for slurm configuration and arguments."""
    args = parse_args()
    script = Path(args.script)
    script_args = Path(args.script_args)
    slurm_args = Path(args.slurm_args)
    job_output_directory = Path(args.job_output_directory)
    launch_conda_jobs_csv(
        job_name=args.job_name,
        job_output_directory=job_output_directory,
        env_name=args.env_name,
        script=script,
        script_args=script_args,
        slurm_args=slurm_args,
        test=args.test,
    )


if __name__ == "__main__":
    main()
