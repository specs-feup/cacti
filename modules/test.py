import os
import sys
import json
import time
import filecmp

from modules import command

from colorama import Fore

# Constants that represent Keys in the output JSON

TEST_PARSING = str('test_parsing')
TEST_CODEGEN = str('test_code_generation')
TEST_IDEMPOTENCY = str('test_idempotency')
TEST_CORRECTNESS = str('test_correctness')
SUCCESS = str('success')
LOG = str('log')
SRC = str('src')
GEN = str('gen')
EQUALS = str('equals')
TIME = str('time')
RESULTS = str('results')


# Constants that represent Keys in the parameters dictionary

PARAMS_FILE = str("file")
PARAMS_OUTPUT_FOLDER = str("output_folder")
PARAMS_CURR_TRY = str("curr_try")
PARAMS_DEBUG = str("debug_mode")


# Success and Error messages

MSG_SUCCESS = f"{Fore.GREEN}{'SUCCESS'}{Fore.RESET}"
MSG_ERROR = f"{Fore.RED}{'ERROR'}{Fore.RESET}"
MSG_NA = str('N/A')

IDEMPOTENCY_DEPTH = int(5)


# Debug modes

DEBUG_ON = str(True)
DEBUG_OFF = str(False)


# Clang LLVM Flags

LLVM_O0 = str('-O0')
LLVM_O2 = str('-O2')
LLVM_O3 = str('-O3')


PREFIX_IR_METADATA = '!'


class Test:
    def __init__(self, source_path: str, output_path: str, curr_try: int) -> None:
        self.source_path = source_path
        self.output_path = output_path
        self.curr_try = curr_try
        
        self.cmd = command.Command({
            PARAMS_FILE : self.source_path,
            PARAMS_OUTPUT_FOLDER : self.output_path,
            PARAMS_CURR_TRY : str(self.curr_try),
            PARAMS_DEBUG : DEBUG_OFF
        })
        
        self.results = dict()

    def __str__(self) -> str:
        parsing = MSG_NA
        codegen = MSG_NA
        idempotency = MSG_NA
        correctness = MSG_NA

        if self.contains(TEST_PARSING):
            if self.success(TEST_PARSING):
                parsing = MSG_SUCCESS
            else:
                parsing = MSG_ERROR

        if self.contains(TEST_CODEGEN):
            if self.success(TEST_CODEGEN):
                codegen = MSG_SUCCESS
            else:
                codegen = MSG_ERROR

        if self.contains(TEST_IDEMPOTENCY):
            if self.success(TEST_IDEMPOTENCY):
                idempotency = MSG_SUCCESS
            else:
                idempotency = MSG_ERROR

        if self.contains(TEST_CORRECTNESS):
            if self.success(TEST_CORRECTNESS):
                correctness = MSG_SUCCESS
            else:
                correctness = MSG_ERROR

        return f"- PARSING: {parsing}\n- CODE GENERATION: {codegen}\n- IDEMPOTENCY: {idempotency}\n- CORRECTNESS: {correctness}\n"

    def execute(self) -> None:
        # test the parsing and code generation
        _, out, err = self.cmd.run()

        self.process(out, err)

        # if both succeeded, test idempotency and correctness
        if self.contains(TEST_CODEGEN) and self.success(TEST_CODEGEN):
            self.idempotency()
            self.correctness()

    def parse_output(self, output: str) -> str:
        _, _, after = output.partition('CACTI_OUTPUT_BEGIN')
        json_data, _, after = after.partition('CACTI_OUTPUT_END')

        return json_data

    def process(self, out: str, err: str) -> None:
        json_data = self.parse_output(out)

        self.results = json.loads(json_data)

        # if the parsing failed, modify the json object to contain information about the error
        if not self.results[TEST_PARSING][SUCCESS]:
            self.results[TEST_PARSING][LOG] = err

        # if the code generation failed, modify the json object to contain information about the error
        elif not self.results[TEST_CODEGEN][SUCCESS]:
            self.results[TEST_CODEGEN][LOG] = err

    def contains(self, test_kind: str) -> bool:
        return test_kind in self.results.keys()

    def success(self, test_kind: str) -> bool:
        return self.results[test_kind][SUCCESS]

    def idempotency_iteration(self) -> tuple:
        start = time.time()

        src_name = 'gen' + str(self.curr_try) + '.cpp'

        if self.curr_try == 0:
            src_name = 'src.cpp'

        src_file = os.path.join(self.output_path, src_name)

        self.curr_try += 1

        self.cmd.params[PARAMS_CURR_TRY] = str(self.curr_try)

        _, stdout, stderr = self.cmd.run()

        gen_file = os.path.join(
            self.output_path, 'gen' + str(self.curr_try) + '.cpp')

        if not os.path.isfile(gen_file):
            raise OSError(f"Error: the file {gen_file} could not be found!")

        end = time.time()

        return stdout, stderr, src_file, gen_file, round(end - start, 3)

    def idempotency(self) -> None:
        subtests = []

        success = True

        # turn on debug mode
        self.cmd.params[PARAMS_DEBUG] = DEBUG_ON

        while True:
            if self.curr_try > IDEMPOTENCY_DEPTH:
                success = False
                break

            try:
                out, err, src, gen, time = self.idempotency_iteration()
            except OSError:
                success = False
                break

            temp_test = json.loads(self.parse_output(out))

            # remove unnecessary information from the test
            temp_test.pop(TEST_IDEMPOTENCY)
            temp_test.pop(TEST_CORRECTNESS)

            if not temp_test[TEST_PARSING][SUCCESS]:
                temp_test[TEST_PARSING][LOG] = err
            elif not temp_test[TEST_CODEGEN][SUCCESS]:
                temp_test[TEST_CODEGEN][LOG] = err

            equals = filecmp.cmp(src, gen)

            temp_test[SRC] = src
            temp_test[GEN] = gen
            temp_test[EQUALS] = equals
            temp_test[TIME] = time

            subtests.append(temp_test)

            if equals:
                success = True
                break

        # turn off debug mode
        self.cmd.params[PARAMS_DEBUG] = DEBUG_OFF

        self.results[TEST_IDEMPOTENCY][RESULTS] = subtests
        self.results[TEST_IDEMPOTENCY][SUCCESS] = success

    def strip_ir(self, ir: str) -> str:
        ir_file = open(ir, 'r')

        lines = []

        readline = ir_file.readline() 

        while 'target triple' not in readline:
            readline = ir_file.readline()

            continue
        
        line = ''

        while True:
            # check for EOF
            if not line:
                break
            
            # check for metadata
            if line.startswith(PREFIX_IR_METADATA):
                continue

            # read the next line and append it to lines
            line = ir_file.readline()
        
            lines.append(line)

        return ''.join(lines)


    def correctness(self) -> None:
        start = time.time()

        gen_file_path = os.path.join(self.output_path, 'src.cpp')

        ir_from_src = os.path.join(self.output_path, 'src.ll')
        ir_from_gen = os.path.join(self.output_path, 'gen.ll')

        src_ir_cmd = self.cmd.emit_llvm(self.source_path, ir_from_src, LLVM_O0)
        self.cmd.cmd = src_ir_cmd
        src_proc_code, _, _ = self.cmd.run()

        gen_ir_cmd = self.cmd.emit_llvm(gen_file_path, ir_from_gen, LLVM_O0)
        self.cmd.cmd = gen_ir_cmd
        gen_proc_code, _, _ = self.cmd.run()

        end = time.time()

        time_correctness = round(start - end, 3)

        if src_proc_code == 1 or gen_proc_code == 1:
            self.results[TEST_CORRECTNESS][SUCCESS] = False
            self.results[TEST_CORRECTNESS][TIME] = time_correctness
        else:
            stripped_src_ir = self.strip_ir(ir_from_src)
            stripped_gen_ir = self.strip_ir(ir_from_gen)

            self.results[TEST_CORRECTNESS][SUCCESS] = (stripped_src_ir == stripped_gen_ir)
            self.results[TEST_CORRECTNESS][TIME] = time_correctness

    def save(self) -> None:
        results_path = os.path.join(self.output_path, 'results.json')

        with open(results_path, 'w+') as f:
            json.dump(self.results, f)
