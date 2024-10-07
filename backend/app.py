import os
from flask import Flask, make_response
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
def generate_nonce():
    return os.urandom(16).hex()  

@app.route('/')
def index():
    nonce = generate_nonce()
    response = make_response('<script nonce="{}">console.log("Inline script executed");</script>'.format(nonce))
    response.headers['Content-Security-Policy'] = "script-src 'self' 'nonce-{}'".format(nonce)
    return response

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    outstanding_debt = db.Column(db.Float, nullable=False, default=0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    fee_charged = db.Column(db.Float, nullable=True)

# CRUD for Books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{'id': book.id, 'title': book.title, 'author': book.author, 'quantity': book.quantity} for book in books])

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    new_book = Book(title=data['title'], author=data['author'], quantity=data['quantity'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully!'})

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get_or_404(id)
    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.quantity = data.get('quantity', book.quantity)
    db.session.commit()
    return jsonify({'message': 'Book updated successfully!'})

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully!'})

# CRUD for Members
@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([{'id': member.id, 'name': member.name, 'outstanding_debt': member.outstanding_debt} for member in members])

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Member added successfully!'})

# Issue and Return Book
@app.route('/issue', methods=['POST'])
def issue_book():
    data = request.get_json()
    member = Member.query.get(data['member_id'])
    book = Book.query.get(data['book_id'])
    
    if book and book.quantity > 0 and member:
        transaction = Transaction(book_id=book.id, member_id=member.id)
        book.quantity -= 1
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'message': 'Book issued successfully!'})
    else:
        return jsonify({'message': 'Cannot issue book. Check availability or member status.'})

@app.route('/return', methods=['POST'])
def return_book():
    data = request.get_json()
    transaction = Transaction.query.get(data['transaction_id'])
    transaction.return_date = datetime.utcnow()
    
    # Calculate rent fee 
    fee = calculate_fee(transaction.issue_date, transaction.return_date)
    transaction.fee_charged = fee
    
    member = Member.query.get(transaction.member_id)
    if member.outstanding_debt + fee > 500:
        return jsonify({'message': 'Outstanding debt exceeds limit. Cannot return book.'})
    
    member.outstanding_debt += fee
    
    # Update book quantity
    book = Book.query.get(transaction.book_id)
    book.quantity += 1
    
    db.session.commit()
    return jsonify({'message': 'Book returned successfully!'})

def calculate_fee(issue_date, return_date):
    # Example fee calculation logic
    days_rented = (return_date - issue_date).days
    fee = days_rented * 10  # Assuming KES 10 per day
    return fee

# Function to create tables within the app context
def create_tables():
    with app.app_context():  # Ensure that the app context is active
        db.create_all()  # This will create the tables
        print("Database tables created!")

if __name__ == '__main__':
    print("Starting Flask server...")
    create_tables() 
    app.run(debug=True)
     