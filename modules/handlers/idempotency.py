import os
import json
import time
import filecmp

from modules.exception import IdempotencyException
from modules.command import *


IDEMPOTENCY_DEPTH = int(5)

PARAMS_FILE = str("file")
PARAMS_OUTPUT_FOLDER = str("output_folder")
PARAMS_CURR_TRY = str("curr_try")
PARAMS_DEBUG = str("debug_mode")

DEBUG_ON = str(True)
DEBUG_OFF = str(False)

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


class IdempotencyHandler:
    def __init__(self, output_path: str, params: dict) -> None:
        self.params = params
        self.output_path = output_path
        self.transpiler = params["transpiler"]
        self.curr_try = 0

    def get_filename(self) -> str:
        if self.curr_try == 0:
            return 'src.cpp'

        return 'gen' + str(self.curr_try) + '.cpp'

    def parse_output(self, output: str) -> str:
        _, _, after = output.partition('CACTI_OUTPUT_BEGIN')
        json_data, _, after = after.partition('CACTI_OUTPUT_END')

        return json_data

    def iteration(self) -> tuple:
        start = time.time()

        src = os.path.join(self.output_path, self.get_filename())
        
        self.curr_try += 1

        self.params[PARAMS_CURR_TRY] = str(self.curr_try)

        args = transpiler_cmd(self.transpiler, self.params)

        cmd = Command(args)

        _, stdout, stderr = cmd.run()

        gen = os.path.join(self.output_path, self.get_filename())

        if not os.path.isfile(gen):
            raise OSError(f"Error: the file {gen} could not be found!")

        end = time.time()

        return stdout, stderr, src, gen, round(end - start, 3)

    def run(self) -> tuple:
        subtests = []

        success = True

        self.params[PARAMS_DEBUG] = DEBUG_ON

        while True:
            if self.curr_try > IDEMPOTENCY_DEPTH:
                success = False
                break

            try:
                out, err, src, gen, time = self.iteration()
            except OSError:
                success = False
                break

            temp_test = json.loads(self.parse_output(out))
            
            temp_test.pop(KEY_TEST_IDEMPOTENCY)
            temp_test.pop(KEY_TEST_CORRECTNESS)

            if not temp_test[KEY_TEST_PARSING][KEY_SUCCESS]:
                temp_test[KEY_TEST_PARSING][KEY_LOG] = err
            elif not temp_test[KEY_TEST_CODEGEN][KEY_SUCCESS]:
                temp_test[KEY_TEST_CODEGEN][KEY_LOG] = err

            equals = filecmp.cmp(src, gen)

            temp_test[KEY_SRC] = src
            temp_test[KEY_GEN] = gen
            temp_test[KEY_EQUALS] = equals
            temp_test[KEY_TIME] = time

            subtests.append(temp_test)

            if equals:
                success = True
                break

        self.params[PARAMS_DEBUG] = DEBUG_OFF

        return subtests, success
