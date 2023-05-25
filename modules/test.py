import os
import json
import time
import filecmp

from modules.command import *

from modules.handlers.idempotency import IdempotencyHandler
from modules.handlers.correctness import CorrectnessHandler
from modules.handlers.display import DisplayHandler

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
PARAMS_TRANSPILER = str("transpiler")
PARAMS_CURR_TRY = str("curr_try")
PARAMS_DEBUG = 'debug_mode'


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

KEY_ARG_SOURCE_PATH = 'source_path'
KEY_ARG_OUTPUT_PATH = 'output_path'
KEY_ARG_TRANSPILER  = 'transpiler'
KEY_ARG_OUTPUT_FILENAME = 'output_filename'
KEY_ARG_STD = 'std'
KEY_ARG_IT  = 'it'
KEY_ARG_OPT = 'opt'
KEY_FLAG_VI = 'vi'
KEY_FLAG_VC = 'vc'


class Test:
    def __init__(self, test_params: dict) -> None:
        self.source_path = test_params[KEY_ARG_SOURCE_PATH]
        self.output_path = test_params[KEY_ARG_OUTPUT_PATH]
        
        self.transpiler = test_params[KEY_ARG_TRANSPILER]

        self.std = test_params[KEY_ARG_STD]
        self.it  = test_params[KEY_ARG_IT]
        self.opt = test_params[KEY_ARG_OPT]

        self.vi = test_params[KEY_FLAG_VI]
        self.vc = test_params[KEY_FLAG_VC]

        self.debug = DEBUG_OFF

        self.trsp_params = {
            KEY_ARG_SOURCE_PATH     : test_params[KEY_ARG_SOURCE_PATH],
            KEY_ARG_OUTPUT_PATH     : test_params[KEY_ARG_OUTPUT_PATH],
            KEY_ARG_OUTPUT_FILENAME : 'src.cpp',
            PARAMS_DEBUG            : DEBUG_OFF
        }

        self.corr_params = {
            KEY_ARG_SOURCE_PATH : test_params[KEY_ARG_SOURCE_PATH],
            KEY_ARG_SOURCE_PATH : test_params[KEY_ARG_OUTPUT_PATH],
            KEY_ARG_OPT         : test_params[KEY_ARG_OPT]
        }

        self.results = dict()

    def print(self) -> None:
        handler = DisplayHandler(self.source_path, self.results)

        handler.run()

    def execute(self) -> None:
        # test the parsing and code generation
        args = transpiler_cmd(self.transpiler, self.trsp_params)

        cmd = Command(args)

        _, out, err = cmd.run()

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
        handler = IdempotencyHandler(self.output_path, self.transpiler)

        subtests, success = handler.run()

        self.results[KEY_TEST_IDEMPOTENCY][KEY_RESULTS] = subtests
        self.results[KEY_TEST_IDEMPOTENCY][KEY_SUCCESS] = success

    def correctness(self) -> None:
        handler = CorrectnessHandler(self.source_path, self.output_path, self.opt)

        success, elapsed = handler.run()

        self.results[KEY_TEST_CORRECTNESS][KEY_TIME] = elapsed
        self.results[KEY_TEST_CORRECTNESS][KEY_SUCCESS] = success

    def save(self) -> None:
        results_path = os.path.join(self.output_path, 'results.json')

        with open(results_path, 'w+') as f:
            json.dump(self.results, f)
