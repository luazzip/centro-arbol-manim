// Centro de un árbol por eliminación de hojas capa por capa (estilo Kahn).
// Compilar: g++ -std=c++17 -O2 -Wall -o bin/centro_arbol src/centro_arbol.cpp
// Uso:      bin/centro_arbol data/ejemplo.txt traces/ejemplo.json
// Entrada:  n y luego n-1 líneas "u v" (nodos numerados desde 0).
// Salida:   traza JSON con cada capa, que consume la animación de Manim.

#include <algorithm>
#include <fstream>
#include <iostream>
#include <utility>
#include <vector>

using namespace std;

// Cola propia (arreglo + índice de frente): no se usa std::queue.
struct Cola {
    vector<int> datos;
    size_t frente = 0;
    void push(int x) { datos.push_back(x); }
    int pop() { return datos[frente++]; }
    int size() const { return (int)(datos.size() - frente); }
    bool empty() const { return frente == datos.size(); }
};

struct Capa {
    vector<int> eliminados;      // hojas que salen de la cola en esta capa
    vector<int> nuevas_hojas;    // nodos que quedan con grado 1 y entran a la cola
    vector<int> grados_antes;
    vector<int> grados_despues;
    int restantes_antes = 0;
    int restantes_despues = 0;
};

struct Resultado {
    vector<int> grados_iniciales;
    vector<int> hojas_iniciales;
    vector<Capa> capas;
    vector<int> centros;
};

// ---------------- Algoritmo principal: O(n) ----------------
Resultado centro_del_arbol(const vector<vector<int>>& ady) {
    int n = (int)ady.size();
    Resultado r;
    vector<int> grado(n);
    vector<bool> eliminado(n, false);
    for (int v = 0; v < n; v++) grado[v] = (int)ady[v].size();
    r.grados_iniciales = grado;

    if (n == 1) {                 // caso borde: el único nodo es el centro
        r.centros.push_back(0);
        return r;
    }

    Cola cola;
    for (int v = 0; v < n; v++)
        if (grado[v] == 1) {
            cola.push(v);
            r.hojas_iniciales.push_back(v);
        }

    int restantes = n;
    while (restantes > 2) {
        Capa capa;
        capa.grados_antes = grado;
        capa.restantes_antes = restantes;
        vector<int> candidatas;

        int tam = cola.size();    // solo las hojas de ESTA capa
        for (int i = 0; i < tam; i++) {
            int hoja = cola.pop();
            eliminado[hoja] = true;
            restantes--;
            capa.eliminados.push_back(hoja);
            for (int vecino : ady[hoja]) {
                if (eliminado[vecino]) continue;
                grado[vecino]--;
                if (grado[vecino] == 1) {
                    cola.push(vecino);
                    candidatas.push_back(vecino);
                }
            }
        }
        for (int v : candidatas)
            if (grado[v] == 1) capa.nuevas_hojas.push_back(v);

        capa.grados_despues = grado;
        capa.restantes_despues = restantes;
        r.capas.push_back(capa);
    }

    for (int v = 0; v < n; v++)
        if (!eliminado[v]) r.centros.push_back(v);
    return r;
}

// ---------------- BFS (solo para verificar y para el diámetro) ----------------
static vector<int> bfs(const vector<vector<int>>& ady, int origen, vector<int>* padre) {
    int n = (int)ady.size();
    vector<int> dist(n, -1);
    if (padre) padre->assign(n, -1);
    Cola cola;
    dist[origen] = 0;
    cola.push(origen);
    while (!cola.empty()) {
        int u = cola.pop();
        for (int v : ady[u]) {
            if (dist[v] == -1) {
                dist[v] = dist[u] + 1;
                if (padre) (*padre)[v] = u;
                cola.push(v);
            }
        }
    }
    return dist;
}

// ---------------- Escritura de la traza JSON ----------------
static void escribir_vector(ostream& os, const vector<int>& v) {
    os << "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i > 0) os << ", ";
        os << v[i];
    }
    os << "]";
}

static void escribir_json(ostream& os, int n, const vector<pair<int, int>>& aristas,
                          const Resultado& r, const vector<int>& ecc, int radio,
                          int diametro, const vector<int>& camino, bool ok) {
    os << "{\n";
    os << "  \"n\": " << n << ",\n";
    os << "  \"aristas\": [";
    for (size_t i = 0; i < aristas.size(); i++) {
        if (i > 0) os << ", ";
        os << "[" << aristas[i].first << ", " << aristas[i].second << "]";
    }
    os << "],\n";
    os << "  \"grados_iniciales\": "; escribir_vector(os, r.grados_iniciales); os << ",\n";
    os << "  \"hojas_iniciales\": ";  escribir_vector(os, r.hojas_iniciales);  os << ",\n";
    os << "  \"capas\": [\n";
    for (size_t i = 0; i < r.capas.size(); i++) {
        const Capa& c = r.capas[i];
        os << "    {\"capa\": " << i + 1;
        os << ", \"eliminados\": ";      escribir_vector(os, c.eliminados);
        os << ", \"nuevas_hojas\": ";    escribir_vector(os, c.nuevas_hojas);
        os << ", \"grados_antes\": ";    escribir_vector(os, c.grados_antes);
        os << ", \"grados_despues\": ";  escribir_vector(os, c.grados_despues);
        os << ", \"restantes_antes\": " << c.restantes_antes;
        os << ", \"restantes_despues\": " << c.restantes_despues << "}";
        os << (i + 1 < r.capas.size() ? ",\n" : "\n");
    }
    os << "  ],\n";
    os << "  \"centros\": ";          escribir_vector(os, r.centros); os << ",\n";
    os << "  \"excentricidad\": ";    escribir_vector(os, ecc);       os << ",\n";
    os << "  \"radio\": " << radio << ",\n";
    os << "  \"diametro\": " << diametro << ",\n";
    os << "  \"camino_diametro\": ";  escribir_vector(os, camino);    os << ",\n";
    os << "  \"verificacion_ok\": " << (ok ? "true" : "false") << "\n";
    os << "}\n";
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Uso: " << argv[0] << " entrada.txt [salida.json]\n";
        return 1;
    }
    ifstream entrada(argv[1]);
    if (!entrada) { cerr << "No se pudo abrir " << argv[1] << "\n"; return 1; }

    int n;
    if (!(entrada >> n) || n < 1) { cerr << "n invalido\n"; return 1; }
    vector<vector<int>> ady(n);
    vector<pair<int, int>> aristas;
    for (int i = 0; i < n - 1; i++) {
        int a, b;
        if (!(entrada >> a >> b) || a < 0 || b < 0 || a >= n || b >= n || a == b) {
            cerr << "Arista invalida en la linea " << i + 2 << "\n";
            return 1;
        }
        ady[a].push_back(b);
        ady[b].push_back(a);
        aristas.push_back({a, b});
    }

    vector<int> d0 = bfs(ady, 0, nullptr);
    for (int d : d0)
        if (d == -1) { cerr << "El grafo no es conexo: no es un arbol\n"; return 1; }

    // 1) Algoritmo (el que se anima)
    Resultado r = centro_del_arbol(ady);

    // 2) Verificación por fuerza bruta: excentricidad de cada nodo, O(n^2)
    vector<int> ecc(n);
    for (int s = 0; s < n; s++) {
        vector<int> d = bfs(ady, s, nullptr);
        ecc[s] = *max_element(d.begin(), d.end());
    }
    int radio = *min_element(ecc.begin(), ecc.end());
    vector<int> centros_bruta;
    for (int v = 0; v < n; v++)
        if (ecc[v] == radio) centros_bruta.push_back(v);
    bool ok = (centros_bruta == r.centros);

    // 3) Diámetro con dos BFS
    int u = (int)(max_element(d0.begin(), d0.end()) - d0.begin());
    vector<int> padre;
    vector<int> du = bfs(ady, u, &padre);
    int w = (int)(max_element(du.begin(), du.end()) - du.begin());
    int diametro = du[w];
    vector<int> camino;
    for (int x = w; x != -1; x = padre[x]) camino.push_back(x);

    ofstream archivo;
    ostream* salida = &cout;
    if (argc >= 3) {
        archivo.open(argv[2]);
        if (!archivo) { cerr << "No se pudo escribir " << argv[2] << "\n"; return 1; }
        salida = &archivo;
    }
    escribir_json(*salida, n, aristas, r, ecc, radio, diametro, camino, ok);

    cerr << "Centro(s):";
    for (int c : r.centros) cerr << " " << c;
    cerr << " | capas: " << r.capas.size()
         << " | verificacion por fuerza bruta: " << (ok ? "OK" : "FALLO") << "\n";
    return ok ? 0 : 2;
}