"""
app/path_setup.py
Agrega la raíz del proyecto al sys.path para que todas las páginas
de Streamlit puedan importar el paquete 'core' correctamente.
Importar este módulo al inicio de cada página.
"""
import sys
import os

# Directorio raíz del proyecto (dos niveles arriba de app/pages/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
