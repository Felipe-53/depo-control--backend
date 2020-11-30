from depo_control import db
from datetime import datetime, timezone

class Conta(db.Model):
    __tablename__ = 'contas'
    # STR UUID, specifically python's str(uuid.uuid4())
    id = db.Column(db.String, primary_key=True)
    login = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    telefone = db.Column(db.String, nullable=True)
    endereco = db.Column(db.String, nullable=True)
    atualizacoes = db.relationship('Atualizacao', back_populates='usuario')

class Deposito(db.Model):
    __tablename__ = 'depositos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    quantidades = db.relationship('Quantidade', back_populates='deposito')
    movimentacoes = db.relationship('Movimentacao', back_populates='deposito')
    localizacao = db.Column(db.String(100), nullable=True)
    ordens = db.relationship('Ordem', back_populates='deposito')

class Conexao(db.Model):
    __tablename__ = 'conexoes'
    pk = db.Column(db.Integer, primary_key=True)
    dispositivo = db.Column(db.String, nullable=False)
    id = db.Column(db.String, nullable=False)

class Mercadoria(db.Model):
    __tablename__ = 'mercadorias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    unidade = db.Column(db.String, nullable=False)
    quantidades = db.relationship('Quantidade', back_populates='mercadoria')
    fornecedor = db.Column(db.String(50), nullable=True)
    ordens = db.relationship('Ordem', back_populates='mercadoria')

class Quantidade(db.Model):
    __tablename__ = 'quantidades'
    id = db.Column(db.Integer, primary_key=True)
    
    mercadoria_id = db.Column(
        db.Integer, db.ForeignKey('mercadorias.id'), nullable=False
    )
    mercadoria = db.relationship('Mercadoria', back_populates='quantidades')
    
    deposito_id = db.Column(
        db.Integer, db.ForeignKey('depositos.id'), nullable=False
    )
    deposito = db.relationship('Deposito', back_populates='quantidades')

    qtd = db.Column(db.Integer, nullable=False)

    @property
    def unidade(self):
        return self.mercadoria.unidade


class Movimentacao(db.Model):
    __tablename__ = 'movimentacoes'
    id = db.Column(db.Integer, primary_key=True)

    tipo = db.Column(db.String(30), nullable=False) # Entrada/Saída
    status = db.Column(db.String(50), nullable=False) # Solicitada, Confirmada, Cancelada

    deposito_id = db.Column(db.Integer, db.ForeignKey('depositos.id'), nullable=False)
    deposito = db.relationship('Deposito', back_populates='movimentacoes')

    ordens = db.relationship(
        'Ordem',
        back_populates='movimentacao',
        cascade='all, delete-orphan',
    )
    atualizacoes = db.relationship(
        'Atualizacao',
        back_populates='movimentacao',
        cascade='all, delete-orphan',
    )

    referencia = db.Column(db.Boolean, default=False, nullable=False)
    ajuste = db.Column(db.Boolean, default=False, nullable=False)


class Ordem(db.Model):
    __tablename__ = 'ordens'
    id = db.Column(db.Integer, primary_key=True)
    
    movimentacao_id = db.Column(
        db.Integer, db.ForeignKey('movimentacoes.id'), nullable=False,
    )
    movimentacao = db.relationship('Movimentacao', back_populates='ordens')
    
    qtd = db.Column(db.Integer, nullable=False)
    
    mercadoria_id = db.Column(db.Integer, db.ForeignKey('mercadorias.id'), nullable=False)
    mercadoria = db.relationship('Mercadoria', back_populates='ordens')

    deposito_id = db.Column(db.Integer, db.ForeignKey('depositos.id'), nullable=False)
    deposito = db.relationship('Deposito', back_populates='ordens')

    # These three are going to be null before they're confirmed
    antes = db.Column(db.Integer, nullable=True)
    depois = db.Column(db.Integer, nullable=True)
    referencia = db.Column(db.Boolean, default=False, nullable=False)

class Atualizacao(db.Model):

    __tablename__ = 'atualizacoes'
    id = db.Column(db.Integer, primary_key=True)
    movimentacao_id = db.Column(
        db.Integer, db.ForeignKey('movimentacoes.id'), nullable=False,
    )
    movimentacao = db.relationship('Movimentacao', back_populates='atualizacoes')
    tipo = db.Column(db.String(50), nullable=False) # Solicitação, Confirmação, Cancelamento
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship('Usuario', back_populates='atualizacoes')
    datetime = db.Column(db.DateTime, default=lambda: datetime.now(tz=timezone.utc))
