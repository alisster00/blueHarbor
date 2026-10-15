import hashlib
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20),  default="viewer")
    email         = db.Column(db.String(120), unique=True)

    def set_password(self, password: str) -> None:
        self.password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()        
        #self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return self.password_hash == hashlib.md5(password.encode("utf-8")).hexdigest()        
        #return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "username": self.username,
            "role":     self.role,
            "email":    self.email,
        }
