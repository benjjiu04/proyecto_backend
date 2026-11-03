from proyecto_integrado_backend.wsgi import application
from waitress import serve


if __name__ == "__main__":
  app_django = serve(application, host="0.0.0.0", port=8000)