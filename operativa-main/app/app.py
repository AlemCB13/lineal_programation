from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from lineal.LinearProgrammingSolver import LinearProgrammingSolver
from gemini.GeminiAnaliser import GeminiAnaliser
from redes.NetworkOptimization import NetworkOptimization

# Configurar la API de Gemini
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("No se encontró la clave de API de Google Gemini. Configúrala en GOOGLE_API_KEY.")

genai.configure(api_key="GENAI_API_KEY")

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/objective')
def objetivo():
    return render_template('objetivo.html')


@app.route('/linear', methods=['GET', 'POST'])
def linear():
    resultado = None
    analisis = None

    if request.method == 'POST':
        # Extraer datos del formulario
        funcion_objetivo = request.form.get('funcion_objetivo')
        objetivo = request.form.get('objetivo')
        restricciones_raw = request.form.get('restriccion')

        # Procesar restricciones
        restricciones = [r.strip() for r in restricciones_raw.split('\n') if r.strip()]

        if not funcion_objetivo or not objetivo or not restricciones:
            return "Faltan datos en el formulario.", 400

        # Resolver el problema
        resultado = LinearProgrammingSolver.resolver_problema(funcion_objetivo, objetivo, restricciones)

        # Obtener el análisis con Gemini
        analisis = GeminiAnaliser.interpretar_sensibilidad(resultado)

    return render_template('linear-programming.html', resultado=resultado, analisis=analisis)

##TRANSPORTES
@app.route('/transportation')
def transportation():
    return render_template('transportation.html')


#REDES
#@app.route("/solve_network")
#def solve_network():
# return render_template("network_form.html")

@app.route("/solve_network", methods=["POST"])
def solve_network():
    edges = request.form["edges"]
    edges = [tuple(map(int, edge.split(","))) for edge in edges.split(";")]

    source = request.form.get("source")
    sink = request.form.get("sink")

    supply = request.form.get("supply")
    supply = {int(k): int(v) for k, v in (item.split(":") for item in supply.split(","))} if supply else {}

    demand = request.form.get("demand")
    demand = {int(k): int(v) for k, v in (item.split(":") for item in demand.split(","))} if demand else {}

    mst = NetworkOptimization.minimum_spanning_tree(edges)
    max_flow = NetworkOptimization.max_flow(edges, int(source), int(sink)) if source and sink else None
    min_cost_flow = NetworkOptimization.min_cost_flow(supply, demand, edges) if supply and demand else None

    return jsonify({
        "MST": mst,
        "Flujo Máximo": max_flow,
        "Flujo de Costo Mínimo": min_cost_flow
    })




if __name__ == '__main__':
    app.run(debug=True)
