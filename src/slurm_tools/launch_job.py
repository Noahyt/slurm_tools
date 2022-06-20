"""Base script to launches Slurm Jobs."""

from slurm_tools import sbatch_command as scommand

from pathlib import Path
import os
import time

_TEST_RUN_COMMAND="cat"
_RUN_COMMAND="sbatch"
_DEFAULT_PARTITION="shared"
_SBATCH_FILE_NAME="sbatch.txt"


class JobLauncher(object):
    """`JobLauncher` allows user to create and launch slurm jobs"""

    def __init__(
        self,
        job_name: str,
        sbatch_file_name: str=_SBATCH_FILE_NAME,
        job_output_directory: str=None,
        include_time_in_job_directory: bool=True,
        verbose: bool=False,
        **kwargs,
    ):
        """"Initializes `JobLauncher` and creates output directories."""
        self.sbatch_commands=[]
        self.pre_commands=[]
        self.job_commands=[]
        self.post_commands=[]
        self.sbatch_file_name=sbatch_file_name
        self.job_output_directory=self._initialize_job_output_directory(job_output_directory)
        self.job_name = job_name
        self.sbatch_commands.append(scommand.JobNameCommand(self.job_name))
        self.job_directory = self._initialize_output_dirs(self.job_output_directory, self.job_name, include_time_in_job_directory)
        self.sbatch_commands.append(scommand.STDERRCommand(self.job_directory))
        self.sbatch_commands.append(scommand.STDOUTCommand(self.job_directory))
        self.verbose=verbose
        if verbose or self.verbose:
            self.sbecho(self.sbatch_commands, "CURRENT DIRECTORY ${PWD}")
            self.sbecho(self.sbatch_commands, f"JOB OUTPUT DIRECTORY {job_output_directory}")
            self.sbecho(self.sbatch_commands, "JOB RUNNING ON ${srun hostname}")


    def set_sbatch_commands(
        self,
        time=None,
        cpu_count=None,
        mem_per_cpu=None,
        partition=None,
        output_directory=None,
        mail_address=None,
        mail_type=None,
        verbose=False,
        **kwargs,
    ):
        """Assembles sbatch commands."""
        self.sbatch_commands.append(scommand.Comment("COMPUTE RESOURCES"))
        self.sbatch_commands.append(scommand.TimeCommand(time))
        if mail_address is not None:
            self.sbatch_commands.append(scommand.MailAddressCommand(mail_address))
        if mail_type is not None:
            self.sbatch_commands.append(scommand.MailTypeCommand(mail_type))
        if partition is not None:
            self.sbatch_commands.append(scommand.PartitionCommand(partition))
        if cpu_count is not None:
            self.sbatch_commands.append(scommand.CPUCountCommand(cpu_count))
        if mem_per_cpu is not None:
            self.sbatch_commands.append(scommand.MemoryPerCpuCommand(mem_per_cpu))
        if verbose or self.verbose:
            self.sbecho(self.sbatch_commands, "JOB ID ${SLURM_JOB_ID}")

    def set_post_commands(
        verbose=False,
    ):
        """Commands to run after core job."""
        if verbose or self.verbose:
            self.sbecho(self.post_commands, "FINISHED.")


    def sbecho(self, command_list, echo_text):
        """Convenience fn to add specified `echo` to sbatch commands."""
        command_list.append(scommand.Echo(echo_text))

    def set_job_commands(
        self,
        verbose=False,
    ):
        """Assembles commands to run job.""" 

    def run(self, test=False):
        """Runs job as specified, creating output folders and saving script."""
        self.sbatch_file = self._write_sbatch(self.job_directory, self.sbatch_file_name)        
        self._call_sbatch(self.sbatch_file, test)
        self._has_run=True

    def build_sbatch(self):
        """Creates `sbatch` string."""
        sbatch_text = []

        sbatch_text.append("#!/bin/bash")

        for c in self.sbatch_commands:
            sbatch_text.append(c.build_str(include_description=self.verbose))

        for c in self.pre_commands:
            sbatch_text.append(c.build_str(include_description=self.verbose))

        for c in self.job_commands:
            sbatch_text.append(c.build_str(include_description=self.verbose))

        for c in self.post_commands:
            sbatch_text.append(c.build_str(include_description=self.verbose))

        return "\n".join(sbatch_text)

    def _initialize_output_dirs(
        self,
        job_output_directory,
        job_name,
        include_time_in_job_directory
    ):
        """Initializes output directory for job."""
        output_folder_name = job_name
        if include_time_in_job_directory:
            t = time.time()
            output_folder_name = f"{output_folder_name}_{time.strftime('%Y_%m_%d_%H_%M_%Z', time.localtime(t))}"
        output_directory = job_output_directory.joinpath(output_folder_name)
        self._initialize_folder(output_directory)
        return output_directory

    def _initialize_job_output_directory(self, job_output_directory):
        """Initializes job directory."""
        job_output_directory=Path(job_output_directory)
        self._initialize_folder(job_output_directory)
        return job_output_directory

    def _initialize_folder(self, folder):
        """Initializes directory for sbatch, stdout/stderr."""
        folder.mkdir(parents=True, exist_ok=True)

    def _write_sbatch(self, output_directory, sbatch_file_name):
        """Creates and writes sbatch file to `job_directory`."""
        sbatch_text = self.build_sbatch()
        sbatch_file = output_directory.joinpath(sbatch_file_name)
        with sbatch_file.open('w') as f:
            f.write(sbatch_text)
        return sbatch_file

    def _sbatch_text(self):
        """Creates sbatch text."""
        pass
        

    def _call_sbatch(self, sbatch_file: Path, test=False):
        """Launches job on slurm."""
        if test:
            run_command=_TEST_RUN_COMMAND
        else:
            run_command=_RUN_COMMAND
        bash_str = f"{run_command} {sbatch_file}"
        os.system(bash_str)


