import subprocess
import json
import os

import constants

from clava import exec


def find_source_files(root):
    return [(subdir + os.sep + file) for subdir, _, files in os.walk(root) for file in files if file.endswith(constants.CPP_EXTENSION)]

def run(cmd):
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True)

    stdout, stderr = proc.communicate()

    return proc.returncode, stdout, stderr


def parse_output(output):
    _, _, after = output.partition(constants.CACTI_DELIMITER_BEGIN)
    json_data, _, after = after.partition(constants.CACTI_DELIMITER_END)

    return json_data


def process_json(json_test, err):
    # if the parsing failed, modify the json object to contain information about the error
    if not json_test['test_parsing']['success']:
        json_test['test_parsing']['log'] = err

    # if the code generation failed, modify the json object to contain information about the error
    elif not json_test['test_code_generation']['success']:
        json_test['test_code_generation']['log'] = err

    return json_test

def get_transpiler_cmd(source_path, ouput_path):
    input_transpiler = str(os.sys.argv[2]).lower()

    if input_transpiler == constants.TRANSPILER_ROSE:
        return ' '
    
    if input_transpiler == constants.TRANSPILER_INSIEME:
        return ' '

    if input_transpiler == constants.TRANSPILER_CETUS:
        return ' '
    
    if input_transpiler == constants.TRANSPILER_CIL:
        return ' '

    if input_transpiler == constants.TRANSPILER_MERCURIUM:
        return ' '

    if input_transpiler == constants.TRANSPILER_CLAVA: 
        return exec.clava(source_path, output_path)
    
    return ' '


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
                        
        cmd = get_transpiler_cmd(source_path, output_path)

        code, out, err = run(cmd)
        
        json_test = json.loads(parse_output(out))
        
        processed_test = process_json(json_test, err)

        file_path = os.path.join(output_path, "results.json")

        with open(file_path, "w+") as f:
            json.dump(processed_test, f)
    