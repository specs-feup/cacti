import os
import argparse

from modules.test import *
from modules.command import *

KEY_ARG_SOURCE_PATH = 'source_path'
KEY_ARG_OUTPUT_PATH = 'output_path'
KEY_ARG_TRANSPILER  = 'transpiler'
KEY_ARG_STD = 'std'
KEY_ARG_IT  = 'it'
KEY_ARG_OPT = 'opt'
KEY_FLAG_VI = 'vi'
KEY_FLAG_VC = 'vc'

def find_source_files(root: str):
    return [(subdir + os.sep + file) for subdir, _, files in os.walk(root) for file in files if file.endswith('.cpp')]
    """Fetches all the C++ source files to be tested by CACTI.
    
    Args:
        root: The path to the root directory where all of the source files are located.
    
    Returns:
        A list containing the full paths to all the source files to be tested by CACTI, in a string format.
    
    Raises:
        This method does not raise any exception.
    """

if __name__ == '__main__':
    if (len(os.sys.argv) < 3):
        print("Usage:\n$ python3 cacti.py <test_folder> <transpiler>")
        exit(1)

    parser = argparse.ArgumentParser(description='Script to run CACTI')

    # add mandatory arguments
    parser.add_argument('-S', dest='path',       required=True, help='path to cacti_tests')
    parser.add_argument('-T', dest='transpiler', required=True, help='name of the transpiler')
    
    # add optional arguments
    parser.add_argument('-std', nargs='?', const='default_std', help='C standard')
    parser.add_argument('-it',  nargs='?', const='id_tries',    help='number of idempotency tries')
    parser.add_argument('opt',  nargs='?', choices=['O0', 'O2', 'O3'],  default='O0', help='optimization flag for emit_llvm')

    # add flags
    parser.add_argument('-vi', action='store_true', help='enable verbose idempotency output')
    parser.add_argument('-vc', action='store_true', help='enable verbose correctness output')

    # parse the arguments
    args = parser.parse_args()
    
    path = args.path
    trsp = args.transpiler
    
    std = args.std
    it  = args.it
    opt = args.opt if args.opt else 'O0'

    vi = args.vi
    vc = args.vc

    test_params = {
        KEY_ARG_SOURCE_PATH : None,
        KEY_ARG_OUTPUT_PATH : None,
        
        KEY_ARG_TRANSPILER  : trsp,
        
        KEY_ARG_STD : std,
        KEY_ARG_IT  : it,
        KEY_ARG_OPT : opt,
        
        KEY_FLAG_VI : vi,
        KEY_FLAG_VC : vc
    }

    WORKING_DIR = str(os.getcwd()) + '/'
    INPUT_FOLDER = WORKING_DIR + args.path
    
    TRANSPILER = str(trsp).lower()

    paths_c98 = find_source_files(os.path.join(INPUT_FOLDER, 'C++98'))
    paths_c11 = find_source_files(os.path.join(INPUT_FOLDER, 'C++11'))
    paths_c17 = find_source_files(os.path.join(INPUT_FOLDER, 'C++17'))
    paths_c20 = find_source_files(os.path.join(INPUT_FOLDER, 'C++20'))

    paths = paths_c98 + paths_c11 + paths_c17 + paths_c20

    paths.sort()

    for source_path in paths:        
        rel_path = source_path[len(INPUT_FOLDER):]
        
        aux_path = 'output' + rel_path[0:len(rel_path) - 7]
        
        output_path = os.path.join(INPUT_FOLDER, aux_path)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        test_params[KEY_ARG_SOURCE_PATH] = source_path
        test_params[KEY_ARG_OUTPUT_PATH] = output_path

        test = Test(test_params)
        
        # execute test
        test.execute()

        # display results
        test.print()

        # save results
        test.save()
    