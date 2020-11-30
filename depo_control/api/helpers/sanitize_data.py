from depo_control.models import Quantidade, Movimentacao, Ordem
from depo_control.exceptions import BadRequestError
from werkzeug.exceptions import InternalServerError

""" Dados candidatos a entrarem no banco de dados
    devem ser minuciosamente examinados. Primeiramente
    verificamos que os dados que se espera realmente estão
    PRESENTES de depois verificamos se eles estão em FORMATO
    APROPRIADO. Qualquer exceção não capturada levantada aqui
    se transforma numa `Internal Server Error` com uma breve
    mensagem para o cliente (vide error_handling.py).
    Sentry automaticamente reporta erros que levam a
    Internal Server Error.
    Por outro lado, em certas ocasiões se faz necessário
    descontinuar a execução do código devido a problemas que
    não levantam erros nem exceções naturalmente. Para tanto,
    faz-se uso de exceções customizadas que se encontram em
    exceptions.py. Um error handler é registrado especificamente
    com esse tipo de exceção.
    Todas exceções se transformar em respostas json do servidor. """


def sanitize_solicitacao(data):
    deposito_id = data['deposito_id']
    usuario_id = data['usuario_id']
    tipo_mov = data['tipo_mov']
    ordens = data['ordens']

    assert type(deposito_id) == int and deposito_id > 0
    assert type(usuario_id) == int and usuario_id > 0
    assert tipo_mov == 'entrada' or tipo_mov == 'saida'
    assert type(ordens) == list
    assert len(ordens) != 0

    for ordem in ordens:

        mercadoria_id = ordem['mercadoria_id']
        qtd = ordem['qtd']

        assert type(mercadoria_id) == int and mercadoria_id > 0
        assert type(qtd) == int and qtd > 0

        quantidade = Quantidade.query.\
            filter_by(deposito_id=deposito_id).\
            filter_by(mercadoria_id=mercadoria_id).first()

        assert quantidade is not None

        if tipo_mov == 'saida' and quantidade.qtd - qtd < 0:
            raise BadRequestError('Você está tentando fazer\
            uma saída que resulta em um número negativo de\
            mercadorias. Favor verificar o estoque.')


def sanitize_mov_dispatching(data):
    mov_id = data['mov_id']
    usuario_id = data['usuario_id']

    assert type(mov_id) == int and mov_id > 0
    assert type(usuario_id) == int and usuario_id > 0

    mov = Movimentacao.query.get(mov_id)
    if mov is None:
        raise InternalServerError

    # É necessário garantir que a mov em questão tenha status de 'solicitada',
    # ao invés de possivelmente 'confirmada' ou 'cancelada'.
    if mov.status != 'solicitada':
        raise BadRequestError(f'A movimentação que você está tentando confirmar tem\
            status de `{mov.status}`')


def sanitize_mov_canceling(data):
    mov_id = data['mov_id']
    usuario_id = data['usuario_id']

    assert type(mov_id) == int and mov_id > 0
    assert type(usuario_id) == int and usuario_id > 0

    mov = Movimentacao.query.get(mov_id)
    if mov is None:
        raise InternalServerError

    # É necessário garantir que a mov em questão tenha status de 'confirmada',
    # ao invés de possivelmente 'solicitada' ou 'cancelada'.
    if mov.status != 'confirmada':
        raise BadRequestError(f'A movimentação que você está tentando cancelar tem\
            status de `{mov.status}`')


def sanitize_referencia(data):
    assert type(data) == list

    for ordem_data in data:

        ordem_id = ordem_data['id']
        assert type(ordem_id) == int and ordem_id > 0

        ordem = Ordem.query.get(ordem_id)
        assert ordem is not None

        referencia = ordem_data['referencia']
        assert type(referencia) is bool
