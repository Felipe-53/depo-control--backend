from sqlalchemy import text
from depo_control.models import Quantidade, Ordem
from depo_control.exceptions import BadRequestError
from werkzeug.exceptions import InternalServerError


def update_quantidades_upon_mov_confirm(mov):

    for ordem in mov.ordens:
        mercadoria_id = ordem.mercadoria_id
        deposito_id = mov.deposito_id

        quantidade = Quantidade.query.filter_by(
            mercadoria_id=mercadoria_id).filter_by(
            deposito_id=deposito_id).first()
        if quantidade is None:
            raise InternalServerError

        if mov.tipo == 'entrada':
            ordem.antes = quantidade.qtd
            ordem.depois = quantidade.qtd + ordem.qtd

            quantidade.qtd += ordem.qtd

        elif mov.tipo == 'saida':
            if quantidade.qtd - ordem.qtd < 0:
                raise BadRequestError('Tentando confirmar uma solicitação\
                    que resulta em um número negativo de mercadorias.\
                    Favor verificar o estoque')

            ordem.antes = quantidade.qtd
            ordem.depois = quantidade.qtd - ordem.qtd

            quantidade.qtd -= ordem.qtd

        else:
            raise InternalServerError


def update_quantidades_upon_mov_cancel(mov):

    for ordem in mov.ordens:

        mercadoria_id = ordem.mercadoria_id
        deposito_id = ordem.deposito_id

        # adressing the issue of canceling a mov
        subsequent_ordens = Ordem.query.filter(text(f'id>{ordem.id}'))\
            .filter_by(mercadoria_id=mercadoria_id)\
            .filter_by(deposito_id=deposito_id).all()

        # mov with `solicitada` status are obviously out
        subsequent_ordens = list(filter(
            lambda ordem: ordem.movimentacao.status != 'solicitada',
            subsequent_ordens
        ))

        if len(subsequent_ordens) != 0:
            for ordem_to_update in subsequent_ordens:
                if mov.tipo == 'entrada':
                    ordem_to_update.antes -= ordem.qtd
                    ordem_to_update.depois -= ordem.qtd
                elif mov.tipo == 'saida':
                    ordem_to_update.antes += ordem.qtd
                    ordem_to_update.depois += ordem.qtd

        # finally, update quantidades table
        quantidade = Quantidade.query.filter_by(
            mercadoria_id=mercadoria_id).filter_by(
            deposito_id=deposito_id).first()
        if quantidade is None:
            raise InternalServerError

        if mov.tipo == 'entrada':

            """ Why comment this? We cannot allow qtds to be negative, can we?
            Well, imagine initially we had 0. Then we get +100. In another mov,
            we take up -25. Then if we realize that instead of +100, there
            entered +50, we would NOT be able to cancel the +100, because
            the next mov (-25) would result in negative value (even though
            we should be able to come in and and cancel the +100 add then
            add the actuall +50 instead). So we must allow negative values
            in the case of canceling a mov. Later we can adjust it
            manually."""
            # if quantidade.qtd - ordem.qtd < 0:
            #    raise BadRequestError('O cancelamento dessa movimentaçao\
            #        implica em um número negativo de mercadorias')

            quantidade.qtd -= ordem.qtd

        elif mov.tipo == 'saida':
            quantidade.qtd += ordem.qtd
