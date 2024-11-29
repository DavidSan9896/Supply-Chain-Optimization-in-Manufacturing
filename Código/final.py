# Importación de librerías necesarias para la creación de la interfaz gráfica y gráficos
import tkinter as tk  # Librería principal para la interfaz gráfica de usuario (GUI)
from tkinter import ttk, messagebox  # ttk es para widgets mejorados y messagebox para mostrar mensajes emergentes
import numpy as np  # Librería para manejo de matrices y operaciones numéricas
import matplotlib.pyplot as plt  # Librería para creación de gráficos y visualización
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Conector entre matplotlib y tkinter para mostrar gráficos en la GUI

# Implementación del Generador Lineal Congruencial (LCG) para números pseudoaleatorios
def linear_congruential_generator(seed, a=1664525, c=1013904223, m=2**32):
    """Generador Lineal Congruencial (LCG) para números pseudoaleatorios."""
    while True:
        seed = (a * seed + c) % m
        yield seed / m  # Normalizamos el valor para obtener un número entre 0 y 1.

def simulate_markov_chain_live():
    try:
        days = int(entry_days.get())  # Número de días
        num_products = int(entry_products.get())  # Número de productos
        total_price = float(entry_price.get())  # Precio total

        if days <= 0 or num_products <= 0 or total_price <= 0:
            raise ValueError("Los valores deben ser mayores a cero.")  # Validación de entrada

        # Matriz de transición de la cadena de Markov
        transition_matrix = np.array([
            [0.6, 0.3, 0.05, 0.03, 0.02],
            [0.2, 0.5, 0.15, 0.1, 0.05],
            [0.1, 0.2, 0.5, 0.15, 0.05],
            [0.05, 0.1, 0.2, 0.5, 0.15],
            [0.02, 0.05, 0.1, 0.2, 0.63]
        ])

        # Inicialización de los estados de los productos
        states = np.zeros((days, num_products), dtype=int)
        states[0, :] = 0

        penalties = [1.0, 0.95, 0.85, 0.5, 0.3]  # Penalizaciones para cada estado
        cost_per_day = total_price / days  # Costo por día
        total_cost = 0  # Costo total acumulado
        discounts = [0] * 5  # Descuentos acumulados por estado

        # Inicializamos el generador LCG con una semilla fija
        seed_value = 42  # Semilla para el generador pseudoaleatorio
        lcg = linear_congruential_generator(seed_value)

        # Ventana de simulación en tiempo real
        new_window = tk.Toplevel(root)  # Nueva ventana para la simulación
        new_window.title("Simulación en Tiempo Real")
        fig, ax = plt.subplots(figsize=(8, 5))  # Tamaño de la figura para la gráfica
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()

        x_data = []  # Datos para el eje X (tiempo)
        y_data = [[] for _ in range(5)]  # Datos para el eje Y (cantidad de productos por estado)
        state_names = ['Excelente', 'Bueno', 'Regular', 'Defectuoso', 'Malo']  # Nombres de los estados

        def update_chart(t=0):
            nonlocal total_cost
            if t < days and new_window.winfo_exists():
                if t > 0:
                    for i in range(num_products):
                        current_state = states[t-1, i]  # Estado actual del producto
                        
                        # Generar un número pseudoaleatorio entre 0 y 1 usando el generador LCG
                        rand_val = next(lcg)

                        # Usar las probabilidades de transición para seleccionar el nuevo estado
                        cumulative_prob = 0.0
                        for new_state in range(5):  # 5 posibles estados
                            cumulative_prob += transition_matrix[current_state, new_state]
                            if rand_val < cumulative_prob:
                                states[t, i] = new_state
                                break

                # Contar los productos en cada estado
                counts = [np.sum(states[t] == i) for i in range(5)]
                daily_penalty = sum(counts[i] * penalties[i] * cost_per_day / num_products for i in range(5))

                # Acumular descuentos y costo total
                for i in range(5):
                    discounts[i] += (counts[i] * (1 - penalties[i]) * cost_per_day / num_products)

                total_cost += daily_penalty

                # Datos para la gráfica
                x_data.append(t)
                for i in range(5):
                    y_data[i].append(counts[i])

                ax.clear()
                for i in range(5):
                    ax.plot(x_data, y_data[i], label=f"{state_names[i]} (n={counts[i]})", marker='o')
                ax.set_xlabel('Tiempo (días)')
                ax.set_ylabel('Número de productos')
                ax.set_title(f'Distribución de Estados en Tiempo Real\nCostos acumulados: ${total_cost:.2f} COP')
                ax.legend()
                ax.grid(True)
                canvas.draw()

                new_window.after(1000, lambda: update_chart(t+1))
            else:
                show_final_summary()

        def show_final_summary():
            final_counts = [np.sum(states[-1] == i) for i in range(5)]

            # Ventana con resumen y gráfica de barras apiladas
            summary_window = tk.Toplevel(new_window)  # Nueva ventana para el resumen final
            summary_window.title("Resumen Final")

            # Gráfico de barras apiladas
            fig_summary, ax_summary = plt.subplots(figsize=(6, 4))
            ax_summary.barh(state_names, final_counts, color=plt.cm.tab20c.colors, edgecolor="black")
            ax_summary.set_xlabel("Cantidad")
            ax_summary.set_title("Distribución Final de Estados")
            ax_summary.grid(True, axis='x', linestyle='--', alpha=0.7)

            canvas_summary = FigureCanvasTkAgg(fig_summary, master=summary_window)
            canvas_summary.get_tk_widget().pack()

            # Texto del resumen
            summary_text = "Resumen Final:\n"
            for i in range(5):
                summary_text += (f"- {state_names[i]}: {final_counts[i]} productos "
                                f"({final_counts[i] / num_products:.1%})\n"
                                f"  Descuento acumulado: ${discounts[i]:.2f}\n")

            summary_label = tk.Label(summary_window, text=summary_text, justify=tk.LEFT, font=("Arial", 12))
            summary_label.pack(pady=10)

            # Nueva ventana para el gráfico de columnas apiladas
            stacked_window = tk.Toplevel(new_window)
            stacked_window.title("Gráfico de Columnas Apiladas")

            selected_days = np.linspace(0, days-1, 5, dtype=int)
            x_labels = [f"Día {d+1}" for d in selected_days]
            y_data_stacked = [np.sum(states[selected_days] == i, axis=1) for i in range(5)]

            fig_stacked, ax_stacked = plt.subplots(figsize=(8, 5))
            width = 0.7
            bottom_values = np.zeros(5)
            colors = plt.cm.tab20c.colors[:5]

            for i in range(5):
                ax_stacked.bar(x_labels, y_data_stacked[i], width, label=state_names[i], bottom=bottom_values, color=colors[i])
                bottom_values += y_data_stacked[i]

            ax_stacked.set_xlabel("Días")
            ax_stacked.set_ylabel("Cantidad de productos")
            ax_stacked.set_title("Distribución de Estados (Columnas Apiladas)")
            ax_stacked.legend()
            ax_stacked.grid(True, axis='y', linestyle='--', alpha=0.7)

            canvas_stacked = FigureCanvasTkAgg(fig_stacked, master=stacked_window)
            canvas_stacked.get_tk_widget().pack()

        update_chart()

    except ValueError as e:
        messagebox.showerror("Error de entrada", str(e))

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Simulación de Cadenas de Manufactura")
root.geometry("400x350")  # Tamaño de la ventana principal
root.configure(bg="#f0f0f0")

label_title = tk.Label(root, text="Optimización de Cadenas de Manufactura", font=("Arial", 14, "bold"), bg="#f0f0f0")
label_title.pack(pady=10)

frame_input = ttk.Frame(root)
frame_input.pack(pady=20)

# Entrada para el número de días
label_days = ttk.Label(frame_input, text="Número de días:")
label_days.grid(row=0, column=0, padx=10, pady=10)
entry_days = ttk.Entry(frame_input, width=10)
entry_days.grid(row=0, column=1)

# Entrada para los productos
label_products = ttk.Label(frame_input, text="Número de productos:")
label_products.grid(row=1, column=0, padx=10, pady=10)
entry_products = ttk.Entry(frame_input, width=10)
entry_products.grid(row=1, column=1)

# Entrada para el precio total
label_price = ttk.Label(frame_input, text="Precio total (COP):")
label_price.grid(row=2, column=0, padx=10, pady=10)
entry_price = ttk.Entry(frame_input, width=10)
entry_price.grid(row=2, column=1)

# Botón para iniciar la simulación
start_button = ttk.Button(root, text="Iniciar Simulación", command=simulate_markov_chain_live)
start_button.pack(pady=20)

root.mainloop() # Ejecuta el bucle principal de la interfaz gráfica
