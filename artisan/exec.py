def artisan(params: dict) -> str: 
  return ['python3', 'artisan/artisan.py', params["file"]]