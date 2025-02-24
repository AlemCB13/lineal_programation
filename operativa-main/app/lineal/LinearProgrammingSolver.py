import pulp
import re
import google.generativeai as genai  # Importar la API de Gemini

# Configurar la API de Gemini
genai.configure(api_key="AIzaSyBTYC7_OtUpp_HC7YsCj_lKnatxYhhJHvc")  # Reemplaza con tu clave de API


class GeminiAnaliser:
    @staticmethod
    def interpretar_sensibilidad(resultado):
        """
        Usa Gemini (Google Generative AI) para interpretar el análisis de sensibilidad.
        """
        model = genai.GenerativeModel("gemini-pro")  # Modelo de Gemini

        prompt = f"""
        Analiza la siguiente solución de un problema de programación lineal y proporciona una interpretación de sensibilidad:
        {resultado}
        """

        response = model.generate_content(prompt)  # Obtener respuesta de Gemini
        return response.text  # Devolver solo el texto generado


class LinearProgrammingSolver:
    @staticmethod
    def resolver_problema(funcion_objetivo, objetivo, restricciones):
        """
        Resuelve un problema de programación lineal utilizando PuLP con el método de la Gran M.
        """
        variables = list(set(re.findall(r'[a-zA-Z]+', funcion_objetivo)))
        coeficientes = [int(coef) for coef in re.findall(r'[-+]?\d+', funcion_objetivo)]

        problema = pulp.LpProblem("Problema_de_Programacion_Lineal",
                                  pulp.LpMaximize if objetivo == "Maximizar" else pulp.LpMinimize)

        lp_variables = {var: pulp.LpVariable(var, lowBound=0) for var in variables}
        artificios = []

        funcion_objetivo_expr = sum(coef * lp_variables[var] for coef, var in zip(coeficientes, variables))
        problema += funcion_objetivo_expr, "Función Objetivo"

        M = 1e6  # Gran M

        for i, restriccion in enumerate(restricciones):
            expr = re.sub(r'([a-zA-Z]+)', lambda m: f'lp_variables["{m.group(1)}"]', restriccion)

            if '<=' in expr:
                lhs, rhs = expr.split('<=')
                problema += (eval(lhs) <= float(rhs.strip())), f"Restricción_{i + 1}"

            elif '>=' in expr:
                lhs, rhs = expr.split('>=')
                artificial = pulp.LpVariable(f'artificial_{i + 1}', lowBound=0)
                artificios.append(artificial)
                problema += (eval(lhs) - artificial >= float(rhs.strip())), f"Restricción_{i + 1}"
                problema.setObjective(funcion_objetivo_expr + M * artificial)

            elif '=' in expr:
                lhs, rhs = expr.split('=')
                artificial = pulp.LpVariable(f'artificial_{i + 1}', lowBound=0)
                artificios.append(artificial)
                problema += (eval(lhs) + artificial == float(rhs.strip())), f"Restricción_{i + 1}"
                problema.setObjective(funcion_objetivo_expr + M * artificial)

        problema.solve()

        resultado = {
            "Objetivo": objetivo,
            "Función": funcion_objetivo,
            "Variables": {var: var_value.varValue for var, var_value in lp_variables.items()},
            "Coeficientes": coeficientes,
            "Restricciones": restricciones,
            "Valor_Objetivo": pulp.value(problema.objective),
            "Holguras": {f"holgura_{i + 1}": problema.constraints[f"Restricción_{i + 1}"].slack for i in
                         range(len(restricciones))},
            "Artificios": {f"artificial_{i + 1}": artificio.varValue for i, artificio in enumerate(artificios)}
        }
        return resultado


if __name__ == "__main__":
    funcion_objetivo = "7*x + 9*y"
    objetivo = "Maximizar"
    restricciones = ["2*x + y <= 5", "x + 2*y >= 6", "x + y = 3"]

    resultado = LinearProgrammingSolver.resolver_problema(funcion_objetivo, objetivo, restricciones)

    print("Resultados del Problema de Programación Lineal:")
    print(f"Función Objetivo: {resultado['Función']}")
    print(f"Tipo de Objetivo: {resultado['Objetivo']}")
    print(f"Variables y Valores: {resultado['Variables']}")
    print(f"Coeficientes: {resultado['Coeficientes']}")
    print(f"Restricciones: {resultado['Restricciones']}")
    print(f"Valor de la Función Objetivo: {resultado['Valor_Objetivo']}")
    print(f"Holguras: {resultado['Holguras']}")
    print(f"Artificios: {resultado['Artificios']}")

    # Llamada a Gemini para interpretar el resultado
    print(GeminiAnaliser.interpretar_sensibilidad(resultado))