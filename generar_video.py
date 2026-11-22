#!/usr/bin/env python3
"""Compila el C++, genera las trazas JSON y renderiza el video de la Parte 2.
Uso: python generar_video.py [l|m|h|k] [nombre_traza]
     l=480p15 (rápido, para probar)  m=720p30  h=1080p60  k=4K
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
EXE = RAIZ / "bin" / ("centro_arbol.exe" if os.name == "nt" else "centro_arbol")
CARPETA_CALIDAD = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}


def correr(cmd, env=None):
    print(">", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, env=env)


def compilar():
    compilador = shutil.which("g++") or shutil.which("clang++")
    if compilador is None:
        sys.exit("No encontré g++ ni clang++. Instala un compilador de C++ (ver README).")
    EXE.parent.mkdir(exist_ok=True)
    correr([compilador, "-std=c++17", "-O0", "-g", "-static", "-Wall", "-o", EXE, RAIZ / "src" / "centro_arbol.cpp"])


def generar_trazas():
    (RAIZ / "traces").mkdir(exist_ok=True)
    for entrada in sorted((RAIZ / "data").glob("*.txt")):
        correr([EXE, entrada, RAIZ / "traces" / (entrada.stem + ".json")])


def renderizar(calidad, traza):
    env = dict(os.environ, TRAZA=str(RAIZ / "traces" / (traza + ".json")))
    correr([sys.executable, "-m", "manim", f"-q{calidad}", "--media_dir", RAIZ / "media",
            "-o", f"parte2_{traza}", RAIZ / "animacion" / "escena_ejecucion.py", "Parte2Ejecucion"],
           env=env)
    print("\nVideo listo en:",
          RAIZ / "media" / "videos" / "escena_ejecucion" / CARPETA_CALIDAD[calidad] / f"parte2_{traza}.mp4")


if __name__ == "__main__":
    calidad = sys.argv[1] if len(sys.argv) > 1 else "h"
    traza = sys.argv[2] if len(sys.argv) > 2 else "ejemplo"
    compilar()
    generar_trazas()
    renderizar(calidad, traza)