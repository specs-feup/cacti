import subprocess

from clava import exec
from modules.exception import InvalidTranspiler


def diff(file1: str, file2: str) -> list:
    return ["diff", file1, file2]


def emit_llvm(source: str, output: str, o_flag: str) -> list:
    return ["clang", "-S", source, "-emit-llvm", o_flag, "-o", output]


def transpiler_cmd(transpiler: str, params: dict) -> list:
    if transpiler == 'clava':
        return exec.clava(params)

    raise InvalidTranspiler('Invalid transpiler')


class Command:
    def __init__(self, args: str) -> None:
        self.args = args

    def run(self) -> tuple:
        proc = subprocess.Popen(self.args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        proc.wait()

        stdout, stderr = proc.communicate()

        return proc.returncode, stdout, stderr
