import os
import subprocess

from clava import exec

class Command:
    def __init__(self, source_path: str, output_path: str, ntry: int, flag: str) -> None:
        self.transpiler = str(os.sys.argv[2]).lower()

        if self.transpiler == 'clava':
            self.args = exec.clava(source_path, output_path, flag, ntry)

    def run(self) -> tuple:
        proc = subprocess.Popen(self.args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        proc.wait()

        stdout, stderr = proc.communicate()

        return proc.returncode, stdout, stderr
    
    def diff(self, file1, file2):
        return self.run(["diff", file1, file2])
    
    def clang(self, source_path, output_path):
        return self.run(["clang", "-S", "-O0", "-emit-llvm", source_path, "-o", output_path])
