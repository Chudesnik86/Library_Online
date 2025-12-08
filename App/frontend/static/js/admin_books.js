// Admin Books Management Script

let isEditMode = false;
let categoriesList = [];

// Load categories
async function loadCategories() {
    try {
        categoriesList = await apiCall('/api/books/categories');
        const datalist = document.getElementById('category-list');
        if (datalist) {
            datalist.innerHTML = categoriesList.map(cat => 
                `<option value="${cat}">${cat}</option>`
            ).join('');
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

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
            <td>
                <a href="#" onclick="showBookDetails(${JSON.stringify(book).replace(/"/g, '&quot;')}); return false;" 
                   style="color: var(--primary-color); text-decoration: none; font-weight: 600; cursor: pointer;">
                   ${book.title}
                </a>
            </td>
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
    document.getElementById('book-id').value = '';
    document.getElementById('book-description').value = '';
    document.getElementById('book-cover-image').value = '';
    document.getElementById('book-category').value = '';
    loadCategories(); // Refresh categories list
    document.getElementById('book-modal').classList.add('active');
}

// Edit book
function editBook(book) {
    isEditMode = true;
    document.getElementById('modal-title').textContent = 'Редактировать книгу';
    document.getElementById('book-id').value = book.id;
    document.getElementById('book-title').value = book.title;
    document.getElementById('book-author').value = book.author || '';
    document.getElementById('book-isbn').value = book.isbn || '';
    document.getElementById('book-category').value = book.category || '';
    document.getElementById('book-description').value = book.description || '';
    document.getElementById('book-cover-image').value = book.cover_image || '';
    document.getElementById('book-total').value = book.total_copies;
    document.getElementById('book-available').value = book.available_copies;
    document.getElementById('book-modal').classList.add('active');
}

// Close modal
function closeModal() {
    document.getElementById('book-modal').classList.remove('active');
}

// Show book details modal
function showBookDetails(book) {
    document.getElementById('book-details-title-text').textContent = book.title;
    document.getElementById('book-details-author').textContent = book.author || 'Не указан';
    document.getElementById('book-details-isbn').textContent = book.isbn || 'Не указан';
    document.getElementById('book-details-category').textContent = book.category || 'Не указана';
    document.getElementById('book-details-id').textContent = book.id;
    document.getElementById('book-details-available').textContent = book.available_copies;
    document.getElementById('book-details-total').textContent = book.total_copies;
    document.getElementById('book-details-description').textContent = book.description || 'Описание отсутствует';
    
    const coverImg = document.getElementById('book-details-cover');
    if (book.cover_image) {
        coverImg.src = book.cover_image;
    } else {
        coverImg.src = 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'280\'%3E%3Crect fill=\'%23E5E7EB\' width=\'200\' height=\'280\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' fill=\'%239CA3AF\' font-size=\'14\'%3EНет обложки%3C/text%3E%3C/svg%3E';
    }
    
    document.getElementById('book-details-modal').classList.add('active');
}

function closeBookDetailsModal() {
    document.getElementById('book-details-modal').classList.remove('active');
}

// Close book details modal on background click
document.addEventListener('DOMContentLoaded', function() {
    const bookDetailsModal = document.getElementById('book-details-modal');
    if (bookDetailsModal) {
        bookDetailsModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeBookDetailsModal();
            }
        });
    }
});

// Handle form submission
document.getElementById('book-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const bookData = {
        title: document.getElementById('book-title').value,
        author: document.getElementById('book-author').value,
        isbn: document.getElementById('book-isbn').value,
        category: document.getElementById('book-category').value,
        description: document.getElementById('book-description').value || null,
        cover_image: document.getElementById('book-cover-image').value || null,
        total_copies: parseInt(document.getElementById('book-total').value),
        available_copies: parseInt(document.getElementById('book-available').value)
    };

    try {
        if (isEditMode) {
            // Include ID for editing
            bookData.id = document.getElementById('book-id').value;
            await apiCall(`/api/books/${bookData.id}`, {
                method: 'PUT',
                body: JSON.stringify(bookData)
            });
            showAlert('Книга обновлена!', 'success');
        } else {
            // Don't send ID for new books - it will be generated automatically
            await apiCall('/api/books', {
                method: 'POST',
                body: JSON.stringify(bookData)
            });
            showAlert('Книга добавлена!', 'success');
        }
        closeModal();
        loadBooks();
        loadCategories(); // Refresh categories list in case new category was added
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
});

// Delete book
async function deleteBook(bookId) {
    const confirmed = await confirmAction('Вы уверены, что хотите удалить эту книгу?', 'Удаление книги');
    if (!confirmed) return;

    try {
        await apiCall(`/api/books/${bookId}`, { method: 'DELETE' });
        showAlert('Книга удалена!', 'success');
        loadBooks();
    } catch (error) {
        showAlert('Ошибка удаления: ' + error.message, 'danger');
    }
}

// Load books and categories on page load
document.addEventListener('DOMContentLoaded', function() {
    loadBooks();
    loadCategories();
});

// Search on Enter
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchBooks();
});

// Import Excel functions
function showImportModal() {
    document.getElementById('import-modal').classList.add('active');
    document.getElementById('import-form').reset();
    document.getElementById('import-results').style.display = 'none';
    document.getElementById('import-results').innerHTML = '';
}

function closeImportModal() {
    document.getElementById('import-modal').classList.remove('active');
    document.getElementById('import-form').reset();
    document.getElementById('import-results').style.display = 'none';
    document.getElementById('import-results').innerHTML = '';
}

// Handle Excel import
document.getElementById('import-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('excel-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Пожалуйста, выберите файл', 'danger');
        return;
    }
    
    // Check file extension
    if (!file.name.toLowerCase().endsWith('.xlsx') && !file.name.toLowerCase().endsWith('.xls')) {
        showAlert('Поддерживаются только файлы Excel (.xlsx, .xls)', 'danger');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const resultsDiv = document.getElementById('import-results');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = '<div style="text-align: center; padding: 1rem;">Загрузка и обработка файла...</div>';
    
    try {
        const token = localStorage.getItem('jwt_token');
        const headers = {};
        
        // Don't set Content-Type for FormData - browser will set it automatically with boundary
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch('/api/books/import', {
            method: 'POST',
            headers: headers,
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            let resultHtml = `
                <div style="background: #E8F5E9; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <h3 style="margin-top: 0; color: #2E7D32;">✅ Импорт завершен</h3>
                    <p><strong>Успешно импортировано:</strong> ${data.imported} из ${data.total} книг</p>
            `;
            
            if (data.failed > 0) {
                resultHtml += `<p style="color: #D32F2F;"><strong>Не удалось импортировать:</strong> ${data.failed} книг</p>`;
            }
            
            if (data.errors && data.errors.length > 0) {
                resultHtml += `<details style="margin-top: 0.5rem;"><summary style="cursor: pointer; color: #D32F2F;">Показать ошибки</summary><ul style="margin-top: 0.5rem;">`;
                data.errors.forEach(error => {
                    resultHtml += `<li style="font-size: 0.9rem;">${error}</li>`;
                });
                resultHtml += `</ul></details>`;
            }
            
            if (data.parse_errors && data.parse_errors.length > 0) {
                resultHtml += `<details style="margin-top: 0.5rem;"><summary style="cursor: pointer; color: #F57C00;">Ошибки чтения файла</summary><ul style="margin-top: 0.5rem;">`;
                data.parse_errors.forEach(error => {
                    resultHtml += `<li style="font-size: 0.9rem;">${error}</li>`;
                });
                resultHtml += `</ul></details>`;
            }
            
            resultHtml += `</div>`;
            resultsDiv.innerHTML = resultHtml;
            
            // Reload books list
            loadBooks();
            
            // Auto-close modal after 3 seconds if all books imported successfully
            if (data.failed === 0) {
                setTimeout(() => {
                    closeImportModal();
                }, 3000);
            }
        } else {
            let errorHtml = `
                <div style="background: #FFEBEE; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <h3 style="margin-top: 0; color: #D32F2F;">❌ Ошибка импорта</h3>
                    <p>${data.error || 'Неизвестная ошибка'}</p>
            `;
            
            if (data.errors && data.errors.length > 0) {
                errorHtml += `<ul style="margin-top: 0.5rem;">`;
                data.errors.forEach(error => {
                    errorHtml += `<li style="font-size: 0.9rem;">${error}</li>`;
                });
                errorHtml += `</ul>`;
            }
            
            errorHtml += `</div>`;
            resultsDiv.innerHTML = errorHtml;
        }
    } catch (error) {
        resultsDiv.innerHTML = `
            <div style="background: #FFEBEE; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <h3 style="margin-top: 0; color: #D32F2F;">❌ Ошибка</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
});








