from flask import Blueprint, jsonify, request
from depo_control.models import (
    Deposito, Mercadoria, Usuario, Movimentacao
)
from ..auth.auth_utils import authentication_required, get_current_account
from ..helpers.serialize_data import serialize_solititacoes
from sqlalchemy import desc

bp = Blueprint('main_get_endpoints', __name__, url_prefix='/api')


@bp.route('/mercadorias', methods=['GET'])
@authentication_required(roles=['admin', 'funcio'])
def mercadorias():
    mercadorias = Mercadoria.query.all()

    data = []

    for mercadoria in mercadorias:
        data.append({
            'id': mercadoria.id,
            'nome': mercadoria.nome,
            'unidade': mercadoria.unidade
        })

    return jsonify(data)


@bp.route('/usuarios', methods=['GET'])
@authentication_required(roles=['admin', 'funcio'])
def funcionarios():

    conta = get_current_account()
    if conta.role == 'admin':
        usuarios = Usuario.query.filter_by(role='admin').all()
    elif conta.role == 'funcio':
        usuarios = Usuario.query.filter_by(role='funcio').all()

    data = []

    for usuario in usuarios:
        data.append({
            'id': usuario.id,
            'nome': usuario.nome
        })

    return jsonify(data)


@bp.route('/depositos', methods=['GET'])
@authentication_required(roles=['admin', 'funcio'])
def depositos():

    data = []

    dps = Deposito.query.all()

    for dp in dps:
        data.append({
            'id': dp.id,
            'nome': dp.nome,
        })

    return jsonify(data)


@bp.route('/solicitacoes', methods=['GET'])
@authentication_required(roles=['admin', 'funcio'])
def get_solicitacoes():

    conta = get_current_account()

    solicitacoes = (
        Movimentacao.query
        .filter_by(status='solicitada')
        .order_by(desc(Movimentacao.id))
        .all()
    )

    if conta.role == 'admin':
        # Admin tem acesso a todas as solicitações, inclusive as feitas por ele mesmo.
        rv = serialize_solititacoes(solicitacoes)

    elif conta.role == 'funcio':
        args = request.args  # FORMATO: ?id=`deposito_id`
        deposito_id = int(args['id'])

        solicitacoes_filtradas = filtrar_solicitacoes_funcio(solicitacoes, deposito_id)

        rv = serialize_solititacoes(solicitacoes_filtradas)

    return jsonify(rv)


def filtrar_solicitacoes_funcio(solicitacoes, deposito_id: int):

    solicitacoes_filtradas = filter(lambda mov: mov.atualizacoes[0].usuario.role == 'admin',
        filter(lambda mov: mov.deposito_id == deposito_id, solicitacoes)
    )

    return list(solicitacoes_filtradas)
