import pulp
from flask import Flask, render_template, request, jsonify


def resolver_problema_transporte(origenes, destinos, oferta, demanda, costos):
    """
    Resuelve un problema de transporte usando PuLP.
    """
    problema = pulp.LpProblem("Problema_de_Transporte", pulp.LpMinimize)

    x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", lowBound=0, cat=pulp.LpContinuous)
         for i in range(len(origenes)) for j in range(len(destinos))}

    problema += pulp.lpSum(costos[i][j] * x[i, j] for i in range(len(origenes)) for j in range(len(destinos)))

    for i in range(len(origenes)):
        problema += pulp.lpSum(x[i, j] for j in range(len(destinos))) == oferta[i]

    for j in range(len(destinos)):
        problema += pulp.lpSum(x[i, j] for i in range(len(origenes))) == demanda[j]

    problema.solve()

    resultado = {
        "estado": pulp.LpStatus[problema.status],
        "variables": {(origenes[i], destinos[j]): x[i, j].varValue for i in range(len(origenes)) for j in
                      range(len(destinos))},
        "costo_total": pulp.value(problema.objective)
    }
    return resultado


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/resolver', methods=['POST'])
def resolver():
    datos = request.json
    solucion = resolver_problema_transporte(
        datos['origenes'], datos['destinos'], datos['oferta'], datos['demanda'], datos['costos']
    )
    return jsonify(solucion)


if __name__ == '__main__':
    app.run(debug=True)
