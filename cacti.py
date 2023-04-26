import subprocess
import json
import time
import os
import filecmp

from clava import exec
from colorama import Fore

from modules import test as module_test
from modules import command as module_command


def find_source_files(root):
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

    WORKING_DIR = str(os.getcwd()) + '/'
    INPUT_FOLDER = WORKING_DIR + str(os.sys.argv[1]).lower()
    
    TRANSPILER = str(os.sys.argv[2]).lower()

    paths_c98 = find_source_files(os.path.join(INPUT_FOLDER, 'C++98'))
    paths_c11 = find_source_files(os.path.join(INPUT_FOLDER, 'C++11'))
    paths_c17 = find_source_files(os.path.join(INPUT_FOLDER, 'C++17'))
    paths_c20 = find_source_files(os.path.join(INPUT_FOLDER, 'C++20'))

    paths = paths_c98 + paths_c11 + paths_c17 + paths_c20

    paths.sort()

    for source_path in paths:        
        rel_path = source_path[len(INPUT_FOLDER):]
        
        aux_path = 'output' + rel_path[0:len(rel_path) - 7]
        
        print(f"Running {rel_path}...")

        output_path = os.path.join(INPUT_FOLDER, aux_path)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        test = module_test.Test(source_path, output_path, 0)

        test.execute()

        print(test)

        test.save()
    