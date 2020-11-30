from flask import request, current_app, g
import functools
from depo_control.models import Conta
import jwt
from depo_control.exceptions import AuthError, PermissionError


def authentication_required(roles=[]):
    def inner(view):

        @functools.wraps(view)
        def decorated_view(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                raise AuthError('Login necessário')

            try:
                token = auth_header.split()[1]  # Authorization: Bearer <jwt>
            except IndexError:
                raise AuthError('Credenciais em formato inapropriado')

            try:
                payload = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )  # retuns a dict
            except jwt.InvalidTokenError:
                raise AuthError('Token inválido')

            conta_id = payload['id']
            conta = Conta.query.filter_by(id=conta_id).first()

            if not conta:
                raise AuthError('Conta não pode ser identificada')

            if conta.role not in roles:
                raise PermissionError('Conta não tem permissão')

            g.conta = conta

            return view(*args, **kwargs)

        return decorated_view

    return inner


def get_current_account():
    conta = getattr(g, 'conta', None)
    if conta is None:
        raise Exception
    return conta
