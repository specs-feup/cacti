def build_av(params: dict) -> str:
  return "\"" + "{" + ",".join(["{}:{}".format(k, '\'' + v + '\'') for k, v in params.items()]) + "}" + "\""

def clava(params: dict) -> str:  
  return ['clava', 'clava/main.js', '-b', '2', '-nci', '-av', build_av(params)]
