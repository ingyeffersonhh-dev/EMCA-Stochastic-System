"""
run.py
Script de arranque oficial del sistema EMCA.
Ejecutar desde la raíz del proyecto:
    python run.py
o directamente:
    streamlit run run.py
"""
import sys
import os

# Garantizar que la raíz del proyecto está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Re-usar el main de la app
exec(open(os.path.join(os.path.dirname(__file__), "app", "main.py"), encoding="utf-8").read())
