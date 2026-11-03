from proyecto_integrado_backend.wsgi import application
from waitress import serve


if __name__ == "__main__":

  port = 8000
  host = "0.0.0.0"
  
  print(f"server iniciado escuchando en: {host}:{port}.")
  app_django = serve(application, host=host, port=port)