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
    """Fetches all the C++ source files to be tested by CACTI.
    
    Args:
        root: The path to the root directory where all of the source files are located.
    
    Returns:
        A list containing the full paths to all the source files to be tested by CACTI, in a string format.
    
    Raises:
        This method does not raise any exception.
    """


def run(cmd):
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True)

    proc.wait()

    stdout, stderr = proc.communicate()

    return proc.returncode, stdout, stderr
    """
    
    """


def parse_output(output):
    _, _, after = output.partition(concti.DELIMITER_BEGIN)
    json_data, _, after = after.partition(concti.DELIMITER_END)

    return json_data


def process_json(json_test, err):
    # if the parsing failed, modify the json object to contain information about the error
    if not json_test[test.PARSING][test.SUCCESS]:
        json_test[test.PARSING][test.LOG] = err

    # if the code generation failed, modify the json object to contain information about the error
    elif not json_test[test.CODE_GENERATION][test.SUCCESS]:
        json_test[test.CODE_GENERATION][test.LOG] = err

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


def test_idempotency(output_path, tries):
    curr_try = 0

    while curr_try != tries:
        src_file_name = concti.GEN_FILE_PREAMBLE + str(curr_try) + misc.CPP_EXTENSION

        if curr_try == 0:
            src_file_name = concti.SRC_FILE_PREAMBLE + misc.CPP_EXTENSION

        src = os.path.join(output_path, src_file_name)

        curr_try += 1

        cmd = get_transpiler_cmd(src, output_path, concti.FLAG_SILENT, curr_try)
        
        _, _, _ = run(cmd)
        
        gen = os.path.join(output_path, concti.GEN_FILE_PREAMBLE + str(curr_try) + misc.CPP_EXTENSION)


        if not os.path.isfile(gen):
            raise OSError(f"Error: the file {gen} could not be found.")

        if filecmp.cmp(src, gen):
            return True, curr_try
    
    return False, curr_try


def get_clang_cmd(source_path, output_path):
    return ["clang", "-S", "-O0", "-emit-llvm", source_path, "-o", output_path]


def test_correctness(source_path, output_path):
    gen_file = os.path.join(output_path, concti.SRC_FILE_PREAMBLE + misc.CPP_EXTENSION)
    
    src_ir_dir = os.path.join(output_path, concti.SRC_FILE_PREAMBLE)
    gen_ir_dir = os.path.join(output_path, concti.GEN_FILE_PREAMBLE)

    os.makedirs(src_ir_dir)
    os.makedirs(gen_ir_dir)

    ir_from_src = os.path.join(src_ir_dir, concti.IR_FILE_PREAMBLE + misc.IR_EXTENSION)
    ir_from_gen = os.path.join(gen_ir_dir, concti.IR_FILE_PREAMBLE + misc.IR_EXTENSION)

    cmd_clang_src = get_clang_cmd(source_path, ir_from_src)
    cmd_clang_gen = get_clang_cmd(gen_file, ir_from_gen)

    src_proc_code, _, _ = run(cmd_clang_src)
    gen_proc_code, _, _ = run(cmd_clang_gen)

    return ir_from_src, ir_from_gen, src_proc_code, gen_proc_code


def strip_ir(ir):
    ir_file = open(ir, "r")
    lines = []

    while "; Function Attrs:" not in ir_file.readline():
        continue

    line = ""

    while True:
        line = ir_file.readline()
        
        if "!llvm.module.flags" in line:
            break

        lines.append(line)
    
    return ''.join(lines)


if __name__ == '__main__':
    if (len(os.sys.argv) < 3):
        print("Usage:\n$ python3 cacti.py <test_folder> <transpiler>")
        exit(misc.EXIT_FAILURE)

    WORKING_DIR = str(os.getcwd()) + '/'
    INPUT_FOLDER = WORKING_DIR + str(os.sys.argv[1]).lower()
    print(f"WOrking DIR = {WORKING_DIR}")
    os.getcwd()
    
    TRANSPILER = str(os.sys.argv[2]).lower()

    paths = find_source_files(INPUT_FOLDER)
    paths.sort()

    for source_path in paths:        
        rel_path = source_path[len(INPUT_FOLDER):]
        aux_path = 'output' + rel_path[0:len(rel_path) - 7]

        output_path = os.path.join(INPUT_FOLDER, aux_path)
        print(f"output_path = {output_path}")
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        cmd = get_transpiler_cmd(source_path, output_path, concti.FLAG_DUMMY, 0)
        
        code, out, err = run(cmd)

        print(">> Test exited successfully.")

        json_test = json.loads(parse_output(out))

        processed_test = process_json(json_test, err)
        
        if test.CODE_GENERATION in processed_test and processed_test[test.CODE_GENERATION][test.SUCCESS]:                
            # start testing for idempotency
            time_idempotency = 0.0
            
            try:
                start_idempotency = time.time()
                
                converged, tries = test_idempotency(output_path, test.IDEMPOTENCY_DEPTH)

                end_idempotency = time.time()

                time_idempotency = round(end_idempotency - start_idempotency, 3)
            except OSError:
                converged = False
                tries = -1
            
            processed_test[test.IDEMPOTENCY][test.SUCCESS] = converged
            processed_test[test.IDEMPOTENCY][test.IDEMPOTENCY_TRIES] = tries
            processed_test[test.IDEMPOTENCY][test.TIME] = time_idempotency

            # start testing for correctness

            start_correctness = time.time()
            
            ir_from_src, ir_from_gen, src_proc_code, gen_proc_code = test_correctness(source_path, output_path)

            end_correctness = time.time()

            time_correctness = round(end_correctness - start_correctness, 3)

            # the clang process failed to execute, meaning correctness cannot be tested
            if src_proc_code == misc.EXIT_FAILURE or gen_proc_code == misc.EXIT_FAILURE:
                processed_test[test.CORRECTNESS][test.SUCCESS] = False
                processed_test[test.CORRECTNESS][test.TIME] = time_correctness
            else:            
                stripped_src_ir = strip_ir(ir_from_src)
                stripped_gen_ir = strip_ir(ir_from_gen)

                processed_test[test.CORRECTNESS][test.SUCCESS] = stripped_src_ir == stripped_gen_ir
                processed_test[test.CORRECTNESS][test.TIME] = time_correctness
                

        file_path = os.path.join(output_path, "results.json")
        
        print("output_path = " + output_path)

        with open(file_path, "w+") as f:
            json.dump(processed_test, f)
    