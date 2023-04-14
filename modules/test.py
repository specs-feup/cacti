import os
import json
import time
import filecmp

from modules import command

from colorama import Fore


class Test:
    def __init__(self, source_path: str, output_path: str, curr_try: int) -> None:
        self.source_path = source_path
        self.output_path = output_path
        self.results = dict()
        self.params = dict()
        self.curr_try = curr_try

        self.transpiler = str(os.sys.argv[2]).lower()

        if self.transpiler == 'clava':
            self.params = {"file": self.source_path, "outputFolder": self.output_path,
                           "idempotencyTry": str(self.curr_try), "silent": 'DUMMY'}

    def __str__(self) -> str:
        parsing = 'N/A'
        codegen = 'N/A'
        idempotency = 'N/A'
        correctness = 'N/A'

        if self.contains('test_parsing'):
            if self.success('test_parsing'):
                parsing = f"{Fore.GREEN}{'SUCCESS'}{Fore.RESET}"
            else:
                parsing = f"{Fore.RED}{'ERROR'}{Fore.RESET}"

        if self.contains('test_code_generation'):
            if self.success('test_code_generation'):
                codegen = f"{Fore.GREEN}{'SUCCESS'}{Fore.RESET}"
            else:
                codegen = f"{Fore.RED}{'ERROR'}{Fore.RESET}"

        if self.contains('test_idempotency'):
            if self.success('test_idempotency'):
                idempotency = f"{Fore.GREEN}{'SUCCESS'}{Fore.RESET}"
            else:
                idempotency = f"{Fore.RED}{'ERROR'}{Fore.RESET}"

        if self.contains('test_correctness'):
            if self.success('test_correctness'):
                correctness = f"{Fore.GREEN}{'SUCCESS'}{Fore.RESET}"
            else:
                correctness = f"{Fore.RED}{'ERROR'}{Fore.RESET}"

        return f"- PARSING: {parsing}\n- CODE GENERATION: {codegen}\n- IDEMPOTENCY: {idempotency}\n- CORRECTNESS: {correctness}\n"

    def update_params(self) -> None:
        if self.transpiler == 'clava':
            self.params = {"file": self.source_path, "outputFolder": self.output_path,
                          "idempotencyTry": str(self.curr_try), "silent": '-s'}


    def parse_output(self, output: str) -> str:
        _, _, after = output.partition('CACTI_OUTPUT_BEGIN')
        json_data, _, after = after.partition('CACTI_OUTPUT_END')

        return json_data

    def process(self, out: str, err: str) -> None:
        json_data = self.parse_output(out)

        self.results = json.loads(json_data)

        # if the parsing failed, modify the json object to contain information about the error
        if not self.results['test_parsing']['success']:
            self.results['test_parsing']['log'] = err

        # if the code generation failed, modify the json object to contain information about the error
        elif not self.results['test_code_generation']['success']:
            self.results['test_code_generation']['log'] = err

    def contains(self, test_kind: str) -> bool:
        return test_kind in self.results.keys()

    def success(self, test_kind: str) -> bool:
        return self.results[test_kind]['success']

    def idempotency_iteration(self) -> tuple:
        start = time.time()

        src_name = 'gen' + str(self.curr_try) + '.cpp'

        if self.curr_try == 0:
            src_name = 'src.cpp'

        print(f"curr_try = {self.curr_try}")
        print(f"src_name = {src_name}")
        
        src_file = os.path.join(self.output_path, src_name)

        print(f"src_file = {src_file}")

        self.curr_try += 1

        self.update_params()

        cmd = command.Command(self.params)

        _, stdout, stderr = cmd.run()

        gen_file = os.path.join(
            self.output_path, 'gen' + str(self.curr_try) + '.cpp')

        if not os.path.isfile(gen_file):
            raise OSError(f"Error: the file {gen_file} could not be found")

        end = time.time()
        
        return stdout, stderr, src_file, gen_file, round(end - start, 3)

    def idempotency(self) -> None:
        subtests = []

        self.update_params()

        while True:
            if self.curr_try >= 5:
                break

            try:
                out, err, src, gen, time = self.idempotency_iteration()

            except OSError:
                break
            
            temp_test = json.loads(self.parse_output(out))
            # if the parsing failed, modify the json object to contain information about the error
            
            if not temp_test['test_parsing']['success']:
                temp_test['test_parsing']['log'] = err

            # if the code generation failed, modify the json object to contain information about the error
            elif not temp_test['test_code_generation']['success']:
                temp_test['test_code_generation']['log'] = err

            success_parsing = temp_test['test_parsing']['success']
            success_codegen = temp_test['test_code_generation']['success']

            if not (success_parsing and success_codegen):
                continue

            equals = filecmp.cmp(src, gen)

            temp_test['src'] = src
            temp_test['gen'] = gen
            temp_test['equals'] = equals
            temp_test['time'] = time

            subtests.append(temp_test)

            if equals:
                break

        success = not (len(subtests) == 0 or len(subtests) == 5)

        self.results['test_idempotency']['results'] = subtests
        self.results['test_idempotency']['success'] = success

    def correctness(self) -> bool:
        pass

    def save(self) -> None:
        results_path = os.path.join(self.output_path, 'results.json')

        with open(results_path, 'w+') as f:
            json.dump(self.results, f)
