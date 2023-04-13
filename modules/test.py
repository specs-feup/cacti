import os
import json
import time

from colorama import Fore


class Test:
    def __init__(self, source_path: str, output_path: str, out: str, err: str) -> None:
        self.source_path = source_path
        self.output_path = output_path
        self.results = dict()
        self.out = out
        self.err = err

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

        return f"- PARSING: {parsing}\n-CODE GENERATION: {codegen}\n- IDEMPOTENCY: {idempotency}\n- CORRECTNESS: {correctness}"

    def process(self) -> None:
        _, _, after = self.out.partition('CACTI_OUTPUT_BEGIN')
        json_data, _, after = after.partition('CACTI_OUTPUT_END')

        self.results = json.loads(json_data)

        # if the parsing failed, modify the json object to contain information about the error
        if not self.results['test_parsing']['success']:
            self.results['test_parsing']['success'] = self.err

        # if the code generation failed, modify the json object to contain information about the error
        elif not self.results['test_code_generation']['success']:
            self.results['test_code_generation']['log'] = self.err

    def contains(self, test_kind: str) -> bool:
        return test_kind in self.results.keys()

    def success(self, test_kind: str) -> bool:
        return self.contains(test_kind) and self.results[test_kind]['success']

    def idempotency_iteration(self, curr_try: int) -> tuple:
        start = time.time()

        src_name = 'gen' + str(curr_try) + '.cpp'

        if curr_try == 0:
            src_name = 'src.cpp'
        
        src_file = os.path.join(self.output_path, src_name)

        curr_try += 1

        

        end = time.time()

        pass

    def idempotency(self) -> bool:
        pass

    def correctness(self) -> bool:
        pass

    def save(self) -> None:
        results_path = os.path.join(self.output_path, 'results.json')

        with open(results_path, 'w+') as f:
            json.dump(self.results, f)
