laraImport("lara.Io");
laraImport("clava.Clava");

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
  
  exit(1);
}


/* Test the parsing */

try {
  Clava.rebuild();

  output.test_parsing = {
    sucess: true,
    log: "The parsing of the source file was completed successfully."
  } 
} 
catch (error) {
  output.test_parsing = {
    sucess: false,
    log: "An error occurred while trying to parse the source file."
  }
  Io.writeJson(outputFolder + "/results.json", output);
  exit(1);
}


/* Test the code generation */

Io.deleteFolderContents(outputFolder)

try {
  Clava.writeCode(outputFolder);
  Clava.popAst();

  output.test_code_generation = {
    sucess: true,
    log: "The generation of the source code was completed succesfully."
  }
}
catch (error) {
  output.test_code_generation = {
    sucess: false,
    log: "An error occurred while trying to generate source code from the input file."
  }
  Io.writeJson(outputFolder + "/results.json", output);
}

Io.writeJson(outputFolder + "/results.json", output);
