def clava(source_path, output_path, silent, idempotencyTry):  
  return ['clava', 'clava/main.js', '-b', '2', '-nci', '-av', "\"{file:" + '\'' + source_path + '\'' + ",idempotencyTry:" + '\'' + str(idempotencyTry) + '\'' + ",silent:" + '\'' + silent + '\'' + ",outputFolder:" + '\'' + output_path + '\'' + "}\""]
