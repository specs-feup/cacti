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
    """Module responsible for displaying the contents of a test.
    
    Attributes:
        path (str): The path to the test (source file).
        test (dict): The dictionary object that contains the result of the test.
    """
    def __init__(self, path: str, test: dict) -> None:
        """Initialize the DisplayHandler instance.
        
        Args:
            path (str): The value for path.
            test (dict): The value for test.
        """
        self.path = path
        self.test = test

    def test_passed(self, test: str, time: float) -> str:
        """Compute the string that gives information about a successful transpilation task.

        Args:
            test (str): The successful transpilation task.
            time (float): The time it took for the task to execute.
        """
        return f"{2*INDENT}{CHECKMARK} " + Style.DIM + Fore.WHITE + test + f" passed successfully ({str(time)}ms)" + Style.RESET_ALL

    def test_failed(self, test: str) -> str:
        """Compute the string that gives information about an unsuccessful transpilation task.

        Args:
            test (str): The unsuccessful transpilation task.
        """
        return f"{2*INDENT}{ERROR} " + Style.DIM + Fore.WHITE + test + f" failed" + Style.RESET_ALL

    def test_unknown(self, test: str) -> str:
        """Compute the string that gives information about an unknown (not executed) transpilation task. 
        
        Args:
            test (str): The unknown transpilation task.
        """
        return f"{2*INDENT}{SQUARE} {test} was not run"
    
    def formatted_path(self) -> str:
        """Pretty prints the path of the test.
        """
        return Fore.WHITE + Style.BRIGHT + self.path + Style.RESET_ALL

    def test_results(self, passed: int, failed: int) -> tuple:
        """Computes the strings that contain information about the number of tests that passed and failed.

        Args:
            passed (int): The number of succesful tasks.
            failed (int): The number of unsuccessful tasks.
        
        Returns:
            tuple: A pair that contains information about the number of tests that passed and failed.
        """
        passed_str = CHECKMARK + " " + Style.BRIGHT + \
            Fore.GREEN + str(passed) + " tests passed" + Style.RESET_ALL
        failed_str = ERROR + " " + Style.BRIGHT + \
            Fore.RED + str(failed) + " tests failed" + Style.RESET_ALL

        return passed_str, failed_str
    
    def contains(self, test_kind: str) -> bool:
        return test_kind in self.test.keys()

    def success(self, test_kind: str) -> bool:
        if KEY_SUCCESS in self.test[test_kind] and self.test[test_kind][KEY_SUCCESS] != "":
            return self.test[test_kind][KEY_SUCCESS]
        return False

    def run(self):
        """Execute the handler.
        """
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
            elif self.test[KEY_TEST_PARSING][KEY_SUCCESS] is False:
                parsing = self.test_failed('parsing')
                failed += 1

        if self.contains(KEY_TEST_CODEGEN):
            if self.success(KEY_TEST_CODEGEN) is True:
                codegen = self.test_passed('codegen', self.test[KEY_TEST_CODEGEN][KEY_TIME])
                passed += 1
            elif self.test[KEY_TEST_CODEGEN][KEY_SUCCESS] is False:
                codegen = self.test_failed('codegen')
                failed += 1

        if self.contains(KEY_TEST_IDEMPOTENCY):
            if self.success(KEY_TEST_IDEMPOTENCY) is True:
                idempotency = self.test_passed('idempotency', 0.0)
                passed += 1
            elif self.test[KEY_TEST_IDEMPOTENCY][KEY_SUCCESS] is False:
                idempotency = self.test_failed('idempotency')
                failed += 1

        if self.contains(KEY_TEST_CORRECTNESS):
            if self.success(KEY_TEST_CORRECTNESS) is True:
                correctness = self.test_passed('correctness', self.test[KEY_TEST_CORRECTNESS][KEY_TIME])
                passed += 1
            elif self.test[KEY_TEST_CORRECTNESS][KEY_SUCCESS] is False:
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
