import sys
def artisan(params: dict) -> str:
  if("--of" not in sys.argv):
    return ['python3', 'artisan/artisan.py', params["source_path"], "../"]
  return ['python3', 'artisan/artisan.py', params["source_path"], params["output_path"]]