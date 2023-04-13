import os
import subprocess


class Command:
    def __init__(self) -> None:
        pass

    def run(self, arg_list) -> tuple:
        proc = subprocess.Popen(arg_list,
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
    