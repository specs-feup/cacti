

laraImport("lara.Io");
laraImport("weaver.Query");
laraImport("clava.Clava");


// miscelleanous constants
const EXIT_FAILURE = 1;
const GEN_FILE_PREAMBLE = 'gen';
const CPP_EXTENSION = '.cpp';


// CACTI consntants
const CACTI_DELIMITER_BEGIN = 'CACTI_OUTPUT_BEGIN';
const CACTI_DELIMITER_END   = 'CACTI_OUTPUT_END';
const CACTI_FLAG_SILENT     = '-s'


// lara arguments
const file = laraArgs.file;
const outputFolder = laraArgs.outputFolder;
const silent = laraArgs.silent;
const idempotencyTry = laraArgs.ntry;


let output = {};

Clava.pushAst();


// access the source file
try {
  output.name = Io.getPath(file).getParentFile().getName();

  Clava.addExistingFile(file);
}
catch (error) {
  output.error = "An error occurred while trying to access the source file.";
  
  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  exit(EXIT_FAILURE);
}


// test the parsing
try {
  const allFilesParsed = Clava.rebuild();

  if (allFilesParsed === false) {
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
  
  if (!(silent == CACTI_FLAG_SILENT)) {
    console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);
  }

  exit(EXIT_FAILURE);
}

if (!(silent == CACTI_FLAG_SILENT))
  Io.deleteFolderContents(outputFolder)

// test the code generation
try {
  Query.search("file").getFirst().setName(GEN_FILE_PREAMBLE + idempotencyTry + CPP_EXTENSION);
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

  if (!(silent == CACTI_FLAG_SILENT))
    console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  exit(EXIT_FAILURE);
}

// update the output json with the idempotency and correctness test objects
output.test_idempotency = {
  success: '',
  tries: 0
};

output.test_correctness = {
  success: '',
  log: ''
};

if (!(silent == CACTI_FLAG_SILENT))
  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);
