def artisan(params: dict) -> str:
  return ['python3', 'artisan/artisan.py', params["source_path"], params["output_path"]]