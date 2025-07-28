import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import Output, Layout, HBox, VBox

# Tooltip
tooltip_popup = Output(layout=Layout(border="1px solid #ccc", padding="8px", width="300px", background="#fffff5", display="none", position="absolute", z_index="100"))

# Textos de ayuda
tooltip_texts = {
    "A": "<b>ℹ Amplitud:</b><br>Controla la magnitud de la señal compleja. Afecta directamente el rango de valores de la parte real e imaginaria.",
    "f": "<b>ℹ Frecuencia:</b><br>Define cuántos ciclos completos ocurren por segundo. Se mide en Hz.",
    "phi": "<b>ℹ Fase:</b><br>Desfase inicial de la señal, medido en radianes.",
    "shift": "<b>ℹ Desplazamiento:</b><br>Desplaza la señal en el tiempo.",
    "fs": "<b>ℹ Frecuencia de muestreo (fs):</b><br>Determina cuántas muestras por segundo se toman para la señal discreta."
}

# Controles con botón de ayuda
def make_control(widget, key):
    btn = widgets.Button(description="?", layout=Layout(width="30px"))
    def on_click(b):
        tooltip_popup.clear_output()
        with tooltip_popup:
            display(widgets.HTML(f"<div style='font-family:sans-serif;font-size:14px;'>{tooltip_texts[key]}</div>"))
        tooltip_popup.layout.display = "block"
    btn.on_click(on_click)
    widget.layout = Layout(width="250px")
    return HBox([widget, btn], layout=Layout(padding="2px"))

# Sliders
amplitude_slider = widgets.FloatSlider(value=1.0, min=0.1, max=5.0, step=0.1, description='Amplitud:')
frequency_slider = widgets.FloatSlider(value=1.0, min=0.1, max=5.0, step=0.1, description='Frecuencia [Hz]:')
phase_slider = widgets.FloatSlider(value=0.0, min=-np.pi, max=np.pi, step=0.1, description='Fase [rad]:')
shift_slider = widgets.FloatSlider(value=0.0, min=-2.0, max=2.0, step=0.1, description='Desplazamiento:')
fs_slider = widgets.IntSlider(value=100, min=1, max=1000, step=5, description='Fs:')

# Panel de controles
controls = VBox([
    make_control(amplitude_slider, "A"),
    make_control(frequency_slider, "f"),
    make_control(phase_slider, "phi"),
    make_control(shift_slider, "shift"),
    make_control(fs_slider, "fs"),
    tooltip_popup
])

# Gráfica
output_plot = Output()

def plot_complex_exponential(A, f, phi, shift, fs):
    output_plot.clear_output(wait=True)
    with output_plot:
        t = np.linspace(0, 10, 1000)
        n = np.arange(0, 10 * fs)
        continuous_signal = A * np.exp(1j * (2 * np.pi * f * (t - shift) + phi))
        discrete_signal = A * np.exp(1j * (2 * np.pi * f * (n / fs - shift) + phi))
        continuous_real = np.real(continuous_signal)
        continuous_imag = np.imag(continuous_signal)
        discrete_real = np.real(discrete_signal)
        discrete_imag = np.imag(discrete_signal)

        plt.figure(figsize=(10, 6))
        plt.plot(t, continuous_real, label="Parte real continua", color='b', linewidth=2)
        plt.plot(t, continuous_imag, label="Parte imaginaria continua", color='g', linewidth=2)
        plt.stem(n / fs, discrete_real, label="Parte real discreta", basefmt=" ", linefmt='r', markerfmt='ro')
        plt.stem(n / fs, discrete_imag, label="Parte imaginaria discreta", basefmt=" ", linefmt='y', markerfmt='yo')
        plt.title('Señales Exponenciales Complejas Continuas y Discretas')
        plt.xlabel('Tiempo [s]')
        plt.ylabel('Amplitud')
        plt.grid(True)
        plt.legend(loc='best')
        plt.xlim([0, 10])
        plt.ylim([-A - 1, A + 1])
        plt.show()

# Enlazar sliders manualmente a la función
def actualizar_grafico(change=None):
    plot_complex_exponential(
        A=amplitude_slider.value,
        f=frequency_slider.value,
        phi=phase_slider.value,
        shift=shift_slider.value,
        fs=fs_slider.value
    )

for s in [amplitude_slider, frequency_slider, phase_slider, shift_slider, fs_slider]:
    s.observe(actualizar_grafico, names='value')

actualizar_grafico()

display(HBox([controls, output_plot]))
