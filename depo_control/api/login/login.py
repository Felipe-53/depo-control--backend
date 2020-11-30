from flask import Blueprint, request, current_app
from depo_control import bcrypt
from depo_control.models import Conta
import jwt
from depo_control.exceptions import LoginError

bp = Blueprint('login', __name__, url_prefix='/api')


@bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    login = data['login']
    password = data['password']

    conta = Conta.query.filter_by(login=login).first()
    if conta is None:
        raise LoginError

    if bcrypt.check_password_hash(conta.password, password):
        token = jwt.encode(
            {'id': conta.id},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

        return {
            'jwt': token,
            'role': conta.role,
        }, 200

    raise LoginError
