def clava(source_path, output_path):  
  return ['clava', 'clava/main.js', '-b', '2', '-nci', '-av', "\"{file:" + '\'' + source_path + '\'' + ",outputFolder:" + '\'' + output_path + '\'' + "}\""]
