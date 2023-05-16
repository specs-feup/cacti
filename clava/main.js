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

// lara arguments
const file = laraArgs.file;
const outputFolder = laraArgs.output_folder;
const idempotencyTry = laraArgs.curr_try;
const debugMode = laraArgs.debug_mode;

console.log('\ntry='+idempotencyTry+'\n');

if (debugMode) {
  console.log("The script was called in debug mode.")
}

// change idempotencyTry name 

const genFileName = idempotencyTry == 0 ? SRC_FILE_PREAMBLE + CPP_EXTENSION : GEN_FILE_PREAMBLE + idempotencyTry + CPP_EXTENSION;

console.log("genfilename = " + genFileName);

let output = {};

Clava.pushAst();


// access the source file
try {
  output.name = Io.getPath(file).getParentFile().getName();

  Clava.addExistingFile(file);

  console.log(Query.root().dump);

  console.log('SUCCESS: I accessed the source file');
}
catch (error) {
  output.error = "An error occurred while trying to access the source file.";
  
  console.log('ERROR: I could not access the source file');
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

  console.log('SUCCESS: I parsed the source file');

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

if (debugMode == false)
  Io.deleteFolderContents(outputFolder)

// test the code generation
try {
  const start = Date.now();

  Query.search("file").getFirst().setName(genFileName);
  Clava.writeCode(outputFolder);
  Clava.popAst();

  console.log('SUCCESS: I generated the code')
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

  console.log('ERROR: I could not generate the code')
  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  throw error;
}

output.test_idempotency = {
  results: [],
  success: ''
};

output.test_correctness = {
  success: '',
  time: 0
};

console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);
