laraImport("lara.Io");
laraImport("clava.Clava");


const EXIT_FAILURE = 1;

const CACTI_DELIMITER_BEGIN = 'CACTI_OUTPUT_BEGIN';
const CACTI_DELIMITER_END   = 'CACTI_OUTPUT_END';

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
  
  exit(EXIT_FAILURE);
}


/* Test the parsing */

try {
  Clava.rebuild();

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
  Clava.writeCode(outputFolder);
  Clava.popAst();

  output.test_code_generation = {
    success: true,
    log: "The generation of the source code was completed succesfully."
  };

  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);
}
catch (error) {
  output.test_code_generation = {
    success: false,
    log: "An error occurred while trying to generate source code from the input file."
  };
    
  console.log(CACTI_DELIMITER_BEGIN + JSON.stringify(output) + CACTI_DELIMITER_END);

  exit(EXIT_FAILURE);
}

