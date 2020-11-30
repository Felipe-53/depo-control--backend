from depo_control.models import Deposito, Conexao
from ..auth.auth_utils import get_current_account
from depo_control import socketio
from depo_control.exceptions import SocketError
import sentry_sdk


def emit_nova_solicitacao(deposito_id):

    conta = get_current_account()

    if conta.role == 'admin':
        dep = Deposito.query.get(deposito_id)
        conexao_deposito = Conexao.query.filter_by(dispositivo=dep.nome).first()
        if conexao_deposito is None:
            raise SocketError('Sua solicitação foi enviada, mas o dispositivo de destino não pôde ser notificado')

        try:
            socketio.emit('nova_solicitacao', room=conexao_deposito.id)
        except Exception as e:  # Exception 'cause I'm not sure what it might throw
            sentry_sdk.capture_exception(e)
            raise SocketError('Sua solicitação foi enviada, mas o dispositivo de destino não pôde ser notificado')

    elif conta.role == 'funcio':
        conexao = Conexao.query.filter_by(dispositivo='Matriz').first()
        if conexao is None:
            raise SocketError('Sua solicitação foi enviada, mas o dispositivo de destino não pôde ser notificado')

        try:
            socketio.emit('nova_solicitacao', room=conexao.id)
        except Exception as e:  # Exception 'cause I'm not sure what it might throw
            sentry_sdk.capture_exception(e)
            raise SocketError('Sua solicitação foi enviada, mas o dispositivo de destino não pôde ser notificado')
