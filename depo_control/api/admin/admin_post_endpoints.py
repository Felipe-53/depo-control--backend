from flask import Blueprint, request
from depo_control.models import Ordem, Movimentacao, Atualizacao
from depo_control import db
from ..auth.auth_utils import authentication_required
from ..helpers.sanitize_data import sanitize_mov_canceling
from ..helpers.sanitize_data import sanitize_referencia
from ..helpers.sanitize_data import sanitize_solicitacao
from ..helpers.update_quantidades import update_quantidades_upon_mov_cancel
from ..helpers.update_quantidades import update_quantidades_upon_mov_confirm

bp = Blueprint('admin_post_endpoints', __name__, url_prefix='/api')


@bp.route('/estabelecer_referencia', methods=['POST'])
@authentication_required(roles=['admin'])
def referencia():

    data = request.get_json()
    sanitize_referencia(data)

    num_ordens = len(data)
    count_false = 0

    for ordem_data in data:

        referencia = ordem_data['referencia']

        ordem_id = ordem_data['id']
        ordem = Ordem.query.get(ordem_id)

        ordem.referencia = referencia

        if referencia is True:
            ordem.movimentacao.referencia = True
        else:
            count_false += 1

    if count_false == num_ordens:
        ordem.movimentacao.referencia = False

    db.session.commit()

    return {
        'message': 'As referências foram atualizadas'
    }, 200


@bp.route('/cancelar_movimentacao', methods=['POST'])
@authentication_required(roles=['admin'])
def cancelar_movimentacao():

    data = request.get_json()
    sanitize_mov_canceling(data)

    # destructure data
    mov_id = data['mov_id']
    usuario_id = data['usuario_id']

    mov = Movimentacao.query.get(mov_id)

    # uma mov cancelada não pode ser referência
    if mov.referencia is True:
        mov.referencia = False
        for ordem in mov.ordens:
            ordem.referencia = False

    update_quantidades_upon_mov_cancel(mov)

    nova_atualizacao = Atualizacao(
        movimentacao=mov,
        usuario_id=usuario_id,
        tipo="cancelamento",
    )

    mov.atualizacoes.append(nova_atualizacao)
    mov.status = 'cancelada'

    db.session.commit()

    return {
        'message': 'A movimentação foi cancelada'
    }, 200


@bp.route('/criar_ajuste', methods=['POST'])
@authentication_required(roles=['admin'])
def criar_ajuste():

    data = request.get_json()
    sanitize_solicitacao(data)

    # Destructure data
    deposito_id = data['deposito_id']
    usuario_id = data['usuario_id']
    tipo_mov = data['tipo_mov']
    incoming_ordens = data['ordens']

    # create Movimentacao
    mov = Movimentacao(
        deposito_id=deposito_id,
        tipo=tipo_mov,
        status='confirmada',
        ajuste=True
    )

    # create array of Ordem
    ordens = []
    for ordem in incoming_ordens:
        ordens.append(Ordem(
            movimentacao=mov,
            mercadoria_id=ordem['mercadoria_id'],
            qtd=ordem['qtd'],
            deposito_id=deposito_id
        ))

    # create atualizacao
    atualizacao = Atualizacao(
        movimentacao=mov,
        tipo='ajuste',
        usuario_id=usuario_id
    )

    # adicionar ordens e atualização à mov
    mov.ordens = ordens
    mov.atualizacoes.append(atualizacao)

    # update_quantidades
    update_quantidades_upon_mov_confirm(mov)

    db.session.add(mov)
    db.session.commit()

    return {
        'message': 'Seu ajuste foi confirmado'
    }, 200
