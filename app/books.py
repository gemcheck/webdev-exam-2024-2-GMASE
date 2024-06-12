from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from functools import wraps
from models import db, Books, Users, Genres, Review, ConnectGenreBook, Covers 
from sqlalchemy.exc import SQLAlchemyError
import os
from flask import current_app
from werkzeug.utils import secure_filename
import bleach
import hashlib
import markdown


bp = Blueprint('books', __name__, url_prefix='/books')

# Допустимые расширения для изображения
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Сохрание обложки в таблицу covers
def save_cover_file(file):
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        raise ValueError("Недопустимый формат файла")
    
    file_data = file.read()
    md5_hash = hashlib.md5(file_data).hexdigest()
    mimetype = filename.rsplit('.', 1)[1].lower()
    
    # Запрос к базе данных, который проверяет, существует ли уже облажка с таким же хешем
    # Если существует, то мы используем уже имеющуюся обложку из базы данных
    existing_cover = db.session.query(Covers).filter_by(md5_hash=md5_hash).first()
    if existing_cover:
        return existing_cover.id_cover, None, None
    
    # Запрос к таблице covers, filename должно быть обязательно заполнено, поэтому присваиваем 
    # значение хэша. Здесь используется flush, он позволяет записывать данные в базу данных, 
    # но не фиксировать их, транзакция остается открытой до вызова commit. Это нужно чтобы получить 
    # id обложки и записать filename 
    new_cover = Covers(md5_hash=md5_hash, mimetype=mimetype, filename=f'{md5_hash}')
    db.session.add(new_cover)
    db.session.flush()

    cover_id = new_cover.id_cover
    new_cover.filename = f'{cover_id}'

    db.session.commit()

    file.seek(0)

    return cover_id, file_data, mimetype

# Добавление новой книги
@bp.route('/new_books', methods=['GET', 'POST'])
def new_books():
    if request.method == 'POST':
        try:
            name_book = request.form['name_book']
            year = request.form['year']
            short_description = bleach.clean(request.form['short_description'])
            publisher = request.form['publisher']
            author = request.form['author']
            pages = request.form['pages']
            selected_genre_ids = request.form.getlist('genres')

            cover_file = request.files['cover']
            if cover_file and cover_file.filename != '':
                cover_id, cover_data, mimetype = save_cover_file(cover_file)
            else:
                cover_id = None

            new_book = Books(
                name_book=name_book, 
                year=year, 
                short_description=short_description, 
                publisher=publisher, 
                author=author, 
                pages=pages, 
                id_cover=cover_id
            )
            db.session.add(new_book)
            db.session.commit()

            for id_genre in selected_genre_ids:
                connect = ConnectGenreBook(id_book=new_book.id_book, id_genre=int(id_genre))
                db.session.add(connect)
            
            db.session.commit()

            if cover_data:
                cover_path = os.path.join('static/images', f'{cover_id}.{mimetype}')
                cover_file.save(cover_path)

            flash('Книга успешно добавлена!', 'success')
            return redirect(url_for('index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        except ValueError as e:
            flash(str(e), 'danger')

    genres = db.session.query(Genres).all()
    return render_template('books/new_books.html', genres=genres)

# Редактирование книги
@bp.route('/edit_books/<int:id_book>', methods=['GET', 'POST'])
def edit_books(id_book):
    book = db.session.query(Books).get_or_404(id_book)
    
    if request.method == 'POST':
        try:
            book.name_book = request.form['name_book']
            book.year = request.form['year']
            book.short_description = bleach.clean(request.form['short_description'])

            selected_genre_ids = request.form.getlist('genres')
            db.session.query(ConnectGenreBook).filter(ConnectGenreBook.id_book == id_book).delete()
            for id_genre in selected_genre_ids:
                connect = ConnectGenreBook(id_book=id_book, id_genre=int(id_genre))
                db.session.add(connect)

            db.session.commit()
            flash('Книга успешно обновлена!', 'success')
            return redirect(url_for('index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
    
    genres = db.session.query(Genres).all()
    book_genres = [cg.id_genre for cg in db.session.query(ConnectGenreBook).filter_by(id_book=id_book).all()]
    return render_template('books/edit_books.html', book=book, genres=genres, book_genres=book_genres)