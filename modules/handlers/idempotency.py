import os
import time

from exception import IdempotencyException
from modules.command import *



class IdempotencyHandler:
    def __init__(self, output_path: str, params: dict) -> None:
        self.params = params
        self.output_path = output_path
        self.transpiler = os.argv[2]
        self.curr_try = 0

    def get_filename(self) -> str:
        if self.curr_try == 0:
            return 'src.cpp'
        
        return 'gen' + str(self.curr_try) + '.cpp'
    
    def iteration(self) -> tuple:
        start = time.time()

        src = os.path.join(self.output_path, self.get_filename())

        self.curr_try += 1

        args = transpiler_cmd(self.transpiler, self.params)

        cmd = Command(args)

        _, stdout, stderr = cmd.run()

        gen = os.path.join(self.output_path, self.get_filename())

        if not os.path.isfile(gen):
            raise OSError(f"Error: the file {gen} could not be found!")

        end = time.time()
        
        return stdout, stderr, src, gen, round(end - start, 3)

    def run() -> None:
        pass
