import os
import subprocess

from clava import exec

class Command:
    def __init__(self, params: dict) -> None:
        self.transpiler = str(os.sys.argv[2]).lower()
        self.params = params
        
        if self.transpiler == 'clava':
            self.cmd = exec.clava(self.params)

    def run(self) -> tuple:
        proc = subprocess.Popen(self.cmd,
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
