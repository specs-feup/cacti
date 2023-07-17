from os import path

def artisan(params: dict) -> str: 
  return ['python3', path.join(__file__ + path.sep + "..", "artisan.py"), params["source_path"]]