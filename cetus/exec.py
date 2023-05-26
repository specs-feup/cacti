from os.path import join

def cetus(params: dict) -> list[str]:  
  return ['cetus', str(params["source_path"]), join(str(params["output_path"]), str(params["output_filename"]))]
