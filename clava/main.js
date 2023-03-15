laraImport("lara.Io");
laraImport("weaver.Query");
laraImport("clava.Clava");

const EXIT_FAILURE = 1;

const CACTI_DELIMITER_BEGIN = 'CACTI_OUTPUT_BEGIN';
const CACTI_DELIMITER_END = 'CACTI_OUTPUT_END';

const file = laraArgs.file;
const outputFolder = laraArgs.outputFolder;

let output = {};

Clava.pushAst();

try {
  output.name = Io.getPath(file).getParentFile().getName();

  Clava.addExistingFile(file);
}
catch (error) {
  output.error = "An error occurred while trying to access the source file.";
  
  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  exit(EXIT_FAILURE);
}


/* Test the parsing */

try {
  Clava.rebuild();

  if (Query.search("file").get().length == 0) {
    throw new Error("An error occurred while trying to parse the source file.");
  }

  output.test_parsing = {
    success: true,
    log: "The parsing of the source code was completed successfully."
  };
}
catch (error) {
  output.test_parsing = {
    success: false,
    log: "An error occurred while trying to parse the source file."
  }

  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  exit(EXIT_FAILURE);
}


/* Test the code generation */

Io.deleteFolderContents(outputFolder)

try {
  Query.search("file").getFirst().setName("generated1.cpp");
  Clava.writeCode(outputFolder);
  Clava.popAst();

  output.test_code_generation = {
    success: true,
    log: "The generation of the source code was completed succesfully."
  };
}
catch (error) {
  output.test_code_generation = {
    success: false,
    log: "An error occurred while trying to generate source code from the input file."
  };

  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  exit(EXIT_FAILURE);
}

/* Test idempotency (generate the code) */

const generatedFile = laraArgs.outputFolder + 'generated1.cpp';
Clava.pushAst();

try {
  Clava.addExistingFile(generatedFile);
  Clava.rebuild();
  Query.search("file").getFirst().setName("generated2.cpp");
  Clava.writeCode(outputFolder);
  Clava.popAst();
}
catch (error) {
  output.test_idempotency = {
    success: false,
    log: "An error occurred while trying to generate source code from the first generated file for the idempotency test.",
  };
  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  exit(EXIT_FAILURE);
}


console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);
