from flask import Blueprint, request
from depo_control import db
from depo_control.models import (
    Movimentacao, Ordem, Atualizacao
)
from ..auth.auth_utils import authentication_required
from ..helpers.sanitize_data import sanitize_solicitacao
from ..helpers.sanitize_data import sanitize_mov_dispatching as sanitize_confirmacao
from ..helpers.sanitize_data import sanitize_mov_dispatching as sanitize_cancelamento
from ..helpers.emit_nova_solicitacao import emit_nova_solicitacao
from ..helpers.emit_solicitacao_confirmada import emit_solicitacao_confirmada
from ..helpers.update_quantidades import update_quantidades_upon_mov_confirm

bp = Blueprint('movs', __name__, url_prefix='/api')


@bp.route('/solicitar_movimentacao', methods=['POST'])
@authentication_required(roles=['admin', 'funcio'])
def solicitar_movimentacao():

    data = request.get_json()
    sanitize_solicitacao(data)

    # Destructure data
    deposito_id = data['deposito_id']
    usuario_id = data['usuario_id']
    tipo_mov = data['tipo_mov']
    incoming_ordens = data['ordens']

    mov = Movimentacao(
        deposito_id=deposito_id,
        tipo=tipo_mov,
        status='solicitada'
    )

    ordens = []
    for ordem in incoming_ordens:
        ordens.append(Ordem(
            movimentacao=mov,
            mercadoria_id=ordem['mercadoria_id'],
            qtd=ordem['qtd'],
            deposito_id=deposito_id
        ))

    atualizacao = Atualizacao(
        movimentacao=mov,
        tipo='solicitacao',
        usuario_id=usuario_id
    )

    # adicionar ordens e atualização à mov
    mov.ordens = ordens
    mov.atualizacoes.append(atualizacao)

    db.session.add(mov)
    db.session.commit()

    # notification via web sockets
    emit_nova_solicitacao(deposito_id)

    return {
        'message': 'Sua solicitação foi enviada!'
    }, 200


@bp.route('/confirmar_solicitacao', methods=['POST'])
@authentication_required(roles=['admin', 'funcio'])
def confirmar_solicitacao():

    data = request.get_json()
    sanitize_confirmacao(data)

    # destructure data
    mov_id = data['mov_id']
    usuario_id = data['usuario_id']

    mov = Movimentacao.query.get(mov_id)

    update_quantidades_upon_mov_confirm(mov)

    nova_atualizacao = Atualizacao(
        movimentacao=mov,
        usuario_id=usuario_id,
        tipo="confirmacao",
    )

    mov.atualizacoes.append(nova_atualizacao)
    mov.status = 'confirmada'

    db.session.commit()

    # notification via web sockets
    emit_solicitacao_confirmada(mov)

    return {
        'message': 'A socitação foi confirmada!'
    }


@bp.route('/cancelar_solicitacao', methods=['POST'])
@authentication_required(roles=['admin', 'funcio'])
def cancelar_solicitacao():

    data = request.get_json()
    sanitize_cancelamento(data)

    # destructure data
    mov_id = data['mov_id']

    mov = Movimentacao.query.get(mov_id)

    db.session.delete(mov)
    db.session.commit()

    return {
        'message': 'A solicitação foi cancenlada'
    }
