
from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import pandas as pd
import os
import sympy as sp
import numpy as np
import plotly.graph_objs as go
import json
import plotly


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Formulario padre

# Regresion Lineal

@app.route('/regLineal', methods=['GET', 'POST'])
def regLineal():
    if request.method == 'POST':
        # Paso 1: usuario indica cuántos puntos quiere ingresar
        if 'cantidad' in request.form and not 'x0' in request.form:
            try:
                cantidad = int(request.form.get('cantidad'))
                if cantidad <= 1:
                    return render_template('regLineal.html', error="Debe ingresar al menos 2 puntos.", cantidad=None)
                return render_template('regLineal.html', cantidad=cantidad)
            except ValueError:
                return render_template('regLineal.html', error="Ingrese un número entero válido.", cantidad=None)

        # Paso 2: usuario ya ingresó todos los x e y
        try:
            cantidad = int(request.form.get('cantidad'))
            x_vals = []
            y_vals = []

            for i in range(cantidad):
                x = float(request.form.get(f'x{i}'))
                y = float(request.form.get(f'y{i}'))
                x_vals.append(x)
                y_vals.append(y)

            n = cantidad
            sum_x = sum(x_vals)
            sum_y = sum(y_vals)
            sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
            sum_x2 = sum(x ** 2 for x in x_vals)

            denominador = n * sum_x2 - sum_x ** 2
            if denominador == 0:
                return render_template('regLineal.html', cantidad=cantidad, error="No se puede calcular la pendiente: división por cero.", x_vals=x_vals, y_vals=y_vals)

            m = (n * sum_xy - sum_x * sum_y) / denominador
            b = (sum_y - m * sum_x) / n

            resultados = {
                'm': round(m, 4),
                'b': round(b, 4)
            }

            xy_pares = list(zip(x_vals, y_vals))

            # Predicción (si el usuario envió un valor para predecir)
            y_predicho = None
            x_prediccion_input = request.form.get('x_prediccion')
            if x_prediccion_input:
                try:
                    x_pred = float(x_prediccion_input)
                    y_predicho = round(m * x_pred + b, 4)
                except ValueError:
                    y_predicho = "Valor no válido"

            # Gráfica Plotly
            min_x = min(x_vals)
            max_x = max(x_vals)
            line_x = [min_x, max_x]
            line_y = [m * x + b for x in line_x]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', name='Datos', marker=dict(size=10)))
            fig.add_trace(go.Scatter(x=line_x, y=line_y, mode='lines', name='Recta de Regresión'))

            # Si hay valor para predicción, lo mostramos en la gráfica como punto distinto
            if y_predicho is not None and isinstance(y_predicho, float):
                fig.add_trace(go.Scatter(
                    x=[x_pred],
                    y=[y_predicho],
                    mode='markers',
                    marker=dict(color='red', size=12, symbol='x'),
                    name=f'Predicción para x={x_pred}'
                ))

            fig.update_layout(
                title="Gráfica de Regresión Lineal",
                xaxis_title="X",
                yaxis_title="Y",
                template="plotly_white"
            )

            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            return render_template('regLineal.html',
                                   resultados=resultados,
                                   x_vals=x_vals,
                                   y_vals=y_vals,
                                   xy_pares=xy_pares,
                                   graphJSON=graphJSON,
                                   y_predicho=y_predicho,
                                   x_prediccion_input=x_prediccion_input,
                                   cantidad=cantidad)

        except ValueError:
            return render_template('regLineal.html', cantidad=cantidad, error="Todos los valores deben ser numéricos.")

    return render_template('regLineal.html', cantidad=None)



#Lagrange

@app.route("/interLagrange", methods=["GET", "POST"])
def interLagrange():
    try:
        if request.method == "POST":
            cantidad = request.form.get("cantidad")

            if cantidad and all(f"x{i}" in request.form for i in range(int(cantidad))):
                # Segundo formulario: recibe los puntos
                cantidad = int(cantidad)
                x_vals = [float(request.form.get(f"x{i}")) for i in range(cantidad)]
                y_vals = [float(request.form.get(f"y{i}")) for i in range(cantidad)]

                x = sp.Symbol("x")
                polinomio = 0
                for i in range(cantidad):
                    termino = y_vals[i]
                    for j in range(cantidad):
                        if i != j:
                            termino *= (x - x_vals[j]) / (x_vals[i] - x_vals[j])
                    polinomio += termino

                polinomio_simplificado = sp.simplify(polinomio)

                # Revisar si se quiere evaluar el polinomio
                x_eval = request.form.get("x_eval")
                y_eval = None
                if x_eval:
                    x_eval = float(x_eval)
                    y_eval = float(polinomio_simplificado.subs(x, x_eval))

                # Graficar usando Plotly
                x_num = np.linspace(min(x_vals) - 1, max(x_vals) + 1, 200)
                y_num = [float(polinomio_simplificado.subs(x, val)) for val in x_num]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', name='Puntos originales'))
                fig.add_trace(go.Scatter(x=x_num, y=y_num, mode='lines', name='Curva interpolada'))
                fig.update_layout(title="Interpolación de Lagrange", xaxis_title="x", yaxis_title="y")

                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                return render_template("interLagrange.html", cantidad=cantidad, x_vals=x_vals, y_vals=y_vals,
                                       polinomio=sp.latex(polinomio_simplificado), x_eval=x_eval, y_eval=y_eval,
                                       graphJSON=graphJSON)

            elif cantidad:  # Primer formulario: solo cantidad
                return render_template("interLagrange.html", cantidad=int(cantidad))
            
            x_vals = [round(float(x), 4) for x in x_vals]
            y_vals = [round(float(y), 4) for y in y_vals] 


        return render_template("interLagrange.html")

    except Exception as e:
        return render_template("interLagrange.html", error=f"Ocurrió un error: {e}")


#ExtraLineal

@app.route("/extraLineal", methods=["GET", "POST"])
def extra_lineal():
    if request.method == "POST":
        try:
            if "cantidad" in request.form and all(f"x{i}" in request.form for i in range(int(request.form["cantidad"]))):
                # Paso 3: Ya tengo los valores X y Y
                cantidad = int(request.form["cantidad"])
                x_vals = [float(request.form[f"x{i}"]) for i in range(cantidad)]
                y_vals = [float(request.form[f"y{i}"]) for i in range(cantidad)]

                # Calcular pendiente e intercepto
                df = pd.DataFrame({"X": x_vals, "Y": y_vals})
                pendiente = ((df["X"] - df["X"].mean()) * (df["Y"] - df["Y"].mean())).sum() / ((df["X"] - df["X"].mean()) ** 2).sum()
                intercepto = df["Y"].mean() - pendiente * df["X"].mean()

                # Evaluación (si se proporciona x_eval)
                x_eval = request.form.get("x_eval")
                y_eval = None
                if x_eval:
                    x_eval = float(x_eval)
                    y_eval = pendiente * x_eval + intercepto
                    y_eval = "{:.4f}".format(y_eval)

                # Graficar
                x_line = [min(x_vals) - 1, max(x_vals) + 1]
                y_line = [pendiente * x + intercepto for x in x_line]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', name='Datos'))
                fig.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines', name='Extrapolación'))
                fig.update_layout(title="Extrapolación Lineal", xaxis_title="X", yaxis_title="Y")

                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                return render_template("extraLineal.html",
                                       cantidad=cantidad,
                                       x_vals=["{:.4f}".format(x) for x in x_vals],
                                       y_vals=["{:.4f}".format(y) for y in y_vals],
                                       pendiente="{:.4f}".format(pendiente),
                                       intercepto="{:.4f}".format(intercepto),
                                       x_eval=x_eval,
                                       y_eval=y_eval,
                                       graphJSON=graphJSON)

            elif "cantidad" in request.form:
                # Paso 2: El usuario envió cuántos datos quiere
                cantidad = int(request.form["cantidad"])
                return render_template("extraLineal.html", cantidad=cantidad)

        except Exception as e:
            return render_template("extraLineal.html", error=f"Error: {e}")

    # Paso 1: Mostrar formulario inicial
    return render_template("extraLineal.html")


# 
    
if __name__ == '__main__':
    app.run(debug=True) 