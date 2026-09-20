from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__)

# Clave secreta
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "clave-partidoapp-2026"
)

# Base de datos
database_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///partido.db"
)

# Compatibilidad con algunas URLs de PostgreSQL
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
MAX_JUGADORES = 4


class Partido(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(20), nullable=False)


class Jugador(db.Model):

    id = db.Column(db.String(36), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    equipo = db.Column(db.String(20), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def inicio():

    partido = Partido.query.first()

    if not partido:
        return render_template("inicio.html")

    jugadores = {
        "partido": {
            "nombre": partido.nombre,
            "fecha": partido.fecha,
            "hora": partido.hora
        },
        "equipo1": [
            {
                "id": jugador.id,
                "nombre": jugador.nombre
            }
            for jugador in Jugador.query.filter_by(equipo="equipo1").all()
        ],
        "equipo2": [
            {
                "id": jugador.id,
                "nombre": jugador.nombre
            }
            for jugador in Jugador.query.filter_by(equipo="equipo2").all()
        ]
    }

    return render_template(
        "inicio.html",
        partido=jugadores["partido"]
    )


@app.route("/crear", methods=["POST"])
def crear():

    nombre = request.form["nombre"].strip()
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    Jugador.query.delete()

    partido = Partido.query.first()

    if partido:
        partido.nombre = nombre
        partido.fecha = fecha
        partido.hora = hora
    else:
        partido = Partido(
            nombre=nombre,
            fecha=fecha,
            hora=hora
        )
        db.session.add(partido)

    db.session.commit()

    jugadores = {
        "partido": {
            "nombre": nombre,
            "fecha": fecha,
            "hora": hora
        },
        "equipo1": [],
        "equipo2": []
    }

    session.pop("jugador_id", None)

    return render_template(
        "index.html",
        jugadores=jugadores
    )


@app.route("/partido")
def partido():

    partido = Partido.query.first()

    jugadores = {
        "partido": {
            "nombre": partido.nombre,
            "fecha": partido.fecha,
            "hora": partido.hora
        },
        "equipo1": [],
        "equipo2": []
    }

    jugadores["equipo1"] = [
        {
            "id": jugador.id,
            "nombre": jugador.nombre
        }
        for jugador in Jugador.query.filter_by(equipo="equipo1").all()
    ]

    jugadores["equipo2"] = [
        {
            "id": jugador.id,
            "nombre": jugador.nombre
        }
        for jugador in Jugador.query.filter_by(equipo="equipo2").all()
    ]

    return render_template(
        "index.html",
        jugadores=jugadores
    )


@app.route("/agregar", methods=["POST"])
def agregar():

    nombre = request.form["nombre"].strip()
    equipo = request.form["equipo"]

    if nombre == "":
        return partido_con_mensaje("Escribe tu nombre.")

    # Evitar que el mismo navegador se registre dos veces
    jugador_id_actual = session.get("jugador_id")

    if jugador_id_actual:

        jugador_actual = db.session.get(
            Jugador,
            jugador_id_actual
        )

        if jugador_actual:

            return partido_con_mensaje(
                "Ya estás apuntado. Sal primero si quieres cambiar de equipo."
            )

    # Comprobar nombre repetido
    jugadores_existentes = Jugador.query.all()

    for jugador in jugadores_existentes:

        if jugador.nombre.lower() == nombre.lower():

            return partido_con_mensaje(
                "Ese nombre ya está registrado."
            )

    # Comprobar máximo de jugadores
    cantidad = Jugador.query.filter_by(
        equipo=equipo
    ).count()

    if cantidad >= MAX_JUGADORES:

        return partido_con_mensaje(
            "Ese equipo ya está lleno. Máximo 4 jugadores."
        )

    jugador_id = str(uuid.uuid4())

    jugador = Jugador(
        id=jugador_id,
        nombre=nombre,
        equipo=equipo
    )

    db.session.add(jugador)
    db.session.commit()

    session["jugador_id"] = jugador_id

    return partido()


@app.route("/salir", methods=["POST"])
def salir():

    jugador_id = session.get("jugador_id")

    if not jugador_id:

        return partido_con_mensaje(
            "No se pudo identificar tu jugador."
        )

    jugador = db.session.get(
        Jugador,
        jugador_id
    )

    if not jugador:

        return partido_con_mensaje(
            "No se encontró tu jugador."
        )

    db.session.delete(jugador)
    db.session.commit()

    session.pop("jugador_id", None)

    return partido()


def partido_con_mensaje(mensaje):

    partido = Partido.query.first()

    jugadores = {
        "partido": {
            "nombre": partido.nombre,
            "fecha": partido.fecha,
            "hora": partido.hora
        },
        "equipo1": [],
        "equipo2": []
    }

    jugadores["equipo1"] = [
        {
            "id": jugador.id,
            "nombre": jugador.nombre
        }
        for jugador in Jugador.query.filter_by(equipo="equipo1").all()
    ]

    jugadores["equipo2"] = [
        {
            "id": jugador.id,
            "nombre": jugador.nombre
        }
        for jugador in Jugador.query.filter_by(equipo="equipo2").all()
    ]

    return render_template(
        "index.html",
        jugadores=jugadores,
        mensaje=mensaje
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )