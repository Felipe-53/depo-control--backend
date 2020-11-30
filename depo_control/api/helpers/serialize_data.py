from datetime import timedelta


def serialize_solititacoes(solicitacoes):
    """ This helper revieces a list of Movimentacao instances
    that have 'solicitada' status and returns a list with the
    same information, but in a format ready to be jsonifyied. """

    # always returns a list: either empty or not
    rv = []

    for mov in solicitacoes:

        atualizacao = mov.atualizacoes[0]

        # taking care of the time first:
        # UTC - 3hrs = localtime
        local_datetime = atualizacao.datetime - timedelta(hours=3)

        mov_id = mov.id
        mov_tipo = mov.tipo
        hora = local_datetime.time().strftime('%H:%M')
        usuario_nome = atualizacao.usuario.nome
        deposito_nome = mov.deposito.nome

        ordens = []

        for ordem in mov.ordens:
            ordens.append({
                'qtd': ordem.qtd,
                'unidade': ordem.mercadoria.unidade,
                'nome': ordem.mercadoria.nome,
            })

        rv.append({
            'mov_id': mov_id,
            'mov_tipo': mov_tipo,
            'hora': hora,
            'usuario_nome': usuario_nome,
            'deposito_nome': deposito_nome,

            'ordens': ordens
        })

    return rv
