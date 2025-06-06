
from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import os 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Formulario padre

#Regresion Lineal

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


            return render_template('regLineal.html', resultados=resultados, x_vals=x_vals, y_vals=y_vals, xy_pares=xy_pares)


        except ValueError:
            return render_template('regLineal.html', cantidad=cantidad, error="Todos los valores deben ser numéricos.")

    return render_template('regLineal.html', cantidad=None)

if __name__ == '__main__':
    app.run(debug=True)  