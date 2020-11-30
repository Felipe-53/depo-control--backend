from flask import Blueprint, jsonify
from depo_control.models import (
    Deposito, Mercadoria, Movimentacao, Quantidade
)
from ..auth.auth_utils import authentication_required
from datetime import timedelta
from sqlalchemy import desc

bp = Blueprint('admin_get_endpoints', __name__, url_prefix='/api')


@bp.route('/quantidades', methods=['GET'])
@authentication_required(roles=['admin'])
def quantidades():

    depositos_query = Deposito.query.all()
    mercadorias_query = Mercadoria.query.all()
    quantidades_query = Quantidade.query.all()

    depositos = []
    mercadorias = []
    quantidades = []

    for deposito in depositos_query:
        depositos.append({
            'id': deposito.id,
            'nome': deposito.nome
        })

    for mercadoria in mercadorias_query:
        mercadorias.append({
            'id': mercadoria.id,
            'nome': mercadoria.nome
        })

    for quantidade in quantidades_query:
        quantidades.append({
            'deposito_id': quantidade.deposito_id,
            'mercadoria_id': quantidade.mercadoria_id,
            'qtd': quantidade.qtd
        })

    return jsonify({
        'depositos': depositos,
        'mercadorias': mercadorias,
        'quantidades': quantidades,
    })


@bp.route('/movimentacoes', methods=['GET'])
@authentication_required(roles=['admin'])
def movimentacoes():

    movs = (
        Movimentacao.query.
        order_by(desc(Movimentacao.id)).
        filter(Movimentacao.status != 'solicitada').
        limit(100).all()
    )

    rv = []

    for mov in movs:
        id_mov = mov.id

        deposito = {'id': mov.deposito.id, 'nome': mov.deposito.nome}
        tipo_mov = mov.tipo
        status = mov.status
        referencia = mov.referencia
        ajuste = mov.ajuste

        ordens = []

        for ordem in mov.ordens:
            ordens.append({
                'id': ordem.id,
                'mercadoria': {'id': ordem.mercadoria.id, 'unidade': ordem.mercadoria.unidade, 'nome': ordem.mercadoria.nome},
                'qtd': ordem.qtd,
                'antes': ordem.antes,
                'depois': ordem.depois,
                'referencia': ordem.referencia,
            })

        atualizacoes = []

        for atualizacao in mov.atualizacoes:
            atualizacoes.append({
                'tipo': atualizacao.tipo,
                'usuario': atualizacao.usuario.nome,
                'datetime': (atualizacao.datetime - timedelta(hours=3)).strftime('%d/%m/%y %H:%M')
            })

        # definir a data da última atualização
        last_index = len(mov.atualizacoes) - 1
        ultima_atualizacao = mov.atualizacoes[last_index]
        data_ultima_atualizacao = (ultima_atualizacao.datetime - timedelta(hours=3)).strftime('%d/%m/%y')

        rv.append({
            'id': id_mov,
            'deposito': deposito,
            'tipo_mov': tipo_mov,
            'status': status,
            'data_ultima_atualizacao':  data_ultima_atualizacao,


            'ordens': ordens,
            'atualizacoes': atualizacoes,

            'referencia': referencia,
            'ajuste': ajuste,
        })

    return jsonify(rv)
