from datetime import datetime
from src.model.database import db
from .sqla_table import Generic_sql_object

class User(Generic_sql_object, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    alias = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    system_admin = db.Column(db.Boolean, nullable=False, default=False)
    role_id = db.Column(db.BigInteger, db.ForeignKey('roles.id'))
    inserted_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    role = db.relationship('Role', back_populates='users')

    __table_args__ = (
        db.Index('idx_user_role', 'role_id'),
    )

    def __init__(self, email, alias, password, role_id=None, enabled=True, system_admin=False):
        self.email = email
        self.alias = alias
        self.password = password
        self.enabled = enabled
        self.system_admin = system_admin
        self.role_id = role_id

    def __repr__(self):
        return f'<User #{self.id} alias="{self.alias}" activo="{self.enabled}">'