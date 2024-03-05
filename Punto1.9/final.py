import numpy as np
import queue

tiempo_simulacion = 4

# Variables enteras ---------------------------------------------------------------
tipo_evento_siguiente = 0  # Tipo de evento siguiente
num_minutos_servicio = 1440
num_ventas_perdidas = 0
num_autos_atendidos = 0
gasolineras_libres = 4

# Variables reales ----------------------------------------------------------------
tiempo_simulacion = 0.0  # reloj
tiempo_siguiente_evento = [None, None, None]
cola = queue.Queue()

# Parámetros ----------------------------------------------------------------------
venta_promedio = 40
tasa_llegadas = 0.5  # por min
media_servicio = 5  # min

# Tiempo de observación
tiempo_observacion = 1440  # min

# tiene 4 tareas
def inicializar_simulacion():
    global tiempo_simulacion, gasolineras_libres, num_autos_atendidos, num_ventas_perdidas, tiempo_siguiente_evento, cola

    tiempo_simulacion = 0.0  # reloj
    gasolineras_libres = 4  # gasolineras libres
    num_autos_atendidos = 0  # autos atendidos
    num_ventas_perdidas = 0  # Número de ventas perdidas
    tiempo_siguiente_evento = [None, None, None]
    cola = queue.Queue()

    # Inicializar lista de eventos
    tiempo_siguiente_evento[0] = tiempo_simulacion + exponencial_poisson(tasa_llegadas)
    tiempo_siguiente_evento[1] = [np.inf, np.inf, np.inf, np.inf]
    tiempo_siguiente_evento[2] = tiempo_observacion

def timing():
    global tiempo_simulacion, tipo_evento_siguiente, tiempo_siguiente_evento

    # Va a la lista de eventos y avanza el reloj al evento siguiente
    tiempo_min_evento = np.inf
    tipo_evento_siguiente = 0

    for num, tiempo_evento in enumerate(tiempo_siguiente_evento):
        if (num != 1 and tiempo_evento < tiempo_min_evento):
            tiempo_min_evento = tiempo_evento
            tipo_evento_siguiente = num + 1

    min_de_servicios = min(tiempo_siguiente_evento[1])
    if (min_de_servicios < tiempo_min_evento):
        tiempo_min_evento = min_de_servicios
        tipo_evento_siguiente = 2

    if tipo_evento_siguiente == 0:
        print("Lista de eventos vacía")
        return
    tiempo_simulacion = tiempo_min_evento

# Rutina del evento llegadas
def espera_cliente(prob_espera):
    # Si el cliente espera, retorna True; de lo contrario, False
    return np.random.rand() > prob_espera

def llegadas():
    global num_autos_atendidos, gasolineras_libres, num_ventas_perdidas, cola, tiempo_siguiente_evento

    # Programo la próxima llegada
    tiempo_siguiente_evento[0] = tiempo_simulacion + exponencial_poisson(tasa_llegadas)

    # Miro si hay gasolinera libre
    if gasolineras_libres > 0:
        num_autos_atendidos += 1
        maximo = max(tiempo_siguiente_evento[1])
        indice_max = tiempo_siguiente_evento[1].index(maximo)
        tiempo_siguiente_evento[1][indice_max] = tiempo_simulacion + expon(media_servicio)
        gasolineras_libres -= 1
    else:
        if espera_cliente(0.5):
            # Aunque puede que realmente no sea importante tener el tiempo de llegada en la cola
            cola.put(tiempo_simulacion)
            num_autos_atendidos += 1
        else:
            num_ventas_perdidas += 1

def terminacion_servicio():
    global gasolineras_libres, cola, tiempo_siguiente_evento
    minimo = min(tiempo_siguiente_evento[1])
    indice_min = tiempo_siguiente_evento[1].index(minimo)
    if cola.empty():
        tiempo_siguiente_evento[1][indice_min] = np.inf
        gasolineras_libres += 1
    else:
        cola.get()
        tiempo_siguiente_evento[1][indice_min] = tiempo_simulacion + expon(media_servicio)

def reporte():
    global num_ventas_perdidas, num_autos_atendidos, venta_promedio

    print(f"La pérdida promedio en este día fue de: {num_ventas_perdidas * venta_promedio}")
    print(f"Las ganancias promedio en este día fueron de: {num_autos_atendidos * venta_promedio}")
    calculo_porcentaje = (num_ventas_perdidas * 100) / (num_ventas_perdidas + num_autos_atendidos)
    print(f"El porcentaje de pérdidas fue de: {round(calculo_porcentaje, 2)}%")
    print('\n')

# Produce las variables aleatorias exponenciales
def exponencial_poisson(tasa_llegadas):
    # Generar un número aleatorio con distribución de Poisson
    return np.random.poisson(lam=1/tasa_llegadas)

def expon(media):
    # Generar un número aleatorio con distribución exponencial
    return np.random.exponential(scale=media)

# PROGRAMA
print(f"La media de servicio es {media_servicio} y la tasa de llegada es {tasa_llegadas}")

for i in range (0,20):

  inicializar_simulacion()

  while tiempo_simulacion < num_minutos_servicio:
      timing()

      if tipo_evento_siguiente == 1:
          llegadas()
      elif tipo_evento_siguiente == 2:
          terminacion_servicio()
      elif tipo_evento_siguiente == 3:
          reporte()
          break
