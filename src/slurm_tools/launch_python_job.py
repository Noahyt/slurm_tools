"""Launches Python Job on Slurm."""

import argparse
import json
from pathlib import Path

from slurm_tools import launch_job
from slurm_tools import sbatch_command as scommand


_CONDA3 = "ANACONDA3"
_CONDA3_MODULE = "Anaconda3"


class CondaJobLauncher(launch_job.JobLauncher):
    """Slurm job with Conda prerequisite."""
    
    def __init__(
        self,
        env_name,
        conda_ver=_CONDA3,
        **kwargs,
    ):
        self.env_name = env_name
        self.conda_ver = conda_ver
        if self.conda_ver==_CONDA3:
            self.conda_module = _CONDA3_MODULE
        super().__init__(**kwargs)

        # Load.
        self.set_pre_commands()

    def set_pre_commands(
        self,
    ):
        """Loads anaconda and sources environment provided at initialization."""
        if self.verbose:
            self.sbecho(self.pre_commands, "LOADING CONDA ENV.")

        self.pre_commands.append(scommand.Comment("CONDA ENVIRONMENT."))
        self.pre_commands.append(scommand.loadModule(self.conda_module))
        self.pre_commands.append(scommand.activateConda())
        self.pre_commands.append(scommand.loadCondaEnv(self.env_name))
        if self.verbose:
            self.sbecho(self.pre_commands, "python: $(which python)")

    @classmethod
    def from_arg_dict(cls, slurm_args):
        """Initializes `CondaJobLauncher` from dictionary of parameters."""
        jl = cls(**slurm_args)
        jl.set_sbatch_commands(**slurm_args)
        return jl

    def set_job_commands(
        self,
        job_script: str,
        job_args: dict,
    ):
        self.job_commands.append(scommand.Comment("RUN PYTHON SCRIPT"))
        if self.verbose:
            self.sbecho(self.pre_commands, "RUNNING SCRIPT.")

        self.job_commands.append(
            scommand.RunPythonScript(job_script, job_args))


# TODO: allow different number of experiment and slurm params.
def launch_conda_job(
    job_name: str,
    job_output_directory: Path,
    env_name: str,
    script: Path,
    script_args: dict,
    slurm_args: dict,
    test: bool=False,
    verbose: bool=True,
):
    """Launches a set of slurm jobs parameterized by csv files for script args and slurm parameters."""
    jl = CondaJobLauncher(
        env_name = env_name,
        job_name=job_name,
        job_output_directory=job_output_directory,
        verbose=verbose
    ) 
    jl.set_sbatch_commands(**slurm_args)
    jl.set_job_commands(script, script_args)
    jl.run(test=test)


# TODO: load from env variable.
# TODO: option to provide script and slurm arguments as str in command line prompt.
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job_name', default="sbatch-job")
    parser.add_argument('--job_output_directory', default=Path.home().joinpath("job_logs"))
    parser.add_argument('--env_name')
    parser.add_argument('--script', type=str)
    parser.add_argument('--script_args', type=json.loads)
    parser.add_argument('--slurm_args', type=json.loads)
    parser.add_argument(
        '--test', action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


def main():
    """Launches script using configuration files for slurm configuration and arguments."""
    args = parse_args()
    script = Path(args.script)
    job_output_directory = Path(args.job_output_directory)
    launch_conda_job(
        job_name = args.job_name,
        job_output_directory=job_output_directory,
        env_name=args.env_name,
        script=args.script,
        script_args=args.script_args,
        slurm_args=args.slurm_args,
        test=args.test,
    ) 

if __name__ == "__main__":
    main()
