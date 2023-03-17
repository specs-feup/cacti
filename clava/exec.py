def clava(source_path, output_path, silent, ntry):  
  return ['clava', 'clava/main.js', '-b', '2', '-nci', '-av', "\"{file:" + '\'' + source_path + '\'' + ",ntry:" + '\'' + str(ntry) + '\'' + ",silent:" + '\'' + silent + '\'' + ",outputFolder:" + '\'' + output_path + '\'' + "}\""]
