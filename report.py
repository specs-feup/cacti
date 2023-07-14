import json
import os
import argparse
from enum import Enum

standardNameToIndex = {
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


class TestDetails:
    """Represents the details of one of the 4 test phases: Parsing, Code Generation, Idempotency or Correctness.
    Attention should be payed in respects to the time and tries attributes, as the idempotency test phase does not posses a "time" attribute and all other test phases do not possess a "tries" attribute.

    Attributes:
        name (string): The name of the test phase (parsing, code generation, idempotency or correctness).
        success (bool): Whether this test phase was successful or not.
        time (int): How many seconds it took the compiler to perform this task. Is -1 if the attribute is not applicable to the test or an error occurred. 
        tries (int): How many iterations it took for the code generation to converge. Is -1 if the attribute is not applicable to the test. 
    """

    def __init__(self, name: str, success: bool, time: int = -1, tries: int = -1):
        self.name: str = name
        self.success: bool = success
        self.time: int = time
        self.tries: int = tries

    def __str__(self):
        return "TestDetails <name = " + self.name + ", success = " + str(self.success) + ", time = " + str(self.time) + ", tries = " + str(self.tries) + ">"

    def __repr__(self):
        return "TestDetails <name = " + self.name + ", success = " + str(self.success) + ", time = " + str(self.time) + ", tries = " + str(self.tries) + ">"


class Test:
    """Represents a Test which includes its name (its parent folder's name as per our convention) and the details of all applicable test phases run.

    Attributes:
        name (str): Name of the test. As per our convention, this is the source file's parent folder's name.
        details (list[TestDetails]): A list containing the details of all applicable test phases that were run for this particular test.
    """

    def __init__(self, name: str, testDetails: list[TestDetails]):
        self.name: str = name
        self.details: list[TestDetails] = testDetails

    def __str__(self):
        return "Test <name = " + self.name + ", test details = " + str(self.details) + ">"

    def __repr__(self):
        return "Test <name = " + self.name + ", test details = " + str(self.details) + ">"


class Standard:
    """Contains all information regarding a standard, which has a name and can contain multiple tests.

    Attributes:
        name (str): The standard's name, i.e. c++11
        tests (list[Test]): A list containing all the tests associated with this standard.
    """

    def __init__(self, name: str, tests: list[Test]):
        self.name: str = name
        self.tests: list[Test] = tests

    def __str__(self):
        return "Standard <name = " + self.name + ", result = " + str(self.tests) + ">"

    def __repr__(self):
        return "Standard <name = " + self.name + ", result = " + str(self.tests) + ">"


trueCounter = 0
falseCounter = 0
unknownCounter = 0


def removeTestPrefix(string: str) -> str:
    """Removes test_ from the given string."""

    # remove test_
    reducedString = string[5:]
    latexString = reducedString.replace("_", "\_")
    return latexString


def escapeBackslash(string: str) -> str:
    """Adds a \\ before every underscore so that it is interpreted correctly in LaTeX."""

    latexString = string.replace("_", "\_")
    return latexString


def snakeToCamelCase(string: str) -> str:
    """Splits the given string on underscores and returns the equivalent in Camel Case"""
    words = list(map(lambda x: x.capitalize(), string.split("\_")))
    return "".join(words)


def latexBool(bool: bool) -> str:
    """Converts a boolean value to a String that can be used in LaTeX. The word is colored depending on the boolean value. Also updates global counters of tests passed/failed..."""
    if bool is True:
        latexBool = r"\textcolor{green}{True}"
        global trueCounter
        trueCounter += 1
        return latexBool
    elif bool is False:
        latexBool = r"\textcolor{red}{False}"
        global falseCounter
        falseCounter += 1
        return latexBool
    else:
        latexBool = r"N/A"
        global unknownCounter
        unknownCounter += 1
        return latexBool

def getStand(stand: Standard) -> int:
    return standardNameToIndex[stand.name]


def processDirectory(general_path: str) -> tuple[list[Test], list[Standard]]:
    # Ensure general path is absolute and minimal
    general_path = os.path.abspath(general_path)

    tests: list[Test] = []
    standards: list[Standard] = []
    for item in os.listdir(general_path):
        itemPath = os.path.join(general_path, item)
        if os.path.isdir(itemPath):
            if item in standardNameToIndex:  # Checks if the item's name corresponds to a standard
                tests.extend(processDirectory(itemPath)[0])
                tests.sort(key=lambda x: x.name)
                stand = Standard(item, tests)
                tests = []
                standards.append(stand)
            else:
                tests.extend(processDirectory(itemPath)[0])
        elif os.path.isfile(itemPath) and item.endswith('.json'):
            result = processFile(itemPath)
            tests.append(result)
    return (tests, standards)


def processFile(file_path: str) -> Test:
    with open(file_path) as json_file:  # reads the JSON file
        parsedJson = json.load(json_file)
        name = ""
        time = ""
        tests = []
        for key, value in parsedJson.items():
            if key == "name":
                name = parsedJson[key]
            elif key == "test_idempotency":
                test = TestDetails(key, parsedJson[key]["success"], tries=len(
                    parsedJson[key]["results"]))
                tests.append(test)
            else:
                if parsedJson[key]["success"]:
                    test = TestDetails(
                        key, parsedJson[key]["success"], parsedJson[key]["time"])
                else:
                    test = TestDetails(key, parsedJson[key]["success"])
                tests.append(test)

        result = Test(name, tests)
        return result

def getAllTests(standards: list[Standard]) -> list[Test]:
    tests = []
    for standard in standards:
        tests.extend(standard.tests)
    return tests

def findMostCompleteTestInfo(tests: list[Test]) -> tuple[Test, int]:
    exampleTest = None
    maxTestPhases = 0
    for test in tests:
        if (len(test.details) > maxTestPhases):
            maxTestPhases = len(test.details)
            exampleTest = test
    return (exampleTest, maxTestPhases)

def writeStandardTestResultRows(standard: Standard, f) -> None:
    for test in standard.tests:
        row = r"\textbf{{\fontsize{10}{12}\selectfont " + \
            escapeBackslash(test.name) + r"}}"
        for details in test.details:
            if (details.tries == -1):
                row += r'& {0}&{1}'.format(details.time if details.time != -1 else 'N/A',
                                            latexBool(details.success))
            else:
                row += r'& {0}&{1}'.format(details.tries,
                                            latexBool(details.success))
        row += r' \\[0.5ex]'
        f.write(row+"\n")

def writeStandards(standards: list[Standard], f) -> None:

    # since the first group of tests in some standards
    # fails on the Parsing, we need to retrieve all the possible tests
    # so the table is correctly formed
    exampleTest, maxNumOfTests = findMostCompleteTestInfo(getAllTests(standards))

    for standard in standards:
        f.write(r"\section{" + standard.name + r"}"+"\n")
        # start table with a column for source file's name and 2 columns per test
        f.write(r"\begin{xltabular}{\textwidth}{l")

        for x in range(1, maxNumOfTests + 1):
            f.write("cc")
        f.write(r"}" + "\n"+(r"\toprule")+"\n")

        # Write column with source files' names
        f.write(r"\multicolumn{1}{Y}{}"+"\n")

        # Writing header and creating test result columns witchery
        for details in exampleTest.details:
            f.write(r"& \multicolumn{2}{@{}c}{\textbf{" +
                    "{0}".format(snakeToCamelCase(removeTestPrefix(details.name))) + r"}}")

        f.write(r"\\"+"\n")
        f.write(r"\cmidrule{2-"+str(2*len(exampleTest.details)+1)+r"}")

        for details in exampleTest.details:
            if (details.tries == -1):
                f.write(
                    r"&\multicolumn{1}{@{}c}{Time}&\multicolumn{1}{@{}c}{Success}")
            else:
                f.write(
                    r"&\multicolumn{1}{@{}c}{Tries}&\multicolumn{1}{@{}c}{Success}")
        f.write(r"\\"+"\n")
        f.write(r"\midrule"+"\n")
        f.write(r"\endhead")

        
        # writing result rows
        writeStandardTestResultRows(standard, f)

        f.write(r"\bottomrule"+"\n")
        f.write(r"\end{xltabular}"+"\n")
        f.write(r"\newpage" + "\n")

def getAbsolutePercentageOfTestsPassed(tests: list[Test], numberOfTotalTestPhases: int) -> float:
    """Calculates the theoretically maximum number of test phases that could be passed, then divides the number of actually passed test phases by that number.
    Counts test phases that weren't run as failed.
    """

    maxPossiblePassedTestPhases: int = len(tests) * numberOfTotalTestPhases
    passedTestPhases: int = 0
    for test in tests:
        for details in test.details:
            if details.success == True: passedTestPhases += 1
    return (passedTestPhases / maxPossiblePassedTestPhases) * 100

def getPercentageOfTestsPassed(tests: list[Test]) -> float:
    """Checks how many test phases succeedeed, how many failed and calculates the percentage based on those two alone.
    Doesn't count with test phases that weren't run.
    """
    passedTestPhases: int = 0
    failedTestPhases: int = 0
    for test in tests:
        for details in test.details:
            if details.success == True: passedTestPhases += 1
            elif details.success == False: failedTestPhases += 1
    return (passedTestPhases / (passedTestPhases + failedTestPhases)) * 100

def writePercentages(standards: list[Standard], maxTestPhases: int, f) -> None:
    f.write(r"\section{Percentages}")
    f.write("Percentage of passed tests:\n")
    f.write(str(round(trueCounter/(falseCounter+trueCounter)*100,2))+r" \%")
    """
    f.write(r"\section{Percentages}")
    f.write(r"Note: In Absolute percentages test phases that were not run count as failed.\n\n")
    f.write(r"Absolute percentage of passed tests:\n")
    f.write(str(round(getAbsolutePercentageOfTestsPassed(getAllTests(standards), maxTestPhases), 2))+r" \%\n\n")
    f.write(r"Percentage of passed tests:\n")
    f.write(str(round(getPercentageOfTestsPassed(getAllTests(standards)), 2))+r" \%")
    for standard in standards:
        f.write(escapeBackslash("\\subsection{" + standard.name + "}"))
        f.write(r"Absolute percentage of passed tests:\n")
        f.write(str(round(getAbsolutePercentageOfTestsPassed(standard.tests, maxTestPhases), 2))+r" \%")
        f.write(r"Percentage of passed tests:\n")
        f.write(str(round(getPercentageOfTestsPassed(standard.tests), 2))+r" \%")
    """




if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Script to generate a LaTeX report based on CACTI's output")

    parser.add_argument('-S', '--source', dest="src_path", required=True,
                        help='path to the output directory created by CACTI')
    parser.add_argument('-T', '--transpiler', dest="transpiler", required=True,
                        help="name of the desired transpiler. inside the output directory there must be a directory with the transpiler's name")

    args = parser.parse_args()

    transpiler = args.transpiler

    # creates path to generate the latex file
    # latex_path = os.path.join(root_dir, "report.tex")
    f = open(transpiler+".tex", "w")

    # different test types folders
    general_path = os.path.join(args.src_path, transpiler)

    # write usepackages and title to the tex file
    f.write(r"\documentclass{article}"+"\n" +
            r"\usepackage{booktabs}"+"\n"+r"\usepackage{xltabular}"+"\n")
    f.write(r"\usepackage{xcolor}"+"\n")
    f.write(
        r"\usepackage[top=1.5cm,bottom=3cm,left=1.5cm,right=1cm,marginparwidth=1.75cm]{geometry}"+"\n"+r"\begin{document}"+"\n")
    f.write(r"\title{" + transpiler.capitalize() + r" Testing Results}"+"\n" +
            r"\maketitle"+"\n"+r"\newcolumntype{Y}{>{\centering\arraybackslash}X}"+"\n")

    standards: list[Standard] = processDirectory(general_path)[1]

    standards.sort(key=lambda x: getStand(x))
    _, maxTestPhases = findMostCompleteTestInfo(getAllTests(standards))
    writeStandards(standards, f)
    writePercentages(standards, maxTestPhases, f)
    f.write(r"\end{document}")