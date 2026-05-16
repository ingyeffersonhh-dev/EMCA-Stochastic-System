# 🏗️ EMCA — Sistema de Información Estocástico para Pilotes

Sistema de apoyo a la toma de decisiones para planificación de perforación de pilotes, basado en simulación de eventos discretos y métodos Monte Carlo.

## Stack Tecnológico
- **UI**: Streamlit
- **Simulación**: SimPy (eventos discretos)
- **Estadística**: NumPy, SciPy, SALib
- **Visualización**: Plotly Express
- **Validación**: Pydantic v2
- **Exportación**: OpenPyXL

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate   # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app/main.py
```

## Arquitectura de Módulos

```
Módulo 1: Parametrización  →  Módulo 2: Simulación  →  Módulo 3: Dashboard
(Entrada de datos)             (Motor estocástico)        (Visualización gerencial)
```

## Estructura del Proyecto

```
EMCA/
├── app/                   # Frontend Streamlit
│   ├── main.py
│   ├── pages/
│   └── components/
├── core/                  # Lógica pura (sin UI)
│   ├── models/            # Pydantic schemas
│   ├── stochastic/        # Distribuciones y sensibilidad
│   ├── simulation/        # Motor SimPy
│   └── analytics/         # KPIs, Gantt, exportación
├── data/                  # Escenarios y resultados
├── tests/                 # Pruebas unitarias
├── config/                # Configuración global
└── exports/               # PDF y Excel generados
```

## Uso Rápido

1. Ingrese los parámetros del proyecto en **Módulo 1**
2. Configure el número de réplicas y ejecute en **Módulo 2**
3. Analice el Gantt, histogramas y alertas en **Módulo 3**
