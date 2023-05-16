from colorama import Fore, Style

KEY_TEST_PARSING = str('test_parsing')
KEY_TEST_CODEGEN = str('test_code_generation')
KEY_TEST_IDEMPOTENCY = str('test_idempotency')
KEY_TEST_CORRECTNESS = str('test_correctness')
KEY_SUCCESS = str('success')
KEY_TIME = str('time')

CHECKMARK = Fore.GREEN + Style.BRIGHT + u'\u2713' + Style.RESET_ALL
ERROR = Fore.RED + Style.BRIGHT + u'\u2715' + Style.RESET_ALL
SQUARE = Fore.WHITE + Style.BRIGHT + u'\u25a0' + Style.RESET_ALL
BRANCH = Fore.BLUE + Style.BRIGHT + '└──' + Style.RESET_ALL
INDENT = 4 * ' '


class DisplayHandler:
    def __init__(self, path: str, test: dict) -> None:
        self.path = path
        self.test = test

    def test_passed(self, test: str, time: float) -> str:
        return f"{2*INDENT}{CHECKMARK} " + Style.DIM + Fore.WHITE + test + f" passed successfully ({str(time)}ms)" + Style.RESET_ALL

    def test_failed(self, test: str) -> str:
        return f"{2*INDENT}{ERROR} " + Style.DIM + Fore.WHITE + test + f" failed" + Style.RESET_ALL

    def test_unknown(self, test: str) -> str:
        return f"{2*INDENT}{SQUARE} {test} was not run"
    
    def formatted_path(self) -> str:
        return Fore.WHITE + Style.BRIGHT + self.path + Style.RESET_ALL

    def test_results(self, passed: int, failed: int) -> tuple:
        passed_str = CHECKMARK + " " + Style.BRIGHT + \
            Fore.GREEN + str(passed) + " tests passed" + Style.RESET_ALL
        failed_str = ERROR + " " + Style.BRIGHT + \
            Fore.RED + str(failed) + " tests failed" + Style.RESET_ALL

        return passed_str, failed_str
    
    def contains(self, test_kind: str) -> bool:
        return test_kind in self.test.keys()

    def success(self, test_kind: str) -> bool:
        return self.test[test_kind][KEY_SUCCESS]

    def run(self):
        parsing = self.test_unknown('parsing')
        codegen = self.test_unknown('codegen')
        idempotency = self.test_unknown('idempotency')
        correctness = self.test_unknown('correctness')

        fpath = self.formatted_path()

        passed = 0
        failed = 0
            
        if self.contains(KEY_TEST_PARSING):
            if self.success(KEY_TEST_PARSING):
                parsing = self.test_passed('parsing', self.test[KEY_TEST_PARSING][KEY_TIME])
                passed += 1
            else:
                parsing = self.test_failed('parsing')
                failed += 1

        if self.contains(KEY_TEST_CODEGEN):
            if self.success(KEY_TEST_CODEGEN):
                codegen = self.test_passed('codegen', self.test[KEY_TEST_CODEGEN][KEY_TIME])
                passed += 1
            else:
                codegen = self.test_failed('codegen')
                failed += 1

        if self.contains(KEY_TEST_IDEMPOTENCY):
            if self.success(KEY_TEST_IDEMPOTENCY):
                idempotency = self.test_passed('idempotency', 0.0)
                passed += 1
            else:
                idempotency = self.test_failed('idempotency')
                failed += 1

        if self.contains(KEY_TEST_CORRECTNESS):
            if self.success(KEY_TEST_CORRECTNESS):
                correctness = self.test_passed('correctness', self.test[KEY_TEST_CORRECTNESS][KEY_TIME])
                passed += 1
            else:
                correctness = self.test_failed('correctness')
                failed += 1

        num_passed, num_failed = self.test_results(passed, failed)

        print(fpath)
        
        print(f"{INDENT}parsing")
        print(parsing)

        print(f"{INDENT}code generation")
        print(codegen)

        print(f"{INDENT}idempotency")
        print(idempotency)

        print(f"{INDENT}correctness")
        print(correctness)

        print(num_passed)
        print(num_failed)
