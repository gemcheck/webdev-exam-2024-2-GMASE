from typing import Optional
import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, current_user
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, MetaData, Date, Integer, DateTime, Text
from datetime import datetime

class Base(DeclarativeBase):
  metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)

class Genres(Base):
   __tablename__ = 'genres'
   id_genre: Mapped[int] = mapped_column(primary_key=True)
   name_genre: Mapped[str] = mapped_column(String(128))

class Users(Base,  UserMixin):
   __tablename__ = 'users'
   id_user: Mapped[int] = mapped_column(primary_key=True)
   name: Mapped[str] = mapped_column(String(128))
   lastname: Mapped[str] = mapped_column(String(128))
   middlename: Mapped[Optional[str]] = mapped_column(String(128))
   login: Mapped[str] = mapped_column(String(32), unique=True)
   hash_pass: Mapped[str] = mapped_column(String(256))
   id_role: Mapped[int] = mapped_column(ForeignKey('roles.id_role', ondelete='CASCADE'))

   def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        return self.password_hash
   
   def check_password(self, password):
      return check_password_hash(self.hash_pass, password)

   @property
   def is_admin(self):
        return self.id_role == current_app.config['ADMIN_ROLE_ID']
   
   @property
   def is_moderator(self):
        return self.id_role == current_app.config['MODERATOR_ROLE_ID']

   def get_id(self):
      return str(self.id_user) 

class Review(Base):
    __tablename__ = 'reviews'
    id_review: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=sa.sql.func.now())
    id_book: Mapped[int] = mapped_column(ForeignKey('books.id_book', ondelete='CASCADE'), nullable=False)
    id_user: Mapped[int] = mapped_column(ForeignKey('users.id_user', ondelete='CASCADE'), nullable=False)

class Books(Base):
   __tablename__ = 'books'
   id_book: Mapped[int] = mapped_column(primary_key=True)
   name_book: Mapped[str] = mapped_column(String(128))
   short_description: Mapped[str] = mapped_column(Text())
   year: Mapped[int] = mapped_column(Integer())
   publisher: Mapped[str] = mapped_column(String(128))
   author: Mapped[str] = mapped_column(String(128))
   pages: Mapped[int] = mapped_column(Integer())
   id_cover: Mapped[int] = mapped_column(ForeignKey('covers.id_cover', ondelete='CASCADE'))

class Covers(Base):
   __tablename__ = 'covers'
   id_cover: Mapped[int] = mapped_column(primary_key=True)
   filename: Mapped[str] = mapped_column(String(128))
   mimetype: Mapped[str] = mapped_column(String(128))
   md5_hash: Mapped[str] = mapped_column(String(256), unique=True)

class Roles(Base):
   __tablename__ = 'roles'
   id_role: Mapped[int] = mapped_column(primary_key=True)
   name_role: Mapped[str] = mapped_column(String(128))
   description: Mapped[str] = mapped_column(Text())

class ConnectGenreBook(Base):
   __tablename__ = 'connect_genre_book'
   id_book: Mapped[int] = mapped_column(ForeignKey('books.id_book', ondelete='CASCADE'), primary_key=True)
   id_genre: Mapped[int] = mapped_column(ForeignKey('genres.id_genre', ondelete='CASCADE'), primary_key=True)
