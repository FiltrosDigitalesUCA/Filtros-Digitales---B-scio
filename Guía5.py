import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import remez, firwin, lfilter, freqz
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, Layout, HBox, VBox, Output
from IPython.display import display

# Tooltip tipo popup para ayudas
tooltip_popup = Output(layout=Layout(border="1px solid #ccc", padding="8px", width="300px", background="#fffff5", display="none", position="absolute", z_index="100"))

# Diccionario de ayudas interactivas
tooltip_texts = {
    "window": "<b>ℹ Tipo de ventana:</b><br>Permite controlar el comportamiento espectral del filtro diseñado mediante firwin. Diferentes ventanas tienen diferentes anchos de banda principal y niveles de ripple.",
    "fs": "<b>ℹ Frecuencia de muestreo (Hz):</b><br>Controla la resolución temporal del sistema. A mayor fs, mejor resolución temporal.",
    "cutoff": "<b>⚠ Frecuencia de corte:</b><br>Define hasta qué frecuencia se preserva la señal. Debe ser menor que fs/2.",
    "orden": "<b>⚠ Orden del filtro:</b><br>Determina la nitidez del filtro y el retardo de grupo. A mayor orden, mayor retardo.",
    "metodo": "<b>ℹ Método de diseño:</b><br><b>firwin:</b> usa ventanas para suavizar el filtro.<br><b>remez:</b> usa optimización equiripple.",
    "amp300": "<b>ℹ Amplitud 300 Hz:</b><br>Controla el peso de la componente más grave de la señal de voz.",
    "amp800": "<b>ℹ Amplitud 800 Hz:</b><br>Controla el peso de la componente intermedia de la voz humana."
}

# Función para mostrar ayudas contextualizadas
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

# Widgets interactivos con ayuda
window_selector = widgets.Dropdown(
    options=['hamming', 'hann', 'blackman'],
    value='hamming',
    description='Ventana:',
    style={'description_width': 'initial'}
)
N_slider = widgets.IntSlider(value=60, min=10, max=200, step=2, description="Orden del filtro FIR")
fs_slider = widgets.IntSlider(value=16000, min=4000, max=48000, step=1000, description="Frecuencia de muestreo [Hz]")
cutoff_slider = widgets.IntSlider(value=4000, min=500, max=fs_slider.value//2 - 100, step=100, description="Frecuencia de corte [Hz]")
metodo_selector = widgets.Dropdown(
    options=['Metodo de ventanas (firwin)', 'Parks-McClellan (remez)'],
    value='Metodo de ventanas (firwin)',
    description='Método de diseño:',
    style={'description_width': 'initial'}
)
amp_300hz_slider = widgets.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description="Amplitud voz 300 Hz")
amp_800hz_slider = widgets.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description="Amplitud voz 800 Hz")
warning_label = widgets.Label(value='', style={'description_width': 'initial'})

# Actualizar el límite máximo del slider de frecuencia de corte cuando cambia fs
def actualizar_cutoff(*args):
    cutoff_slider.max = fs_slider.value // 2 - 100
    if cutoff_slider.value > cutoff_slider.max:
        cutoff_slider.value = cutoff_slider.max
    if cutoff_slider.value >= cutoff_slider.max:
        warning_label.value = '⚠️ Frecuencia de corte cerca del límite de Nyquist. Ajusta "Frecuencia de muestreo" o "Frecuencia de corte".'
    else:
        warning_label.value = ''

fs_slider.observe(actualizar_cutoff, 'value')
cutoff_slider.observe(actualizar_cutoff, 'value')

# Función para mostrar u ocultar selector de ventana
def actualizar_visibilidad_ventana(change):
    if metodo_selector.value == 'Parks-McClellan (remez)':
        window_selector.layout.display = 'none'
    else:
        window_selector.layout.display = 'flex'

metodo_selector.observe(actualizar_visibilidad_ventana, names='value')
actualizar_visibilidad_ventana(None)

# Contenedor de interfaz con ayudas
ui = VBox([
    make_control(window_selector, "window"),
    make_control(N_slider, "orden"),
    make_control(fs_slider, "fs"),
    make_control(cutoff_slider, "cutoff"),
    make_control(amp_300hz_slider, "amp300"),
    make_control(amp_800hz_slider, "amp800"),
    make_control(metodo_selector, "metodo"),
    warning_label,
    tooltip_popup
])

# Generador de la señal de prueba (voz + ruido)
def generar_senal(fs, amp_300hz, amp_800hz):
    t = np.linspace(0, 1, fs, endpoint=False)
    senal_voz = (
        amp_300hz * np.sin(2 * np.pi * 300 * t) +
        amp_800hz * np.sin(2 * np.pi * 800 * t)
    )
    senal_ruido = (
        0.3 * np.sin(2 * np.pi * 2000 * t) +
        0.3 * np.sin(2 * np.pi * 6000 * t) +
        0.3 * np.sin(2 * np.pi * 7000 * t)
    )
    senal = senal_voz + senal_ruido
    return t, senal, senal_voz

# Aplicador del filtro
def aplicar_filtro(N, cutoff_hz, fs, metodo, amp_300hz, amp_800hz, ventana):
    t, senal, senal_voz = generar_senal(fs, amp_300hz, amp_800hz)
    nyq = fs / 2
    cutoff_norm = cutoff_hz / nyq

    if metodo == 'Parks-McClellan (remez)':
        bands = [0, cutoff_norm, cutoff_norm + 0.1, 1.0]
        desired = [1, 0]
        try:
            h = remez(N + 1, bands, desired, fs=2)
        except ValueError as e:
            print("Error en diseño Parks-McClellan:", e)
            return
    elif metodo == 'Metodo de ventanas (firwin)':
        h = firwin(N + 1, cutoff_norm, window=ventana)
    else:
        raise ValueError("Método desconocido")

    senal_filtrada = lfilter(h, 1.0, senal)
    w, H = freqz(h, worN=8000, fs=fs)

    plt.figure(figsize=(14, 12))
    plt.subplot(3, 1, 1)
    plt.stem(t[:200], senal_voz[:200], linefmt='green', markerfmt='go', basefmt=' ')
    plt.title("\nSeñal de Voz Ideal (Referencia)")
    plt.xlabel("Tiempo (s)"); plt.ylabel("Amplitud"); plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.stem(t[:200], senal[:200], linefmt='gray', markerfmt='o', basefmt=' ', label='Señal original (voz + ruido)')
    plt.stem(t[:200], senal_filtrada[:200], linefmt='blue', markerfmt='bo', basefmt=' ', label='Señal filtrada')
    plt.title(f"\nComparación Señal Original y Filtrada - Método: {metodo}")
    plt.xlabel("Tiempo (s)"); plt.ylabel("Amplitud"); plt.legend(); plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(w, 20 * np.log10(np.abs(H)), color='darkgreen')
    plt.title("\nRespuesta en Frecuencia del Filtro FIR")
    plt.xlabel("Frecuencia (Hz)"); plt.ylabel("Magnitud (dB)")
    plt.ylim([-100, 5]); plt.grid(True)

    plt.tight_layout(); plt.show()

# Salida interactiva
out = widgets.interactive_output(aplicar_filtro, {
    'N': N_slider,
    'cutoff_hz': cutoff_slider,
    'fs': fs_slider,
    'metodo': metodo_selector,
    'amp_300hz': amp_300hz_slider,
    'amp_800hz': amp_800hz_slider,
    'ventana': window_selector
})

display(ui, out)