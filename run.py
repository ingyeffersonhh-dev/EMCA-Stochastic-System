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

# Re-usar el main de la app con el contexto de archivos correcto
main_path = os.path.join(os.path.dirname(__file__), "app", "main.py")
with open(main_path, "r", encoding="utf-8") as f:
    code = compile(f.read(), main_path, "exec")
exec(code, {"__file__": main_path, "__name__": "__main__"})

