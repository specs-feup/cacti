import json
import os
import argparse
from enum import Enum

standard_name_to_index = {
    "c++98": 1,
    "c++11": 2,
    "c++14": 3,
    "c++17": 4,
    "c++20": 5,
    "c89": 6,
    "c99": 7,
    "c11": 8,
    "c23": 9,
}

class standards(Enum):
    stand_11 = 1
    stand_14 = 2
    stand_17 = 3
    stand_20 = 4
    stand_98 = 5
    extensions = 6
    cstand89 = 7
    cstand99 = 8
    cstand11 = 9
    cstand23 = 10

true_counter = 0
false_counter = 0
unknown_counter = 0

def latexTest(string):
    #remove test_
    reducedString= string[5:]
    latexString=reducedString.replace("_","\_").capitalize()
    return latexString

def latexSource(string):
    latexString=string.replace("_","\_").capitalize()
    return latexString

def latexCamelCase(string):
    words = string.split("\_",1)
    latexString = string
    if (len(words)>1):
        latexString = words[0]+" "+words[1].capitalize()
    return latexString


def latexBool(bool):
    if bool is True:
        latexBool= r"\textcolor{green}{True}"
        global true_counter
        true_counter+=1
        return latexBool
    elif bool is False:
        latexBool= r"\textcolor{red}{False}"
        global false_counter
        false_counter+=1
        return latexBool
    else:
        latexBool= r"N/A"
        global unknown_counter
        unknown_counter+=1
        return latexBool

def getStand(stand):
    return standard_name_to_index[stand.name]

def processDirectory(general_path):
    results = []
    standards = []
    for item in os.listdir(general_path):
        item_path = os.path.join(general_path, item)
        if os.path.isdir(item_path):
            if item in standard_name_to_index:  # checks if item corresponds to a standard
                results.extend(processDirectory(item_path)[0])
                results.sort(key=lambda x: x.name)
                stand = Standard(item, results)
                results = []
                standards.append(stand)
            else:
                results.extend(processDirectory(item_path)[0])
        elif os.path.isfile(item_path) and item.endswith('.json'):
            result = processFile(item_path)
            results.append(result)
    return [results,standards]
        

def processFile(file_path):
    with open(file_path) as json_file:  # reads the JSON file
        parsed_json = json.load(json_file)
        name = ""
        time = ""
        tests = []
        for key, value in parsed_json.items():
            if key == "name":
                name = parsed_json[key]
            elif key == "test_idempotency":
                test = Test(key, parsed_json[key]["success"], tries=len(parsed_json[key]["results"]))
                tests.append(test)
            else:
                if parsed_json[key]["success"]:
                    test = Test(key, parsed_json[key]["success"], parsed_json[key]["time"])
                else:
                    test = Test(key, parsed_json[key]["success"])
                tests.append(test)

        result = Result(name, tests)
        return result

class Standard:
    def __init__(self, name, result):
        self.name = name
        self.result = result 


class Result:
    def __init__(self, name, tests):
        self.name = name
        self.tests= tests
class Test:
    def __init__(self, name, success, time=0, tries=-1):
        self.name = name
        self.success = success
        self.time = time
        self.tries= tries

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Script to generate a LaTeX report based on CACTI's output")

    parser.add_argument('-S', '--source', dest="src_path", required=True, help='path to the output directory created by CACTI')
    parser.add_argument('-T', '--transpiler', dest="transpiler", required=True, help="name of the desired transpiler. inside the output directory there must be a directory with the transpiler's name")

    args = parser.parse_args()

    transpiler = args.transpiler

    # creates path to generate the latex file
    # latex_path = os.path.join(root_dir, "report.tex")
    f = open(transpiler+".tex", "w")

    # different test types folders
    general_path = os.path.join(args.src_path, transpiler)

    # write usepackages and title to the tex file
    f.write(r"\documentclass{article}"+"\n"+r"\usepackage{booktabs}"+"\n"+r"\usepackage{xltabular}"+"\n")
    f.write(r"\usepackage{xcolor}"+"\n")
    f.write(r"\usepackage[top=1.5cm,bottom=3cm,left=1.5cm,right=1cm,marginparwidth=1.75cm]{geometry}"+"\n"+r"\begin{document}"+"\n")
    f.write(r"\title{" + transpiler.capitalize() + r" Testing Results}"+"\n"+r"\maketitle"+"\n"+r"\newcolumntype{Y}{>{\centering\arraybackslash}X}"+"\n")
    

    


    standards = processDirectory(general_path)[1]
    
    standards.sort(key=lambda x: getStand(x))

    #since the first group of tests in some standards
    #fails on the Parsing, we need to retrieve all the possible tests
    #so the table is correctly formed

    exampleResult = []
    maxNumOfTests = 0
    for i in standards:

        for j in range(0, len(i.result)):
            if(len(i.result[j].tests) > maxNumOfTests):
                maxNumOfTests = len(i.result[j].tests)
                exampleResult = i.result[j]

    for standard in standards:
        f.write(r"\section{"+ standard.name.capitalize() + r"}"+"\n")
        # start table with a column for source file's name and 2 columns per test  
        f.write(r"\begin{xltabular}{\textwidth}{l")


        for x in range(1, maxNumOfTests + 1):
            f.write("cc")
        f.write(r"}"+ "\n"+(r"\toprule")+"\n")

        #column with source file's name
        f.write(r"\multicolumn{1}{Y}{}"+"\n")

        for test in exampleResult.tests:
            f.write(r"& \multicolumn{2}{@{}c}{\textbf{" + "{0}".format(latexCamelCase(latexTest(test.name))) + r"}}")

        f.write(r"\\"+"\n")
        f.write(r"\cmidrule{2-"+str(2*len(exampleResult.tests)+1)+r"}")

        for test in exampleResult.tests:
            if (test.tries == -1):
                f.write(r"&\multicolumn{1}{@{}c}{Time}&\multicolumn{1}{@{}c}{Success}")
            else:
                f.write(r"&\multicolumn{1}{@{}c}{Tries}&\multicolumn{1}{@{}c}{Success}")
        f.write(r"\\"+"\n")
        f.write(r"\midrule"+"\n")
        f.write(r"\endhead")

        # writing result rows
        for result in standard.result:
            row = r"\textbf{{\fontsize{10}{12}\selectfont " + latexSource(result.name) + r"}}"
            for test in result.tests:
                if (test.tries == -1):
                    row+= r'& {0}&{1}'.format(test.time, latexBool(test.success))
                else: 
                    row+= r'& {0}&{1}'.format(test.tries, latexBool(test.success))
            row += r' \\[0.5ex]'
            f.write(row+"\n")
        f.write(r"\bottomrule"+"\n")
        f.write(r"\end{xltabular}"+"\n")
        f.write(r"\newpage" + "\n")
    f.write(r"\section{Percentages}")
    f.write("Percentage of passed tests:\n")
    f.write(str(round(true_counter/(false_counter+true_counter)*100,2))+r" \%")
    f.write(r"\end{document}")
  