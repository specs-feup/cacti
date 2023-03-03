import os
import subprocess
import constants

def find_source_files(root):
    return [(subdir + os.sep + file) for subdir, _, files in os.walk(root) for file in files if file.endswith(constants.CPP_EXTENSION)]


if __name__ == '__main__':
    if (len(os.sys.argv) < 3):
        print("Usage: ")
        print("$ python3 cacti.py <test_folder> <transpiler>")
        exit(constants.EXIT_FAILURE)

    WORKING_DIR = str(os.getcwd()) + '/'
    INPUT_FOLDER = WORKING_DIR + str(os.sys.argv[1]).lower()

    os.getcwd()
    TRANSPILER   = str(os.sys.argv[2]).lower()

    paths = find_source_files(INPUT_FOLDER)
    paths.sort()

    for source_path in paths:        
        rel_path = source_path[len(INPUT_FOLDER) + 1:]

        output_path = INPUT_FOLDER + '/output/' + rel_path[0:len(rel_path) - 7]
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        script_folder = f"{WORKING_DIR}{TRANSPILER}/" 
        script_path = script_folder + 'script.sh'
        
        cmd_str = f"{script_path} \'{script_folder}\' \'{source_path}\' \'{output_path}\'"

        subprocess.run(cmd_str, shell = True)



