"""
Paso 1: leer el DualShock 4 por Bluetooth y mostrar los bytes crudos.

Objetivo: ver con tus propios ojos qué bytes cambian al pulsar cada botón
o mover cada stick, antes de escribir ningún decodificador.

Ejecutar:  .venv\\Scripts\\python paso1_leer_crudo.py
Salir:     Ctrl+C
"""

import sys
import hid

SONY_VID = 0x054C
DS4_PIDS = {
    0x05C4: "DualShock 4 v1",
    0x09CC: "DualShock 4 v2",
    0x0BA0: "Adaptador inalámbrico DS4",
}

# Por Bluetooth el DS4 arranca en modo "reducido" (report 0x01, pocos datos).
# Al pedirle el feature report 0x02 (calibración del giroscopio) pasa a enviar
# el report extendido 0x11, que trae todo: sticks, botones, gatillos, IMU,
# touchpad y batería.
REPORT_REDUCIDO = 0x01
REPORT_EXTENDIDO_BT = 0x11
FEATURE_CALIBRACION = 0x02
TAM_LECTURA = 78  # tamaño del report 0x11 por Bluetooth

# Cuántos bytes mostramos (los del final son IMU/touchpad/CRC y cambian siempre)
BYTES_A_MOSTRAR = 16

VERDE = "\033[92m"
GRIS = "\033[90m"
RESET = "\033[0m"


def buscar_ds4():
    for info in hid.enumerate(SONY_VID):
        if info["product_id"] in DS4_PIDS:
            return info
    return None


def activar_modo_extendido(dispositivo):
    # El contenido de la respuesta no nos importa todavía; lo importante es
    # que al pedirla el mando cambia al report 0x11.
    dispositivo.get_feature_report(FEATURE_CALIBRACION, 37)


def formatear(datos, anteriores):
    partes = []
    for i, byte in enumerate(datos[:BYTES_A_MOSTRAR]):
        color = VERDE if anteriores and byte != anteriores[i] else GRIS
        partes.append(f"{color}{byte:02X}{RESET}")
    return " ".join(partes)


def main():
    info = buscar_ds4()
    if info is None:
        print("No se encontró ningún DualShock 4. ¿Está emparejado y encendido?")
        sys.exit(1)

    conexion = "Bluetooth" if info.get("bus_type") == 2 else "USB"
    print(f"Encontrado: {DS4_PIDS[info['product_id']]} por {conexion}")

    dispositivo = hid.device()
    dispositivo.open_path(info["path"])
    activar_modo_extendido(dispositivo)

    cabecera = " ".join(f"{i:02d}" for i in range(BYTES_A_MOSTRAR))
    print(f"\nByte: {cabecera}")

    anteriores = None
    try:
        while True:
            datos = dispositivo.read(TAM_LECTURA, 1000)
            if not datos:
                print("\nSin datos en 1 s (¿se ha apagado el mando?)")
                continue

            if datos[0] == REPORT_REDUCIDO:
                # Si ves esto el mando no ha cambiado a modo extendido
                print(f"\r[0x01 reducido] {formatear(datos, anteriores)}", end="")
            else:
                print(f"\rDatos {formatear(datos, anteriores)}", end="")

            anteriores = datos
    except KeyboardInterrupt:
        print("\nSaliendo.")
    finally:
        dispositivo.close()


if __name__ == "__main__":
    main()
