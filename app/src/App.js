
const App = () => {
// Fetch and display all books
function fetchBooks() {
    fetch('http://127.0.0.1:5000/books')
        .then(response => response.json())
        .then(books => {
            const bookList = document.getElementById('book-list');
            bookList.innerHTML = '';
            books.forEach(book => {
                const li = document.createElement('li');
                li.textContent = `${book.title} by ${book.author} - Quantity: ${book.quantity}`;
                bookList.appendChild(li);
            });
        })
        .catch(error => console.error('Error fetching books:', error));
}

// Add a new book
document.getElementById('book-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const title = document.getElementById('book-title').value;
    const author = document.getElementById('book-author').value;
    const quantity = document.getElementById('book-quantity').value;

    const newBook = {
        id: Date.now(),
        title: title,
        author: author,
        quantity: quantity
    };

    fetch('http://127.0.0.1:5000/books', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(newBook)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);  // "Book added successfully!"
        fetchBooks();  // Refresh the book list after adding a new book
    })
    .catch(error => console.error('Error adding book:', error));
});

// Fetch books when the page loads
document.addEventListener('DOMContentLoaded', fetchBooks);

};

export default App; 
