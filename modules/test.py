import os
import json
import time
import filecmp

from modules.command import *

from modules.handlers.idempotency import IdempotencyHandler
from modules.handlers.correctness import CorrectnessHandler

from colorama import Fore


# Constants that represent Keys in the output JSON

KEY_TEST_PARSING = str('test_parsing')
KEY_TEST_CODEGEN = str('test_code_generation')
KEY_TEST_IDEMPOTENCY = str('test_idempotency')
KEY_TEST_CORRECTNESS = str('test_correctness')
KEY_SUCCESS = str('success')
KEY_LOG = str('log')
KEY_SRC = str('src')
KEY_GEN = str('gen')
KEY_EQUALS = str('equals')
KEY_TIME = str('time')
KEY_RESULTS = str('results')


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
        
        self.params = {
            PARAMS_FILE : self.source_path,
            PARAMS_OUTPUT_FOLDER : self.output_path,
            PARAMS_CURR_TRY : str(self.curr_try),
            PARAMS_DEBUG : DEBUG_OFF
        }
        
        self.results = dict()

    def __str__(self) -> str:
        parsing = MSG_NA
        codegen = MSG_NA
        idempotency = MSG_NA
        correctness = MSG_NA

        if self.contains(KEY_TEST_PARSING):
            if self.success(KEY_TEST_PARSING):
                parsing = MSG_SUCCESS
            else:
                parsing = MSG_ERROR

        if self.contains(KEY_TEST_CODEGEN):
            if self.success(KEY_TEST_CODEGEN):
                codegen = MSG_SUCCESS
            else:
                codegen = MSG_ERROR

        if self.contains(KEY_TEST_IDEMPOTENCY):
            if self.success(KEY_TEST_IDEMPOTENCY):
                idempotency = MSG_SUCCESS
            else:
                idempotency = MSG_ERROR

        if self.contains(KEY_TEST_CORRECTNESS):
            if self.success(KEY_TEST_CORRECTNESS):
                correctness = MSG_SUCCESS
            else:
                correctness = MSG_ERROR

        return f"- PARSING: {parsing}\n- CODE GENERATION: {codegen}\n- IDEMPOTENCY: {idempotency}\n- CORRECTNESS: {correctness}\n"

    def execute(self) -> None:
        # test the parsing and code generation
        _, out, err = self.cmd.run()

        self.process(out, err)

        # if both succeeded, test idempotency and correctness
        if self.contains(KEY_TEST_CODEGEN) and self.success(KEY_TEST_CODEGEN):
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
        if not self.results[KEY_TEST_PARSING][KEY_SUCCESS]:
            self.results[KEY_TEST_PARSING][KEY_LOG] = err

        # if the code generation failed, modify the json object to contain information about the error
        elif not self.results[KEY_TEST_CODEGEN][KEY_SUCCESS]:
            self.results[KEY_TEST_CODEGEN][KEY_LOG] = err

    def contains(self, test_kind: str) -> bool:
        return test_kind in self.results.keys()

    def success(self, test_kind: str) -> bool:
        return self.results[test_kind][KEY_SUCCESS]
    
    def idempotency(self) -> None:
        handler = IdempotencyHandler(self.output_path, self.params)

        subtests, success = handler.run()

        self.results[KEY_TEST_IDEMPOTENCY][KEY_RESULTS] = subtests
        self.results[KEY_TEST_IDEMPOTENCY][KEY_SUCCESS] = success
    
    def correctness(self) -> None:
        handler = CorrectnessHandler(self.source_path, self.output_path)

        success, elapsed = handler.run()

        self.results[KEY_TEST_CORRECTNESS][KEY_TIME] = elapsed
        self.results[KEY_TEST_CORRECTNESS][KEY_SUCCESS] = success

    def save(self) -> None:
        results_path = os.path.join(self.output_path, 'results.json')

        with open(results_path, 'w+') as f:
            json.dump(self.results, f)
