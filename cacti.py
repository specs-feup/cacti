import subprocess
import json
import time
import os
import filecmp

from clava import exec
from colorama import Fore

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


def diff(file1, file2):
    return run(["diff", file1, file2])


def idempotency_iteration(curr_try, output_path):
    start = time.time()

    src_file_name = concti.GEN_FILE_PREAMBLE + str(curr_try) + misc.CPP_EXTENSION

    if curr_try == 0:
        src_file_name = concti.SRC_FILE_PREAMBLE + misc.CPP_EXTENSION
    
    src = os.path.join(output_path, src_file_name)

    curr_try += 1

    cmd = get_transpiler_cmd(src, output_path, concti.FLAG_SILENT, curr_try)

    _, out, err = run(cmd)

    gen = os.path.join(output_path, concti.GEN_FILE_PREAMBLE + str(curr_try) + misc.CPP_EXTENSION)

    if not os.path.isfile(gen):
        raise OSError(f"Error: the file {gen} could not be found")
    
    end = time.time()
    
    return out, err, src, gen, round(end - start, 3)


def test_idempotency(output_path):
    results = []

    for num_try in range(0, test.IDEMPOTENCY_DEPTH):
        try:
            temp_result, err, src, gen, time = idempotency_iteration(num_try, output_path)
        except OSError:
            break
        
        json_test = json.loads(parse_output(temp_result))
        temp_test = process_json(json_test, err)

        result_parsing = temp_test[test.PARSING][test.SUCCESS]
        result_codegen = temp_test[test.CODE_GENERATION][test.SUCCESS]
        
        # the parsing or code generation failed, skip to next iteration
        if not (result_parsing and result_codegen):
            continue
        
        # chamar diff se nao forem iguais
        eq = filecmp.cmp(src, gen)

        temp_test[test.SRC_FILE] = src
        temp_test[test.GEN_FILE] = gen
        temp_test[test.EQ] = eq
        temp_test[test.TIME] = time

        results.append(temp_test)

        if eq:
            break
    
    success = not (len(results) == test.IDEMPOTENCY_DEPTH or len(results) == 0)

    return results, success


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


def save_results(output_path, test):
    file_path = os.path.join(output_path, concti.JSON_RESULTS)

    with open(file_path, "w+") as f:
        json.dump(test, f)


def strip_ir(ir):
    ir_file = open(ir, "r")
    lines = []

    readline = ir_file.readline()

    while "; Function Attrs:" not in readline:
        if readline == '' or readline == "!llvm.module.flags":
            break

        readline = ir_file.readline()

        continue

    print("got out ot first while loop in strip_ir")
    
    line = ""

    while True:
        line = ir_file.readline()
        print("line = ")
        
        if "!llvm.module.flags" in line:
            break

        lines.append(line)

    print ("got out of second while loop in strip_ir")
    
    return ''.join(lines)


def print_test(processed_test):
    parsing     = 'N/A'
    code_gen    = 'N/A'
    idempotency = 'N/A'
    correctness = 'N/A'
    
    if test.PARSING in processed_test:
        if processed_test[test.PARSING][test.SUCCESS]:
            parsing = test.SUCCESS_MSG
        else:
            parsing = test.ERROR_MSG
    
    if test.CODE_GENERATION in processed_test:
        if processed_test[test.CODE_GENERATION][test.SUCCESS]:
            code_gen = test.SUCCESS_MSG
        else:
            code_gen = test.ERROR_MSG
    
    if test.IDEMPOTENCY in processed_test:
        if processed_test[test.IDEMPOTENCY][test.SUCCESS]:
            idempotency = test.SUCCESS_MSG
        else:
            idempotency = test.ERROR_MSG

    if test.CORRECTNESS in processed_test:
        if processed_test[test.CORRECTNESS][test.SUCCESS]:
            correctness = test.SUCCESS_MSG
        else:
            correctness = test.ERROR_MSG
    
    print(f"- PARSING = {parsing}")
    print(f"- CODE GENERATION = {code_gen}")
    print(f"- IDEMPOTENCY = {idempotency}")
    print(f"- CORRECTNESS = {correctness}\n")


if __name__ == '__main__':
    if (len(os.sys.argv) < 3):
        print("Usage:\n$ python3 cacti.py <test_folder> <transpiler>")
        exit(misc.EXIT_FAILURE)

    WORKING_DIR = str(os.getcwd()) + '/'
    INPUT_FOLDER = WORKING_DIR + str(os.sys.argv[1]).lower()
    
    TRANSPILER = str(os.sys.argv[2]).lower()

    paths_c98 = find_source_files(os.path.join(INPUT_FOLDER, concti.C98_STANDARD))
    paths_c11 = find_source_files(os.path.join(INPUT_FOLDER, concti.C11_STANDARD))
    paths_c17 = find_source_files(os.path.join(INPUT_FOLDER, concti.C17_STANDARD))
    paths_c20 = find_source_files(os.path.join(INPUT_FOLDER, concti.C20_STANDARD))

    paths = paths_c98 + paths_c11 + paths_c17 + paths_c20

    paths.sort()

    for source_path in paths:        
        rel_path = source_path[len(INPUT_FOLDER):]
        
        aux_path = 'output' + rel_path[0:len(rel_path) - 7]
        
        print(f"Running {rel_path}...")

        output_path = os.path.join(INPUT_FOLDER, aux_path)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        cmd = get_transpiler_cmd(source_path, output_path, concti.FLAG_DUMMY, 0)
        
        code, out, err = run(cmd)

        json_test = json.loads(parse_output(out))

        processed_test = process_json(json_test, err)
        
        # the test for code generation passed, which means we can test for idempotency and correctness
        if test.CODE_GENERATION in processed_test and processed_test[test.CODE_GENERATION][test.SUCCESS]:
            
            # start testing for idempotency
            results, success = test_idempotency(output_path)    

            processed_test[test.IDEMPOTENCY][test.RESULTS] = results
            processed_test[test.IDEMPOTENCY][test.SUCCESS] = success

            # start testing for correctness
            # start_correctness = time.time()
                        
            # ir_from_src, ir_from_gen, src_proc_code, gen_proc_code = test_correctness(source_path, output_path)
            # end_correctness = time.time()

            # time_correctness = round(end_correctness - start_correctness, 3)

            # # the clang process failed to execute, meaning correctness cannot be tested
            # if src_proc_code == misc.EXIT_FAILURE or gen_proc_code == misc.EXIT_FAILURE:
            #     processed_test[test.CORRECTNESS][test.SUCCESS] = False
            #     processed_test[test.CORRECTNESS][test.TIME] = time_correctness
            # else:
            #     stripped_src_ir = strip_ir(ir_from_src)
            #     stripped_gen_ir = strip_ir(ir_from_gen)

            #     processed_test[test.CORRECTNESS][test.SUCCESS] = stripped_src_ir == stripped_gen_ir
            #     processed_test[test.CORRECTNESS][test.TIME] = time_correctness
        
        
        save_results(output_path, processed_test)

        print_test(processed_test)
    