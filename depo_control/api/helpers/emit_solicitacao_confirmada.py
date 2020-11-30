from depo_control.models import Conexao, Movimentacao
from ..auth.auth_utils import get_current_account
from depo_control import socketio
from depo_control.exceptions import SocketError
from werkzeug.exceptions import InternalServerError
import sentry_sdk


def emit_solicitacao_confirmada(mov: Movimentacao):

    conta = get_current_account()

    if conta.role == 'admin':

        conexao_deposito = Conexao.query.filter_by(dispositivo=mov.deposito.nome).first()

        if conexao_deposito is None:
            raise SocketError('A solicitação foi confirmada, mas o dispositivo de destino não pôde ser notificado')

        try:
            socketio.emit('solicitacao_confirmada', {'id': mov.id}, room=conexao_deposito.id)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise SocketError('A solicitação foi confirmada, mas o dispositivo de destino não pôde ser notificado')

    elif conta.role == 'funcio':
        conexao_matriz = Conexao.query.filter_by(dispositivo='Matriz').first()

        if conexao_matriz is None:
            raise SocketError('A solicitação foi confirmada, mas o dispositivo de destino não pôde ser notificado')

        try:
            socketio.emit('solicitacao_confirmada', {'id': mov.id}, room=conexao_matriz.id)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise SocketError('A solicitação foi confirmada, mas o dispositivo de destino não pôde ser notificado')

    else:
        raise InternalServerError
