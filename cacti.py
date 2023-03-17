import subprocess
import json
import time
import os
import filecmp

from clava import exec

from constants import const_cacti as concti
from constants import const_misc  as misc
from constants import const_test  as test


def find_source_files(root):
    return [(subdir + os.sep + file) for subdir, _, files in os.walk(root) for file in files if file.endswith(misc.CPP_EXTENSION)]


def run(cmd):
    start_time = time.time()

    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True)

    proc.wait()

    end_time = time.time()

    runtime = end_time - start_time
    
    stdout, stderr = proc.communicate()

    return proc.returncode, stdout, stderr, round(runtime, 3)


def parse_output(output):
    _, _, after = output.partition(concti.DELIMITER_BEGIN)
    json_data, _, after = after.partition(concti.DELIMITER_END)

    return json_data


def process_json(json_test, err, runtime):
    # if the parsing failed, modify the json object to contain information about the error
    if not json_test[test.PARSING][test.SUCCESS]:
        json_test[test.PARSING][test.LOG] = err

    # if the code generation failed, modify the json object to contain information about the error
    elif not json_test[test.CODE_GENERATION][test.SUCCESS]:
        json_test[test.CODE_GENERATION][test.LOG] = err
    
    elif test.IDEMPOTENCY in json_test and not json_test[test.IDEMPOTENCY][test.SUCCESS]:
        json_test[test.IDEMPOTENCY][test.LOG] = err

    json_test[test.RUNTIME] = runtime

    return json_test


def get_transpiler_cmd(source_path, ouput_path, silent, ntry):
    input_transpiler = str(os.sys.argv[2]).lower()

    if input_transpiler == misc.TRANSPILER_ROSE:
        return ' '
    
    if input_transpiler == misc.TRANSPILER_INSIEME:
        return ' '

    if input_transpiler == misc.TRANSPILER_CETUS:
        return ' '
    
    if input_transpiler == misc.TRANSPILER_CIL:
        return ' '

    if input_transpiler == misc.TRANSPILER_MERCURIUM:
        return ' '

    if input_transpiler == misc.TRANSPILER_CLAVA: 
        return exec.clava(source_path, output_path, silent, ntry)
    
    return ' '


def test_idempotency(output_path, tries):
    curr_try = 0

    while curr_try != tries:
        src = os.path.join(output_path, concti.GEN_FILE_PREAMBLE + str(curr_try) + misc.CPP_EXTENSION)

        curr_try += 1

        cmd = get_transpiler_cmd(src, output_path, concti.FLAG_SILENT, curr_try)
        
        _, _, _, _ = run(cmd)
        
        gen = os.path.join(output_path, concti.GEN_FILE_PREAMBLE + str(curr_try) + misc.CPP_EXTENSION)
        
        if not os.path.isfile(gen) or filecmp.cmp(src, gen):
            break
    
    return curr_try


if __name__ == '__main__':
    if (len(os.sys.argv) < 3):
        print("Usage:\n$ python3 cacti.py <test_folder> <transpiler>")
        exit(misc.EXIT_FAILURE)

    WORKING_DIR = str(os.getcwd()) + '/'
    INPUT_FOLDER = WORKING_DIR + str(os.sys.argv[1]).lower()

    os.getcwd()
    
    TRANSPILER   = str(os.sys.argv[2]).lower()

    paths = find_source_files(INPUT_FOLDER)
    paths.sort()

    for source_path in paths:        
        rel_path = source_path[len(INPUT_FOLDER):]

        output_path = os.path.join(INPUT_FOLDER, 'output', rel_path[0:len(rel_path) - 7])
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        cmd = get_transpiler_cmd(source_path, output_path, 'dummy', 0)

        print(f"Running {rel_path}...")
        
        code, out, err, runtime = run(cmd)
        
        print(">> Test exited successfully.")

        json_test = json.loads(parse_output(out))

        processed_test = process_json(json_test, err, runtime)
        
        if test.CODE_GENERATION in processed_test:
            if processed_test[test.CODE_GENERATION][test.SUCCESS]:
                tries = test_idempotency(output_path, test.IDEMPOTENCY_TRIES)

        file_path = os.path.join(output_path, "results.json")

        with open(file_path, "w+") as f:
            json.dump(processed_test, f)
    