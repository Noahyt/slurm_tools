"""Modules to build sbatch commands"""

from slurm_tools import csv_util

class Command(object):
    """Base class for sbatch file commands."""

    description=""

    def build_str(self, include_description=True):
        """Returns string representation of command."""
        command=[]
        if include_description:
            command.append(self.description_str())
        command.append(self.command_str())
        return "\n".join(command)

    def command_str(self):
        """`command_str` returns a list of command strings."""
        raise NotImplementedError

    def description_str(self):
        return f"# {self.description}"

class Comment(Command):
    """Add comment"""

    def __init__(self, text):
        self.text=text

    def build_str(self, **kwargs):
        """Override `build_str` since we never want a description."""
        return super().build_str(include_description=False)

    def command_str(self):
        return f"# {self.text}"

class BashCommand(Command):
    """A base class for bash commands."""

    def command_str(self):
        return f"{self.command_call} {self.command_arg}"


class Echo(BashCommand):
    """Prints text."""

    command_call="echo"

    def build_str(self, **kwargs):
        """Override `build_str` since we never want a description."""
        return super().build_str(include_description=False)

    def __init__(self, text):
        self.command_arg=text


class loadModule(Command):

    _MODULE_LOAD = "module load"

    def __init__(self, module: str):
        self.module=module
        self.description = f"load module {module}"

    def command_str(self):
        return f"{self._MODULE_LOAD} {self.module}"


class activateConda(BashCommand):

    def __init__(self):
        self.command_call = "eval"
        self.command_arg = "\"$(conda shell.bash hook)\""


class deactivateConda(BashCommand):
    command_call = "conda"
    command_arg = "deactivate"


class loadCondaEnv(BashCommand):

    def __init__(self, conda_env):
        self.command_call = "source activate"
        self.command_arg = conda_env


class SbatchCommand(Command):
    """A base class for building sbatch commands.

    An implementing class should set for each command:
        - `command_call`
        - `command_arg`

    Optionally, any help description.
    """

    _SBATCH_COMMAND="#SBATCH"

    def command_str(self):
         return f"{self._SBATCH_COMMAND} --{self.command_call}={self.command_arg}"


class JobNameCommand(SbatchCommand):
    command_call="job-name"
    description="Slurm job name."

    def __init__(self, name):
        self.name=name
        self.command_arg=self.name

class RunPythonScript(BashCommand):

    command_call="python -m"

    def __init__(self, job_script, job_args):
        self.job_script=job_script
        self.job_args=job_args
        self.command_arg = f"{self.job_script} {self.python_command_arg(self.job_args)}"

    def python_command_arg(self, job_args):
        """Creates argument for python script."""
        return csv_util.dict_to_CLI_args(job_args)


class MailAddressCommand(SbatchCommand):
    """Emails status of job."""

    command_call="mail-user"
    description="Set email address for update."

    def __init__(self, email, mail_type="FAIL"):
        self.email=email
        self.command_arg=self.email


class MailTypeCommand(SbatchCommand):
    """Emails status of job."""

    command_call="mail-type"
    description="Notify user by email at given status."

    def __init__(self, mail_type="FAIL"):
        self.mail_type=mail_type
        self.command_arg=self.mail_type


class STDOUTCommand(SbatchCommand):
    """Sets location to save STDOUT."""
    command_call="output"
    description="Set file for `stdout`."

    def __init__(self, output_directory):
        self.output_directory=output_directory
        self.command_arg=f"{self.output_directory}/output.txt"


class STDERRCommand(SbatchCommand):
    """Sets location to save STDERR."""
    command_call="error"
    description="Set file for `stderr`."

    def __init__(self, output_directory):
        self.output_directory=output_directory
        self.command_arg=f"{self.output_directory}/error.txt"


class PartitionCommand(SbatchCommand):
    """Sets partition on which to run job."""
    command_call="partition"
    description="Set partition for job" 

    def __init__(self, partition="shared"):
        self.partition = partition
        self.command_arg=self.partition


class TimeCommand(SbatchCommand):
    """Sets partition on which to run job."""
    command_call="time"
    description="Set total run time for job" 

    def __init__(self, time):
        self.time = time
        self.command_arg=self.time


class NTaskCommand(SbatchCommand):
    """Sets number of tasks requested.
    The default is for 1 cpu per task, so for simple jobs this is equivalent to setting
    the number of CPUs.
    """
    command_call="ntasks"
    description="Set number of requeted tasks (default 1 cpu/task)." 

    def __init__(self, task_count):
        self.task_count = task_count
        self.command_arg=self.task_count


class MemoryPerCpuCommand(SbatchCommand):
    """Sets partition on which to run job."""
    command_call="mem-per-cpu"
    description="Set memory for each cpu in job" 

    def __init__(self, mem_per_cpu):
        self.mem_per_cpu = mem_per_cpu
        self.command_arg=self.mem_per_cpu
