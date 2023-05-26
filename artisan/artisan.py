import shutil
import os
import sys
import subprocess
import json
import re

def copy_temp_file(source_file):

    output_path = source_file.replace("cacti_tests", "cacti_tests/output/artisan")

    file_name = source_file.split("/")[-2]

    script_directory = os.path.dirname(__file__)


    temp_file = os.path.join(script_directory, 'src.cpp')


    os.chdir(script_directory)

    # Copy src.cpp to artisan directory
    
    shutil.copy2(source_file, temp_file)

    proc = subprocess.run(['artisan', 'script.py'], capture_output=True, text=True)


    stdout = proc.stdout
    stderr = proc.stderr 

    pattern = r"CACTI:(.*?):CACTI"
    output = re.findall(pattern, stdout, re.DOTALL)


    success = "Error" not in output[0]

    test_parsing = {
        "success": success,
        "log": output[0],
        "time": output[1]
    }

    log = ""
    time = ""

    if(success):
        success = "Error" not in output[2]
        log = output[2]
        time = output[3]
    else: 
        log=stdout

    if(success):
        with open(output_path, "w") as file:
            file.write(output[4])

    test_code_generation = {
        "success": success if success is True else "",
        "log": log,
        "time": time
    }


    test_idempotency = {
        "success": "",
        "tries": "",
        "results": ""
    }

    test_correctness = {
        "success": ""
    }

    result = {
       "name": file_name,
       "test_parsing": test_parsing,
       "test_code_generation": test_code_generation,
       "test_idempotency": test_idempotency,
       "test_correctness": test_correctness
    }

    

    json_result = json.dumps(result)

    print("CACTI_OUTPUT_BEGIN" + json_result + "CACTI_OUTPUT_END")

    # delete src.cpp
    os.remove(temp_file)

    

if __name__ == '__main__':

    source_file = sys.argv[1]
    copy_temp_file(source_file)
