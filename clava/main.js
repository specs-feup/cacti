laraImport("lara.Io");
laraImport("weaver.Query");
laraImport("clava.Clava");


// miscelleanous constants
const EXIT_FAILURE = 1;
const SRC_FILE_PREAMBLE = 'src';
const GEN_FILE_PREAMBLE = 'gen';
const CPP_EXTENSION = '.cpp';


// CACTI constants
const CACTI_DELIMITER_BEGIN = 'CACTI_OUTPUT_BEGIN';
const CACTI_DELIMITER_END   = 'CACTI_OUTPUT_END';
const CACTI_FLAG_SILENT     = '-s'


// lara arguments
const file = laraArgs.file;
const outputFolder = laraArgs.outputFolder;
const silent = laraArgs.silent;
const idempotencyTry = laraArgs.idempotencyTry;

const genFileName = idempotencyTry == 0 ? SRC_FILE_PREAMBLE + CPP_EXTENSION : GEN_FILE_PREAMBLE + idempotencyTry + CPP_EXTENSION;

let output = {};

Clava.pushAst();


// access the source file
try {
  output.name = Io.getPath(file).getParentFile().getName();

  Clava.addExistingFile(file);

  console.log(Query.root().dump);
}
catch (error) {
  output.error = "An error occurred while trying to access the source file.";
  
  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  throw error;
}


// test the parsing
try {
  const start = Date.now();

  const allFilesParsed = Clava.rebuild();

  const end = Date.now();

  if (allFilesParsed === false) 
    throw new Error("An error occurred while trying to parse the source file.");

  const time = (end - start)/1000.0

  output.test_parsing = {
    success: true,
    log: "The parsing of the source code was completed successfully.",
    time: time
  };
}
catch (error) {
  output.test_parsing = {
    success: false,
    log: "An error occurred while trying to parse the source file."
  }
  
  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  throw error;
}

if (!(silent == CACTI_FLAG_SILENT))
  Io.deleteFolderContents(outputFolder)

// test the code generation
try {
  const start = Date.now();

  Query.search("file").getFirst().setName(genFileName);
  Clava.writeCode(outputFolder);
  Clava.popAst();

  const end = Date.now();

  const time = (end - start)/1000.0;

  output.test_code_generation = {
    success: true,
    log: "The generation of the source code was completed succesfully.",
    time: time
  };
}
catch (error) {
  output.test_code_generation = {
    success: false,
    log: "An error occurred while trying to generate source code from the input file."
  };

  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  throw error;
}

// update the output json with the idempotency and correctness test objects
output.test_idempotency = {
  results: []
};

output.test_correctness = {
  success: '',
  time: 0
};

console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);
