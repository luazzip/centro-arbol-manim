"""Tema visual compartido por las tres partes del video."""
import numpy as np
from manim import *

FONDO = "#0E1116"
COLOR_NODO = "#3B82F6"        # azul: nodo normal
COLOR_HOJA = "#F59E0B"        # ámbar: hoja (grado 1)
COLOR_ELIMINADO = "#EF4444"   # rojo: se va a eliminar
COLOR_CENTRO = "#22C55E"      # verde: centro
COLOR_DIAMETRO = "#A855F7"    # morado: camino del diámetro
COLOR_ARISTA = "#6B7280"
COLOR_ARISTA_TENUE = "#222831"
COLOR_TENUE = "#4B5563"       # elementos ya eliminados
COLOR_TEXTO = "#E5E7EB"
COLOR_SUAVE = "#9CA3AF"
COLOR_TEXTO_OSCURO = "#0B0F14"
COLOR_CELDA = "#161B22"
RADIO_NODO = 0.28


def calcular_posiciones(n, aristas, raiz, ancho=6.5, alto=3.6):
    """Dibuja el árbol por niveles, con la raíz arriba. Devuelve {nodo: np.array([x, y, 0])}."""
    ady = [[] for _ in range(n)]
    for a, b in aristas:
        ady[a].append(b)
        ady[b].append(a)

    hijos = [[] for _ in range(n)]
    profundidad = [0] * n
    visto = [False] * n
    visto[raiz] = True
    orden = [raiz]
    i = 0
    while i < len(orden):
        u = orden[i]
        i += 1
        for v in ady[u]:
            if not visto[v]:
                visto[v] = True
                profundidad[v] = profundidad[u] + 1
                hijos[u].append(v)
                orden.append(v)

    x = [0.0] * n
    hojas = [0]

    def colocar(u):
        if not hijos[u]:
            x[u] = float(hojas[0])
            hojas[0] += 1
        else:
            for h in hijos[u]:
                colocar(h)
            x[u] = (x[hijos[u][0]] + x[hijos[u][-1]]) / 2

    colocar(raiz)
    max_x = max(hojas[0] - 1, 1)
    max_prof = max(profundidad)
    paso_x = min(ancho / max_x, 1.3)
    paso_y = min(alto / max(max_prof, 1), 1.4)
    centro_x = (hojas[0] - 1) / 2
    return {
        v: np.array([(x[v] - centro_x) * paso_x, (max_prof / 2 - profundidad[v]) * paso_y, 0.0])
        for v in range(n)
    }