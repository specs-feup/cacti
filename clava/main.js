laraImport("lara.Io");
laraImport("weaver.Query");
laraImport("clava.Clava");

/* CACTI constants */
const CACTI_DELIMITER_BEGIN = 'CACTI_OUTPUT_BEGIN';
const CACTI_DELIMITER_END   = 'CACTI_OUTPUT_END';

/* lara arguments */
const file = laraArgs.source_path;
const outputFolder = laraArgs.output_path;
const outputFilename = laraArgs.output_filename;
const debugMode = laraArgs.debug_mode;

let output = {};

Clava.pushAst();


/* step 1: access the source file */
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


/* step 2: parse the file */
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


if (debugMode == false)
  Io.deleteFolderContents(outputFolder)


/* step 3: generate code */
try {
  const start = Date.now();

  Query.search("file").getFirst().setName(outputFilename);
  Clava.writeCode(outputFolder);
  Clava.popAst();

  const end = Date.now();

  const time = (end - start)/1000.0;

  output.test_code_generation = {
    success: true,
    output_filename: outputFilename,
    output_folder: outputFolder,
    log: "The generation of the source code was completed succesfully.",
    time: time
  };
}
catch (error) {
  output.test_code_generation = {
    success: false,
    output_filename: outputFilename,
    output_folder: outputFolder,
    log: "An error occurred while trying to generate source code from the input file."
  };

  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  throw error;
}


/* add idempotency entry to the output json */
output.test_idempotency = {
  results: [],
  success: ''
};

/* add correctness entry to the output json */
output.test_correctness = {
  success: '',
  time: 0
};


/* output json */
console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);
