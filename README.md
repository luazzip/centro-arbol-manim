# Centro de un árbol: animación con Manim

Proyecto Final 2 – CS2023 Algoritmos y Estructuras de Datos (UTEC, 2026-2) – Grupo 7.
Algoritmo: **centro de un árbol** por eliminación iterativa de hojas, O(n).
La animación la genera una traza JSON producida por la implementación real en C++.

## Software requerido
- Python 3.10–3.12 y `pip install -r requirements.txt` (Manim Community)
- g++ (C++17)
- ffmpeg (solo si Manim lo pide)

## Compilar y ejecutar
```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1      Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# Todo en uno (compila, genera trazas y renderiza). Calidad: l | m | h
python generar_video.py h

# O paso a paso:
mkdir -p bin traces
g++ -std=c++17 -O2 -Wall -o bin/centro_arbol src/centro_arbol.cpp
bin/centro_arbol data/ejemplo.txt traces/ejemplo.json      # Windows: bin\centro_arbol.exe
manim -pqh animacion/escena_ejecucion.py Parte2Ejecucion
```
El video queda en `media/videos/escena_ejecucion/1080p60/`.