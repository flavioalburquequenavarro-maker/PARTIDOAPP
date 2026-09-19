from flask import Flask, render_template, request
import json

app = Flask(__name__)

ARCHIVO = "jugadores.json"
MAX_JUGADORES = 4


def cargar_jugadores():
    with open(ARCHIVO, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_jugadores(jugadores):
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(jugadores, archivo, ensure_ascii=False, indent=4)


@app.route("/")
def inicio():
    jugadores = cargar_jugadores()

    return render_template(
        "inicio.html",
        partido=jugadores["partido"]
    )


@app.route("/crear", methods=["POST"])
def crear():

    nombre = request.form["nombre"].strip()
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    jugadores = cargar_jugadores()

    jugadores["partido"]["nombre"] = nombre
    jugadores["partido"]["fecha"] = fecha
    jugadores["partido"]["hora"] = hora

    jugadores["equipo1"] = []
    jugadores["equipo2"] = []

    guardar_jugadores(jugadores)

    return render_template(
        "index.html",
        jugadores=jugadores
    )


@app.route("/partido")
def partido():

    jugadores = cargar_jugadores()

    return render_template(
        "index.html",
        jugadores=jugadores
    )


@app.route("/agregar", methods=["POST"])
def agregar():

    nombre = request.form["nombre"].strip()
    equipo = request.form["equipo"]

    jugadores = cargar_jugadores()

    if nombre == "":
        return render_template(
            "index.html",
            jugadores=jugadores,
            mensaje="Escribe tu nombre."
        )

    todos_los_jugadores = (
        jugadores["equipo1"] +
        jugadores["equipo2"]
    )

    if nombre.lower() in [
        jugador.lower()
        for jugador in todos_los_jugadores
    ]:
        return render_template(
            "index.html",
            jugadores=jugadores,
            mensaje="Ese nombre ya está registrado."
        )

    if len(jugadores[equipo]) >= MAX_JUGADORES:
        return render_template(
            "index.html",
            jugadores=jugadores,
            mensaje="Ese equipo ya está lleno. Máximo 4 jugadores."
        )

    jugadores[equipo].append(nombre)

    guardar_jugadores(jugadores)

    return render_template(
        "index.html",
        jugadores=jugadores
    )


@app.route("/salir", methods=["POST"])
def salir():

    nombre = request.form["nombre"]

    jugadores = cargar_jugadores()

    for equipo in ["equipo1", "equipo2"]:

        if nombre in jugadores[equipo]:
            jugadores[equipo].remove(nombre)

    guardar_jugadores(jugadores)

    return render_template(
        "index.html",
        jugadores=jugadores
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)