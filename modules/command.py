import os
import subprocess

from clava import exec

class Command:
    def __init__(self, params: dict) -> None:
        self.transpiler = str(os.sys.argv[2]).lower()
        self.params = params
        self.cmd = ''
        
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
    
    def emit_llvm(self, source_path: str, output_path: str, o_flag: str) -> list:
        return ["clang", "-S", source_path, "-emit-llvm", o_flag, "-o", output_path]
