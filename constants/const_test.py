from colorama import Fore

PARSING           = str('test_parsing')
CODE_GENERATION   = str('test_code_generation')
IDEMPOTENCY       = str('test_idempotency')
IDEMPOTENCY_TRIES = str('tries')
IDEMPOTENCY_DEPTH = int(5)
CORRECTNESS       = str('test_correctness')
SUCCESS           = str('success')
ERROR             = str('error')
SUCCESS_MSG       = f"{Fore.GREEN}{'SUCCESS'}{Fore.RESET}"
ERROR_MSG         = f"{Fore.RED}{'ERROR'}{Fore.RESET}"
LOG               = str('log')
TIME              = str('time')
RESULTS           = str('results')
SRC_FILE          = str('src_file')
GEN_FILE          = str('gen_file')
EQ                = str('eq')