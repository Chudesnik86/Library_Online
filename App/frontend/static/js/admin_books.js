// Admin Books Management Script

let isEditMode = false;

// Load all books
async function loadBooks() {
    try {
        const books = await apiCall('/api/books');
        displayBooks(books);
    } catch (error) {
        showAlert('Ошибка загрузки книг: ' + error.message, 'danger');
    }
}

// Display books in table
function displayBooks(books) {
    const tbody = document.getElementById('books-table');
    if (books.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">Книги не найдены</td></tr>';
        return;
    }

    tbody.innerHTML = books.map(book => `
        <tr>
            <td>${book.id}</td>
            <td>${book.title}</td>
            <td>${book.author || '-'}</td>
            <td>${book.isbn || '-'}</td>
            <td>${book.category || '-'}</td>
            <td>${book.total_copies}</td>
            <td>${book.available_copies}</td>
            <td>
                <button class="btn btn-warning" onclick='editBook(${JSON.stringify(book)})'>✏️</button>
                <button class="btn btn-danger" onclick="deleteBook('${book.id}')">🗑️</button>
            </td>
        </tr>
    `).join('');
}

// Search books
async function searchBooks() {
    const searchTerm = document.getElementById('search-input').value;
    try {
        const books = await apiCall(`/api/books?search=${encodeURIComponent(searchTerm)}`);
        displayBooks(books);
    } catch (error) {
        showAlert('Ошибка поиска: ' + error.message, 'danger');
    }
}

// Show add book modal
function showAddBookModal() {
    isEditMode = false;
    document.getElementById('modal-title').textContent = 'Добавить книгу';
    document.getElementById('book-form').reset();
    document.getElementById('book-id-input').readOnly = false;
    document.getElementById('book-modal').classList.add('active');
}

// Edit book
function editBook(book) {
    isEditMode = true;
    document.getElementById('modal-title').textContent = 'Редактировать книгу';
    document.getElementById('book-id').value = book.id;
    document.getElementById('book-id-input').value = book.id;
    document.getElementById('book-id-input').readOnly = true;
    document.getElementById('book-title').value = book.title;
    document.getElementById('book-author').value = book.author || '';
    document.getElementById('book-isbn').value = book.isbn || '';
    document.getElementById('book-category').value = book.category || '';
    document.getElementById('book-total').value = book.total_copies;
    document.getElementById('book-available').value = book.available_copies;
    document.getElementById('book-modal').classList.add('active');
}

// Close modal
function closeModal() {
    document.getElementById('book-modal').classList.remove('active');
}

// Handle form submission
document.getElementById('book-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const bookData = {
        id: document.getElementById('book-id-input').value,
        title: document.getElementById('book-title').value,
        author: document.getElementById('book-author').value,
        isbn: document.getElementById('book-isbn').value,
        category: document.getElementById('book-category').value,
        total_copies: parseInt(document.getElementById('book-total').value),
        available_copies: parseInt(document.getElementById('book-available').value)
    };

    try {
        if (isEditMode) {
            await apiCall(`/api/books/${bookData.id}`, {
                method: 'PUT',
                body: JSON.stringify(bookData)
            });
            showAlert('Книга обновлена!', 'success');
        } else {
            await apiCall('/api/books', {
                method: 'POST',
                body: JSON.stringify(bookData)
            });
            showAlert('Книга добавлена!', 'success');
        }
        closeModal();
        loadBooks();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
});

// Delete book
async function deleteBook(bookId) {
    if (!confirm('Вы уверены, что хотите удалить эту книгу?')) return;

    try {
        await apiCall(`/api/books/${bookId}`, { method: 'DELETE' });
        showAlert('Книга удалена!', 'success');
        loadBooks();
    } catch (error) {
        showAlert('Ошибка удаления: ' + error.message, 'danger');
    }
}

// Load books on page load
document.addEventListener('DOMContentLoaded', loadBooks);

// Search on Enter
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchBooks();
});








