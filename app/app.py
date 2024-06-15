from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from flask_migrate import Migrate
from models import db, Books, Genres, Review, ConnectGenreBook, Covers 
from auth import bp as auth_bp, init_login_manager
from books import bp as books_bp
from sqlalchemy import func
import bleach
import markdown

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

db.init_app(app)
migrate = Migrate(app, db)

init_login_manager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)

# Главная страница с пагинацией
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books_query = (
        db.session.query(
            Books.id_book,
            Books.name_book,
            func.group_concat(Genres.name_genre.distinct()).label('genres'),
            Books.year,
            func.round(func.avg(Review.rating), 1).label('avg_rating'),
            func.count(Review.id_review.distinct()).label('review_count'),
            Covers.filename,
            Covers.mimetype
        )
        .join(ConnectGenreBook, ConnectGenreBook.id_book == Books.id_book)
        .join(Genres, Genres.id_genre == ConnectGenreBook.id_genre)
        .outerjoin(Review, Review.id_book == Books.id_book)
        .outerjoin(Covers, Covers.id_cover == Books.id_cover)
        .group_by(Books.id_book, Books.name_book, Books.year, Covers.filename) 
        .order_by(Books.year.desc())
    )
    pagination = books_query.paginate(per_page=9, page=page)
    books = pagination.items
    return render_template("index.html", books=books, pagination=pagination)

# Написать рецензию
@app.route('/write_review/<int:id_book>', methods=['GET', 'POST'])
@login_required
def write_review(id_book):
    book = db.session.query(Books).get_or_404(id_book)
    existing_review = db.session.query(Review).filter_by(id_book=id_book, id_user=current_user.id_user).first()
    
    if existing_review:
        flash('Вы уже написали рецензию на эту книгу.', 'warning')
        return redirect(url_for('books.view_books', id_book=id_book))
    
    if request.method == 'POST':
        rating = request.form['rating']
        text = request.form['text']
        
        sanitized_text = bleach.clean(text)
        
        review = Review(rating=rating, text=sanitized_text, id_book=id_book, id_user=current_user.id_user)
        db.session.add(review)
        db.session.commit()
        
        flash('Рецензия успешно добавлена!', 'success')
        return redirect(url_for('books.view_books', id_book=id_book))
    
    return render_template('write_review.html', book=book)

