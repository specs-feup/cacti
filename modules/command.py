import subprocess

from clava import exec
from modules.exception import InvalidTranspiler


def diff(file1: str, file2: str) -> list:
    """Compute the arguments for the `diff` command to be executed on two files.

    Args:
        file1 (str): The path to the first file.
        file2 (str): The path to the second file.

    Returns:
        list: A list containing the arguments for this command.
    """
    return ["diff", file1, file2]


def emit_llvm(source: str, output: str, o_flag: str) -> list:
    """Computes the arguments for the `emit_llvm` command.

    Args:
        source (str): The path of the file.
        output (str): The path of the output folder, to where the IR file (.ll) will be written into.
        o_flag (str): The optimization flag to be used by this command.

    Returns:
        list: A list containing the arguments for this command.
    """
    return ["clang", "-S", source, "-emit-llvm", o_flag, "-o", output]

def transpiler_cmd(transpiler: str, params: dict) -> list:
    """Computes the arguments for the command that launches the transpiler subprocess.
    
    Args:
        transpiler (str): The name of the transpiler that will be launched.
        params (dict): Parameters that each transpiler must oblige to in order to properly execute tests.
    
    Returns:
        list: A list containing the arguments for this command.

    Raises:
        InvalidTranspiler: If the transpiler is invalid.
    """
    if transpiler == 'clava':
        return exec.clava(params)

    raise InvalidTranspiler('Invalid transpiler: ' + transpiler)


class Command:
    """Module responsible for executing commands.

    Attributes:
        args (list): The list of arguments of the command to execute.
    """
    def __init__(self, args: list) -> None:
        """Initialize the Command instance.

        Attributes:
            args (list): The value for args.
        """        
        self.args = args

    def run(self) -> tuple:
        """Execute the desired command.

        Returns:
            tuple: A 3-element tuple containg the process return code, the content of STDOUT, and the content of STDERR.
        """
        proc = subprocess.Popen(self.args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        proc.wait()

        stdout, stderr = proc.communicate()

        return proc.returncode, stdout, stderr
