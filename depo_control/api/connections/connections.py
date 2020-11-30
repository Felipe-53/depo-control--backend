from flask import request
from depo_control.models import Deposito, Conexao
from depo_control import db


def register_socketio_handlers(socketio):

    @socketio.on('manage_connection')
    def add_conn(dispositivo):

        dispositivos = []

        deps = Deposito.query.all()
        for dep in deps:
            dispositivos.append(dep.nome)
        dispositivos.append('Matriz')

        assert type(dispositivo) == str
        assert dispositivo in dispositivos

        sid = request.sid

        conn = Conexao.query.filter_by(
            dispositivo=dispositivo).first()

        if not conn:
            conn = Conexao(
                dispositivo=dispositivo,
                id=sid,
            )

            db.session.add(conn)
            db.session.commit()

        else:
            conn.id = sid
            db.session.commit()

        # manually close session afterwards
        db.session.close()
