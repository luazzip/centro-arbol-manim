"""
Parte 2 (Integrante 2): animación de la ejecución del algoritmo.
Lee la traza JSON generada por src/centro_arbol.cpp y anima cada capa.

Uso (desde la raíz del repo):
    manim -pqh animacion/escena_ejecucion.py Parte2Ejecucion
Otra traza (PowerShell):  $env:TRAZA="traces/camino4.json"
Otra traza (bash):        TRAZA=traces/camino4.json manim ...
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *
from tema import *

RAIZ_REPO = Path(__file__).resolve().parent.parent
RUTA_TRAZA = Path(os.environ.get("TRAZA", RAIZ_REPO / "traces" / "ejemplo.json"))

VELOCIDAD = 1.0   # >1 = más lento, <1 = más rápido (todo el video se escala)
PANEL_X = 0.9     # borde izquierdo del panel derecho
COLA_Y = -0.1


class Parte2Ejecucion(Scene):
    # ------------------------------------------------------------ utilidades
    def jugar(self, *anims, t=1.0):
        t *= VELOCIDAD
        self.duracion += t
        self.play(*anims, run_time=t)

    def esperar(self, t=1.0):
        t *= VELOCIDAD
        self.duracion += t
        self.wait(t)

    def cap(self, texto):
        """Subtítulo inferior. Devuelve la lista de animaciones para meter en un play."""
        nuevo = Text(texto, font_size=26, color=COLOR_TEXTO)
        if nuevo.width > 13:
            nuevo.scale_to_fit_width(13)
        nuevo.to_edge(DOWN, buff=0.3)
        if self.subtitulo is None:
            anims = [FadeIn(nuevo, shift=UP * 0.15)]
        else:
            anims = [FadeOut(self.subtitulo, shift=UP * 0.15), FadeIn(nuevo, shift=UP * 0.15)]
        self.subtitulo = nuevo
        return anims

    def color_nodo(self, v, color):
        return self.nodos[v][0].animate.set_fill(color).set_stroke(color)

    def cambiar(self, atributo, texto):
        viejo = getattr(self, atributo)
        nuevo = Text(texto, font_size=36, color=COLOR_TEXTO).move_to(viejo)
        setattr(self, atributo, nuevo)
        return ReplacementTransform(viejo, nuevo)

    def bloque(self, lineas, y):
        grupo = VGroup(*[Text(txt, font_size=tam, color=col) for txt, tam, col in lineas])
        grupo.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        if grupo.width > 6.0:
            grupo.scale_to_fit_width(6.0)
        grupo.move_to([PANEL_X, y, 0], aligned_edge=LEFT)
        return grupo

    # ------------------------------------------------------------ construcción
    def construir_arbol(self):
        t = self.traza
        pos = calcular_posiciones(self.n, t["aristas"], t["centros"][0])
        desplazamiento = np.array([-3.35, 0.15, 0.0])
        self.pos = {v: p + desplazamiento for v, p in pos.items()}

        self.aristas = {}
        for a, b in t["aristas"]:
            clave = (min(a, b), max(a, b))
            self.aristas[clave] = Line(self.pos[a], self.pos[b], color=COLOR_ARISTA, stroke_width=3)
            self.aristas[clave].set_z_index(0)

        self.nodos = {}
        for v in range(self.n):
            circ = Circle(radius=RADIO_NODO, color=COLOR_NODO, fill_opacity=1, stroke_width=3)
            circ.move_to(self.pos[v])
            txt = Text(str(v), font_size=22, color=COLOR_TEXTO_OSCURO, weight=BOLD).move_to(self.pos[v])
            self.nodos[v] = VGroup(circ, txt).set_z_index(2)

    def construir_panel(self):
        n = self.n
        w = min(0.55, 5.8 / n)
        self.w_celda = w
        self.fs = 22 if w >= 0.45 else 16
        self.cuad_grado, self.txt_grado = {}, {}

        cuadros = VGroup()
        for v in range(n):
            c = Square(side_length=w, color=COLOR_SUAVE, stroke_width=2).set_fill(COLOR_CELDA, 1)
            self.cuad_grado[v] = c
            cuadros.add(c)
        cuadros.arrange(RIGHT, buff=0).move_to([PANEL_X, 1.3, 0], aligned_edge=LEFT)

        indices = VGroup(*[
            Text(str(v), font_size=16, color=COLOR_SUAVE).next_to(self.cuad_grado[v], UP, buff=0.08)
            for v in range(n)
        ])
        for v in range(n):
            self.txt_grado[v] = Text(str(self.grado[v]), font_size=self.fs, color=COLOR_TEXTO)
            self.txt_grado[v].move_to(self.cuad_grado[v])

        etiqueta_g = Text("grado[v]", font_size=24, color=COLOR_TEXTO)
        etiqueta_g.move_to([PANEL_X, 2.5, 0], aligned_edge=LEFT)

        marco = Rectangle(width=5.8, height=w + 0.14, color=COLOR_SUAVE, stroke_width=1.5)
        marco.move_to([PANEL_X, COLA_Y, 0], aligned_edge=LEFT)
        etiqueta_c = Text("cola de hojas", font_size=24, color=COLOR_TEXTO)
        etiqueta_c.move_to([PANEL_X, COLA_Y + 0.55, 0], aligned_edge=LEFT)
        self.cola_origen = np.array([PANEL_X + 0.07 + w / 2, COLA_Y, 0.0])
        self.cola_items = []

        lbl_rest = Text("nodos restantes:", font_size=26, color=COLOR_TEXTO)
        lbl_rest.move_to([PANEL_X, -1.2, 0], aligned_edge=LEFT)
        self.num_rest = Text(str(self.restantes), font_size=36, color=COLOR_TEXTO)
        self.num_rest.next_to(lbl_rest, RIGHT, buff=0.25)

        lbl_capa = Text("capa actual:", font_size=26, color=COLOR_TEXTO)
        lbl_capa.move_to([PANEL_X, -1.95, 0], aligned_edge=LEFT)
        self.num_capa = Text("0", font_size=36, color=COLOR_TEXTO)
        self.num_capa.next_to(lbl_capa, RIGHT, buff=0.25)

        regla = Text("mientras restantes > 2: quitar todas las hojas", font_size=22, color=COLOR_SUAVE)
        regla.move_to([PANEL_X, -2.75, 0], aligned_edge=LEFT)

        self.panel_fijo = VGroup(etiqueta_g, cuadros, indices, marco, etiqueta_c, lbl_rest, lbl_capa, regla)

    def crear_item_cola(self, v, slot):
        w = self.w_celda
        cuadro = Square(side_length=w * 0.92, color=COLOR_HOJA, stroke_width=2).set_fill(COLOR_HOJA, 0.25)
        num = Text(str(v), font_size=self.fs, color=COLOR_TEXTO).move_to(cuadro)
        item = VGroup(cuadro, num)
        item.move_to(self.cola_origen + RIGHT * slot * w)
        return item

    def encolar(self, nodos):
        anims = []
        for v in nodos:
            item = self.crear_item_cola(v, len(self.cola_items))
            self.cola_items.append(item)
            anims.append(FadeIn(item, shift=RIGHT * 0.3))
        return anims

    # ------------------------------------------------------------ escena
    def construct(self):
        self.camera.background_color = FONDO
        self.duracion = 0.0
        self.subtitulo = None
        with open(RUTA_TRAZA, encoding="utf-8") as f:
            self.traza = json.load(f)
        self.n = self.traza["n"]
        self.grado = list(self.traza["grados_iniciales"])
        self.restantes = self.n
        self.vivos = set(range(self.n))

        self.fase_presentacion()    # 0:45 - 0:55
        self.fase_ejecucion()       # 0:55 - 1:25
        self.fase_comprobacion()    # 1:25 - 1:35
        print(f"\n>>> Duración de la Parte 2: {self.duracion:.1f} s (ajusta VELOCIDAD si hace falta)\n")

    # ---- 0:45 - 0:55: presentar árbol + arreglo de grados
    def fase_presentacion(self):
        n = self.n
        titulo = Text("Centro de un árbol: eliminar hojas por capas", font_size=32, color=COLOR_TEXTO)
        titulo.to_edge(UP, buff=0.3)
        self.construir_arbol()
        self.construir_panel()

        self.jugar(FadeIn(titulo, shift=DOWN * 0.2), t=0.8)
        if self.aristas:
            self.jugar(LaggedStart(*[Create(e) for e in self.aristas.values()], lag_ratio=0.15), t=1.5)
        self.jugar(LaggedStart(*[FadeIn(self.nodos[v], scale=0.5) for v in range(n)], lag_ratio=0.1),
                   *self.cap(f"Árbol de ejemplo: n = {n} nodos y {n - 1} aristas"), t=1.6)
        self.esperar(1.0)
        self.jugar(FadeIn(self.panel_fijo),
                   *[FadeIn(m) for m in self.txt_grado.values()],
                   FadeIn(self.num_rest), FadeIn(self.num_capa),
                   *self.cap("grado[v] = cantidad de vecinos del nodo v"), t=1.2)
        self.esperar(3.9)

    # ---- 0:55 - 1:25: ejecución capa por capa
    def fase_ejecucion(self):
        t = self.traza
        capas = t["capas"]
        if not capas:
            self.marcar_centros("Con n ≤ 2 no se entra al bucle: esos nodos ya son el centro")
            return

        hojas = t["hojas_iniciales"]
        self.jugar(*self.cap("Hojas = nodos de grado 1: se marcan y se meten a la cola"),
                   *[self.color_nodo(v, COLOR_HOJA) for v in hojas], t=1.0)
        self.jugar(LaggedStart(*self.encolar(hojas), lag_ratio=0.25), t=1.6)
        self.esperar(1.2)

        for k, capa in enumerate(capas, start=1):
            self.ejecutar_capa(k, capa)
        self.marcar_centros()

    def ejecutar_capa(self, k, capa):
        elim = capa["eliminados"]
        elim_set = set(elim)
        self.vivos -= elim_set

        # a) las hojas de la cola se marcan en rojo
        self.jugar(*self.cap(f"Capa {k}: se sacan de la cola todas las hojas a la vez"),
                   *[self.color_nodo(v, COLOR_ELIMINADO) for v in elim],
                   self.cambiar("num_capa", str(k)), t=1.2)

        # b) se eliminan de golpe: nodos y aristas se apagan, la cola se vacía
        anims = []
        for v in elim:
            anims += [
                self.nodos[v][0].animate.set_fill(FONDO).set_stroke(COLOR_TENUE),
                self.nodos[v][1].animate.set_color(COLOR_TENUE),
                self.cuad_grado[v].animate.set_stroke(COLOR_TENUE),
                self.txt_grado[v].animate.set_color(COLOR_TENUE),
            ]
        for clave, arista in self.aristas.items():
            if clave[0] in elim_set or clave[1] in elim_set:
                anims.append(arista.animate.set_color(COLOR_ARISTA_TENUE))
        anims += [FadeOut(item, shift=LEFT * 0.3) for item in self.cola_items]
        anims.append(self.cambiar("num_rest", str(capa["restantes_despues"])))
        self.cola_items = []
        self.jugar(*anims, t=1.3)

        # c) se actualizan los grados de los vecinos
        cambios = [v for v in sorted(self.vivos)
                   if capa["grados_despues"][v] != capa["grados_antes"][v]]
        if cambios:
            self.jugar(*self.cap("Cada hoja eliminada le resta 1 al grado de su vecino"),
                       *[Indicate(self.nodos[v], color=COLOR_HOJA, scale_factor=1.25) for v in cambios],
                       t=1.0)
            anims = []
            for v in cambios:
                nuevo = Text(str(capa["grados_despues"][v]), font_size=self.fs, color=COLOR_TEXTO)
                nuevo.move_to(self.cuad_grado[v])
                anims.append(ReplacementTransform(self.txt_grado[v], nuevo))
                anims.append(Indicate(self.cuad_grado[v], color=COLOR_HOJA, scale_factor=1.2))
                self.txt_grado[v] = nuevo
            self.jugar(*anims, t=1.2)

        # d) los que quedan con grado 1 son hojas nuevas y entran a la cola
        nuevas = capa["nuevas_hojas"]
        if nuevas:
            self.jugar(*self.cap("Los nodos que quedan con grado 1 son hojas nuevas: entran a la cola"),
                       *[self.color_nodo(v, COLOR_HOJA) for v in nuevas],
                       LaggedStart(*self.encolar(nuevas), lag_ratio=0.3), t=1.6)
        self.esperar(1.6)

        self.grado = list(capa["grados_despues"])
        self.restantes = capa["restantes_despues"]

    def marcar_centros(self, texto=None):
        centros = self.traza["centros"]
        if texto is None:
            if len(centros) == 1:
                texto = f"Queda 1 nodo (≤ 2): el centro es el nodo {centros[0]}"
            else:
                texto = f"Quedan 2 nodos (≤ 2): los centros son {centros[0]} y {centros[1]}"
        self.jugar(*self.cap(texto), *[self.color_nodo(c, COLOR_CENTRO) for c in centros], t=1.2)
        self.jugar(*[Flash(self.nodos[c].get_center(), color=COLOR_CENTRO, flash_radius=0.6)
                     for c in centros], t=1.0)
        self.esperar(1.9)

    # ---- 1:25 - 1:35: comprobación visual con excentricidades y diámetro
    def fase_comprobacion(self):
        t = self.traza
        n = self.n
        centros = t["centros"]
        ecc = t["excentricidad"]

        # 1) se limpia el panel y se restaura el árbol completo
        fuera = [FadeOut(self.panel_fijo),
                 *[FadeOut(m) for m in self.txt_grado.values()],
                 FadeOut(self.num_rest), FadeOut(self.num_capa),
                 *[FadeOut(m) for m in self.cola_items]]
        restaurar = []
        for v in range(n):
            restaurar.append(self.color_nodo(v, COLOR_CENTRO if v in centros else COLOR_NODO))
            restaurar.append(self.nodos[v][1].animate.set_color(COLOR_TEXTO_OSCURO))
        for e in self.aristas.values():
            restaurar.append(e.animate.set_color(COLOR_ARISTA))
        self.jugar(*self.cap("Comprobación visual: el centro tiene la excentricidad mínima"),
                   *fuera, *restaurar, t=1.3)

        # 2) excentricidad de cada nodo
        etiquetas = {}
        for v in range(n):
            et = Text(str(ecc[v]), font_size=20, color=COLOR_TEXTO)
            et.next_to(self.nodos[v], UR, buff=0.02)
            et.set_stroke(FONDO, width=4, background=True)
            et.set_z_index(3)
            etiquetas[v] = et
        b1 = self.bloque([("excentricidad(v)", 30, COLOR_TEXTO),
                          ("= distancia máxima de v a cualquier otro nodo", 22, COLOR_SUAVE)], 1.7)
        self.jugar(*self.cap("Excentricidad = distancia máxima desde cada nodo (número sobre el nodo)"),
                   LaggedStart(*[FadeIn(etiquetas[v], scale=0.5) for v in range(n)], lag_ratio=0.08),
                   FadeIn(b1), t=1.6)
        self.esperar(1.0)

        # 3) el centro tiene la excentricidad mínima
        b2 = self.bloque([(f"radio = excentricidad mínima = {t['radio']}", 26, COLOR_CENTRO),
                          ("el centro es el nodo con excentricidad igual al radio", 22, COLOR_SUAVE)], 0.2)
        anims = []
        for v in range(n):
            if v in centros:
                anims.append(etiquetas[v].animate.set_color(COLOR_CENTRO).scale(1.5))
            else:
                anims.append(etiquetas[v].animate.set_color(COLOR_TENUE))
        self.jugar(*self.cap(f"El centro tiene la menor excentricidad: {t['radio']}"),
                   *anims, FadeIn(b2),
                   *[Flash(self.nodos[c].get_center(), color=COLOR_CENTRO, flash_radius=0.6) for c in centros],
                   t=1.3)
        self.esperar(1.0)

        # 4) relación con el diámetro
        camino = t["camino_diametro"]
        anims = []
        for a, b in zip(camino, camino[1:]):
            anims.append(self.aristas[(min(a, b), max(a, b))].animate.set_stroke(COLOR_DIAMETRO, width=6))
        b3 = self.bloque([(f"diámetro = {t['diametro']} aristas (camino morado)", 26, COLOR_DIAMETRO),
                          ("el centro es el punto medio de ese camino", 22, COLOR_SUAVE)], -1.3)
        self.jugar(*self.cap(f"El diámetro mide {t['diametro']} aristas y el centro está en su punto medio"),
                   *anims, FadeIn(b3), t=1.6)
        self.esperar(2.2)