import random

def generar_paginas():
    r = random.random()

    # 15% probabilidad
    if r < 0.15:
        return random.randint(100,200)
    # 35% probabilidad
    elif r < 0.50:
        return random.randint(201,300)
    # 35% probabilidad
    elif r < 0.85:
        return random.randint(301,400)
    # 12% probabilidad
    elif r < 0.97:
        return random.randint(401,600)
    # 3 % probabilidad
    return random.randint(601,2000)

def generar_precio(paginas):
    precio_base=25000

    # Rango de precio extra por página

    if paginas < 100:
        factor = random.randint(50, 100)

    elif paginas < 400:
        factor = random.randint(110, 200)

    elif paginas < 700:
        factor = random.randint(210, 300)

    else:
        factor = random.randint(350, 500)

    variable = paginas * factor

    precio = precio_base + variable

    return precio

def generar_estado(precio):
    if precio < 40000:
        probabilidad_usado = 0.70
    elif precio < 50000:
        probabilidad_usado = 0.50
    elif precio < 70000:
        probabilidad_usado = 0.20
    else: 
        probabilidad_usado = 0.10

    if random.random() < probabilidad_usado:
        return "USADO"

    return "NUEVO"

