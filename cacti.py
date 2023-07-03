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
SUPPORTED_STANDARDS: list[str] = ['C89', 'C95', 'C99', 'C11', 'C17', 'C23', 'C++98' ,'C++11', 'C++20']

def get_file_extension(standard: str) -> str:
        return ".cpp" if standard.lower().find("c++") != -1 else ".c"


def find_source_files(root: str):
    return [(subdir + os.sep + file) for subdir, _, files in os.walk(root) for file in files if file.endswith('.cpp') or file.endswith('.c')]
    """Fetches all the C/C++ source files to be tested by CACTI.
    
    Args:
        root: The path to the root directory where all of the source files are located.
    
    Returns:
        A list containing the full paths to all the source files to be tested by CACTI, in a string format.
    
    Raises:
        This method does not raise any exception.
    """

def find_source_files_standards(root: str) -> dict[str, list[str]]:
    files_by_standard: dict[str, list[str]] = dict()
    for standard in SUPPORTED_STANDARDS:
        file_extension: str = get_file_extension(standard)

        files_by_standard[standard] = [] if standard not in os.listdir(root) else \
                [str(os.path.abspath(subdir + os.sep + file)) for subdir, _, files in os.walk(os.path.join(root, standard))\
                    for file in files if file.endswith(file_extension)]

    return files_by_standard

def find_source_files_nonstandards(root: str) -> dict[str, list[str]]:
    root = os.path.abspath(root)

    source_files = dict()
    child_directories = [os.path.join(root, name) for name in os.listdir(root) if os.path.isdir(os.path.join(root, name)) and name not in SUPPORTED_STANDARDS and name != "output"]

    # Print the child directories
    for child_directory in child_directories:
        standard_replacement_name = os.path.basename(child_directory)
        source_files[standard_replacement_name] = \
            [str(os.path.abspath(subdir + os.sep + file)) for subdir, _, files in os.walk(root)\
                for file in files if file.endswith(".cpp") or file.endswith(".c")]
    
    return source_files

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to run CACTI')

    # add mandatory arguments
    parser.add_argument('-S', '--source', dest='path', required=True, help='path to cacti_tests')
    parser.add_argument('-T', '--transpiler', dest='transpiler', required=True, help='name of the transpiler')
    
    # add optional arguments
    parser.add_argument('-i', '--it', '--idempotency-tries', dest='it', nargs='?', const='id_tries', help='number of idempotency tries')
    parser.add_argument('-o', '--opt', '--optimize', dest='opt', nargs='?', choices=['O0', 'O2', 'O3'],  default='O0', help='optimization flag for emit_llvm')
    parser.add_argument('--of', '--output-folder', dest="output_folder", type=str, default=os.getcwd(), nargs='?', const='')

    std_arguments_group = parser.add_mutually_exclusive_group()
    std_arguments_group.add_argument('--std', nargs='?', const='default_std', help='C/C++ standard')
    std_arguments_group.add_argument('--aas', '--allow-any-std', dest='aas', action='store_const', const=True, default=False, help='allow any standards of C/C++')

    # add flags
    parser.add_argument('--vi', '--verbose-idempotency', dest='vi', action='store_true', help='enable verbose idempotency output')
    parser.add_argument('--vc', '--verbose-correctness', dest='vc', action='store_true', help='enable verbose correctness output')

    # parse the arguments
    args = parser.parse_args()
    
    path = args.path
    trsp = args.transpiler
    
    std = args.std
    it  = args.it
    opt = args.opt if args.opt else 'O0'
    any_std = args.aas

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
    INPUT_FOLDER = str(os.path.abspath(WORKING_DIR + args.path))
    TRANSPILER = str(trsp).lower()

    paths_by_standard: dict[str, list[str]] = dict()

    if std:
        paths = find_source_files(os.path.join(INPUT_FOLDER, std))
    elif any_std:
        standard_paths = [path for path_list in find_source_files_standards(INPUT_FOLDER).values() for path in path_list]
        non_standard_paths = [path for path_list in find_source_files_nonstandards(INPUT_FOLDER).values() for path in path_list]
        paths = standard_paths + non_standard_paths
    else:
        paths = [path for path_list in find_source_files_standards(INPUT_FOLDER).values() for path in path_list]
    
    for path in paths:
        if path.find("Extension") != -1:
            print(path)
    
    paths.sort()

    for source_path in paths:        
        rel_path = source_path[len(INPUT_FOLDER):]

        aux_path = 'output/' + TRANSPILER + "/" + rel_path[0:]
        
        output_path = os.path.join(args.output_folder, aux_path)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        test_params[KEY_ARG_SOURCE_PATH] = source_path
        test_params[KEY_ARG_OUTPUT_PATH] = output_path

        test = Test(test_params)
        
        # execute test
        test.execute()

        # display results
        test.print()
        print('\n')

        # save results
        test.save()
    