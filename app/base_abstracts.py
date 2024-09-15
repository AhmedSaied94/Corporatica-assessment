from app import db


class ParentAbstract(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    __abstract__ = True

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
