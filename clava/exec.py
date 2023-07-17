from os import path

def build_av(params: dict) -> str:
  return "\"" + "{" + ",".join(["{}:{}".format(k, '\'' + v + '\'') for k, v in params.items()]) + "}" + "\""

def clava(params: dict) -> list[str]:  
  return ['clava', path.join(__file__ + path.sep + "..", "main.js"), '-b', '2', '-nci', '-av', build_av(params)]
