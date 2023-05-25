import os
import time
import difflib

from modules.exception import CorrectnessException
from modules.command import *


LLVM_O0 = str('-O0')
LLVM_O2 = str('-O2')
LLVM_O3 = str('-O3')


class CorrectnessHandler:
    def __init__(self, params: dict) -> None:
        self.source_path = params["source_path"]
        self.output_path = params["output_path"]
        self.opt = params["opt"]
        self.vc = params["vc"]

    def strip_ir(self, ir: str) -> str:
        ir_file = open(ir, 'r')

        lines = []

        readline = ir_file.readline()

        while 'target triple' not in readline:
            readline = ir_file.readline()

            continue

        line = ''

        while True:
            if not line:
                break

            if line.startswith("!"):
                continue
            
            line = ir_file.readline()

            lines.append(line)

        return ''.join(lines)

    def run(self) -> None:
        start = time.time()

        gen_path = os.path.join(self.output_path, 'src.cpp')
        
        ir_from_src = os.path.join(self.output_path, 'src.ll')
        ir_from_gen = os.path.join(self.output_path, 'gen.ll')

        src_ir_cmd = Command(emit_llvm(self.source_path, ir_from_src, '-' + self.opt))
        gen_ir_cmd = Command(emit_llvm(gen_path, ir_from_gen, '-' + self.opt))

        src_proc_code, _, _ = src_ir_cmd.run()
        gen_proc_code, _, _ = gen_ir_cmd.run()

        end = time.time()

        elapsed = round(end - start, 3)

        # emit_llvm failed to execute
        if (src_proc_code != 0) or (gen_proc_code != 0):
            print("emit_llvm failed to execute")
            return False, elapsed
        
        stripped_src_ir = self.strip_ir(ir_from_src)
        stripped_gen_ir = self.strip_ir(ir_from_gen)

        success = stripped_src_ir == stripped_gen_ir

        return success, elapsed
