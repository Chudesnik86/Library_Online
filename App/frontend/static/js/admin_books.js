// Admin Books Management Script

let isEditMode = false;
let categoriesList = [];
let authorsList = [];
let selectedAuthors = []; // Array of {id: number, name: string, wikipedia_url: string} or {name: string, wikipedia_url: string} for new authors
let selectedCovers = []; // Array of cover URLs
let currentPage = 1;
let totalPages = 1;
let totalBooks = 0;
let booksPerPage = parseInt(localStorage.getItem('booksPerPage')) || 50; // Load from localStorage or default to 50

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

// Load authors
async function loadAuthors() {
    try {
        authorsList = await apiCall('/api/authors');
        const select = document.getElementById('author-select');
        if (select) {
            select.innerHTML = '<option value="">Выберите автора...</option>' + 
                authorsList.map(author => 
                    `<option value="${author.id}">${author.full_name}</option>`
                ).join('');
        }
    } catch (error) {
        console.error('Error loading authors:', error);
    }
}

// Add author from select
function addAuthorFromSelect() {
    const select = document.getElementById('author-select');
    const authorId = parseInt(select.value);
    if (!authorId) return;
    
    const author = authorsList.find(a => a.id === authorId);
    if (!author) return;
    
    // Check if already selected
    if (selectedAuthors.some(a => a.id === authorId)) {
        showAlert('Этот автор уже добавлен', 'warning');
        select.value = '';
        return;
    }
    
    selectedAuthors.push({
        id: author.id, 
        name: author.full_name,
        wikipedia_url: author.wikipedia_url || ''
    });
    select.value = '';
    updateSelectedAuthorsDisplay();
}

// Add new author (by name)
async function addNewAuthor() {
    const input = document.getElementById('new-author-input');
    const authorName = input.value.trim();
    
    if (!authorName) {
        showAlert('Введите имя автора', 'warning');
        return;
    }
    
    // Check if already selected
    if (selectedAuthors.some(a => a.name === authorName)) {
        showAlert('Этот автор уже добавлен', 'warning');
        input.value = '';
        return;
    }
    
    // Add as new author (will be created if needed)
    selectedAuthors.push({name: authorName, wikipedia_url: ''});
    input.value = '';
    updateSelectedAuthorsDisplay();
}

// Remove author
function removeAuthor(index) {
    selectedAuthors.splice(index, 1);
    updateSelectedAuthorsDisplay();
}

// Update selected authors display
function updateSelectedAuthorsDisplay() {
    const container = document.getElementById('selected-authors');
    if (!container) return;
    
    if (selectedAuthors.length === 0) {
        container.innerHTML = '<div style="color: var(--light-text); font-size: 0.9rem;">Авторы не выбраны</div>';
        return;
    }
    
    container.innerHTML = selectedAuthors.map((author, index) => `
        <div style="background: #F3F4F6; border: 1px solid #ddd; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong style="color: var(--primary-color);">${author.name}</strong>
                <button type="button" onclick="removeAuthor(${index})" 
                        style="background: var(--danger-color); border: none; 
                               color: white; cursor: pointer; border-radius: 50%; 
                               width: 24px; height: 24px; display: flex; align-items: center; 
                               justify-content: center; font-size: 0.9rem; padding: 0;">×</button>
            </div>
            <div>
                <label style="display: block; font-size: 0.85rem; color: var(--dark-text); margin-bottom: 0.25rem;">Ссылка на автора (Wikipedia и т.д.):</label>
                <input type="url" class="form-control" 
                       id="author-url-${index}" 
                       placeholder="https://ru.wikipedia.org/wiki/..." 
                       value="${author.wikipedia_url || ''}"
                       style="font-size: 0.9rem; padding: 0.4rem;"
                       onchange="updateAuthorUrl(${index}, this.value)" />
            </div>
        </div>
    `).join('');
}

// Update author URL
function updateAuthorUrl(index, url) {
    if (selectedAuthors[index]) {
        selectedAuthors[index].wikipedia_url = url;
    }
}

// Add cover
function addCover() {
    const input = document.getElementById('new-cover-input');
    const coverUrl = input.value.trim();
    
    if (!coverUrl) {
        showAlert('Введите URL обложки', 'warning');
        return;
    }
    
    // Basic URL validation
    try {
        new URL(coverUrl);
    } catch (e) {
        showAlert('Введите корректный URL', 'warning');
        return;
    }
    
    // Check if already added
    if (selectedCovers.includes(coverUrl)) {
        showAlert('Эта обложка уже добавлена', 'warning');
        input.value = '';
        return;
    }
    
    selectedCovers.push(coverUrl);
    input.value = '';
    updateSelectedCoversDisplay();
}

// Remove cover
function removeCover(index) {
    selectedCovers.splice(index, 1);
    updateSelectedCoversDisplay();
}

// Update selected covers display
function updateSelectedCoversDisplay() {
    const container = document.getElementById('selected-covers');
    if (!container) return;
    
    if (selectedCovers.length === 0) {
        container.innerHTML = '<div style="color: var(--light-text); font-size: 0.9rem;">Обложки не добавлены</div>';
        return;
    }
    
    container.innerHTML = selectedCovers.map((coverUrl, index) => `
        <div style="background: #F3F4F6; border: 1px solid #ddd; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1; margin-right: 0.5rem;">
                    <div style="font-size: 0.85rem; color: var(--dark-text); margin-bottom: 0.25rem;">Обложка ${index + 1}:</div>
                    <div style="font-size: 0.9rem; color: var(--primary-color); word-break: break-all;">${coverUrl}</div>
                </div>
                <button type="button" onclick="removeCover(${index})" 
                        style="background: var(--danger-color); border: none; 
                               color: white; cursor: pointer; border-radius: 50%; 
                               width: 28px; height: 28px; display: flex; align-items: center; 
                               justify-content: center; font-size: 0.9rem; padding: 0; flex-shrink: 0;">×</button>
            </div>
        </div>
    `).join('');
}

// Load all books with pagination
async function loadBooks(page = 1) {
    try {
        currentPage = page;
        const response = await apiCall(`/api/books?page=${page}&per_page=${booksPerPage}`);
        
        // Handle both old format (array) and new format (object with pagination)
        if (Array.isArray(response)) {
            displayBooks(response);
            document.getElementById('pagination-container').style.display = 'none';
        } else {
            displayBooks(response.books || []);
            totalPages = response.total_pages || 1;
            totalBooks = response.total || 0;
            updatePagination();
        }
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
            <td>${(book.author_names && book.author_names.length > 0) ? book.author_names.join(', ') : (book.author || '-')}</td>
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

// Search books with pagination
async function searchBooks(page = 1) {
    const searchTerm = document.getElementById('search-input').value;
    try {
        currentPage = page;
        const response = await apiCall(`/api/books?search=${encodeURIComponent(searchTerm)}&page=${page}&per_page=${booksPerPage}`);
        
        // Handle both old format (array) and new format (object with pagination)
        if (Array.isArray(response)) {
            displayBooks(response);
            document.getElementById('pagination-container').style.display = 'none';
        } else {
            displayBooks(response.books || []);
            totalPages = response.total_pages || 1;
            totalBooks = response.total || 0;
            updatePagination();
        }
    } catch (error) {
        showAlert('Ошибка поиска: ' + error.message, 'danger');
    }
}

// Update pagination controls
function updatePagination() {
    const container = document.getElementById('pagination-container');
    if (!container) return;
    
    if (totalPages <= 1) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'flex';
    container.style.flexDirection = 'row';
    
    // Update page info
    const start = totalBooks > 0 ? (currentPage - 1) * booksPerPage + 1 : 0;
    const end = Math.min(currentPage * booksPerPage, totalBooks);
    document.getElementById('pagination-info-start').textContent = start;
    document.getElementById('pagination-info-end').textContent = end;
    document.getElementById('pagination-info-total').textContent = totalBooks;
    document.getElementById('pagination-total-pages').textContent = totalPages;
    document.getElementById('pagination-page-input').value = currentPage;
    
    // Update buttons
    document.getElementById('pagination-prev').disabled = currentPage <= 1;
    document.getElementById('pagination-next').disabled = currentPage >= totalPages;
}

// Change page
function changePage(page) {
    if (page < 1 || page > totalPages) return;
    
    const searchTerm = document.getElementById('search-input').value;
    if (searchTerm) {
        searchBooks(page);
    } else {
        loadBooks(page);
    }
}

// Go to specific page
function goToPage(page) {
    if (page < 1) page = 1;
    if (page > totalPages) page = totalPages;
    changePage(page);
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
    selectedAuthors = [];
    selectedCovers = [];
    updateSelectedAuthorsDisplay();
    updateSelectedCoversDisplay();
    loadCategories(); // Refresh categories list
    loadAuthors(); // Load authors list
    document.getElementById('book-modal').classList.add('active');
}

// Edit book
async function editBook(book) {
    isEditMode = true;
    document.getElementById('modal-title').textContent = 'Редактировать книгу';
    document.getElementById('book-id').value = book.id;
    document.getElementById('book-title').value = book.title;
    document.getElementById('book-isbn').value = book.isbn || '';
    document.getElementById('book-category').value = book.category || '';
    document.getElementById('book-description').value = book.description || '';
    document.getElementById('book-total').value = book.total_copies;
    
    // Load covers
    selectedCovers = [];
    if (book.covers && book.covers.length > 0) {
        selectedCovers = book.covers.map(c => c.file_name || c);
    } else if (book.cover_image) {
        selectedCovers = [book.cover_image];
    }
    updateSelectedCoversDisplay();
    document.getElementById('book-available').value = book.available_copies;
    
    // Load authors and set selected authors
    await loadAuthors();
    selectedAuthors = [];
    
    // Use authors_info if available (includes wikipedia_url), otherwise fallback to author_names
    // Only use legacy author field if neither authors_info nor author_names are available
    if (book.authors_info && book.authors_info.length > 0) {
        // Use authors_info which includes wikipedia_url
        for (const authorInfo of book.authors_info) {
            const authorName = authorInfo.full_name || authorInfo.name;
            // Skip if already added (avoid duplicates)
            if (selectedAuthors.some(a => a.name === authorName)) {
                continue;
            }
            const existingAuthor = authorsList.find(a => a.full_name === authorName);
            if (existingAuthor) {
                selectedAuthors.push({
                    id: existingAuthor.id, 
                    name: existingAuthor.full_name,
                    wikipedia_url: authorInfo.wikipedia_url || existingAuthor.wikipedia_url || ''
                });
            } else {
                selectedAuthors.push({
                    name: authorName, 
                    wikipedia_url: authorInfo.wikipedia_url || ''
                });
            }
        }
    } else if (book.author_names && book.author_names.length > 0) {
        // Fallback to author_names if authors_info not available
        for (const authorName of book.author_names) {
            // Skip if already added (avoid duplicates)
            if (selectedAuthors.some(a => a.name === authorName)) {
                continue;
            }
            const existingAuthor = authorsList.find(a => a.full_name === authorName);
            if (existingAuthor) {
                selectedAuthors.push({
                    id: existingAuthor.id, 
                    name: existingAuthor.full_name,
                    wikipedia_url: existingAuthor.wikipedia_url || ''
                });
            } else {
                selectedAuthors.push({name: authorName, wikipedia_url: ''});
            }
        }
    } else if (book.author && (!book.authors_info || book.authors_info.length === 0) && (!book.author_names || book.author_names.length === 0)) {
        // Only parse legacy author field if no modern fields are available
        // Parse comma-separated authors from legacy field
        const authorNames = book.author.split(',').map(a => a.trim()).filter(a => a);
        for (const authorName of authorNames) {
            // Skip if already added (avoid duplicates)
            if (selectedAuthors.some(a => a.name === authorName)) {
                continue;
            }
            const existingAuthor = authorsList.find(a => a.full_name === authorName);
            if (existingAuthor) {
                selectedAuthors.push({
                    id: existingAuthor.id, 
                    name: existingAuthor.full_name,
                    wikipedia_url: existingAuthor.wikipedia_url || ''
                });
            } else {
                selectedAuthors.push({name: authorName, wikipedia_url: ''});
            }
        }
    }
    
    updateSelectedAuthorsDisplay();
    document.getElementById('book-modal').classList.add('active');
}

// Close modal
function closeModal() {
    document.getElementById('book-modal').classList.remove('active');
}

// Show book details modal
function showBookDetails(book) {
    document.getElementById('book-details-title-text').textContent = book.title;
    const authors = (book.author_names && book.author_names.length > 0) 
        ? book.author_names.join(', ') 
        : (book.author || 'Не указан');
    document.getElementById('book-details-author').textContent = authors;
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

    // Collect author names and info
    const authorNames = selectedAuthors.map(a => a.name);
    const authorsInfo = selectedAuthors.map(a => ({
        name: a.name,
        wikipedia_url: a.wikipedia_url || null
    }));
    
    const bookData = {
        title: document.getElementById('book-title').value,
        author: authorNames.join(', '), // Legacy field for backward compatibility
        author_names: authorNames, // New field for multiple authors
        authors_info: authorsInfo, // Full author info with URLs
        isbn: document.getElementById('book-isbn').value,
        category: document.getElementById('book-category').value,
        description: document.getElementById('book-description').value || null,
        cover_image: selectedCovers.length > 0 ? selectedCovers[0] : null, // Legacy field - first cover
        covers: selectedCovers.map(url => ({file_name: url})), // New field - all covers
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
    const confirmed = await confirmAction(
        'Вы уверены, что хотите удалить эту книгу?\n\nПри удалении будут также удалены:\n- Все связанные выдачи\n- Обложки\n- Связи с авторами\n- Связи с категориями\n- Связи с выставками', 
        'Удаление книги'
    );
    if (!confirmed) return;

    try {
        const result = await apiCall(`/api/books/${bookId}`, { method: 'DELETE' });
        if (result.success) {
            showAlert(result.message || 'Книга успешно удалена!', 'success');
            loadBooks();
        } else {
            showAlert(result.error || 'Ошибка удаления книги', 'danger');
        }
    } catch (error) {
        const errorMessage = error.message || 'Не удалось удалить книгу';
        showAlert('Ошибка удаления: ' + errorMessage, 'danger');
    }
}

// Change books per page
function changePerPage(perPage) {
    booksPerPage = perPage;
    localStorage.setItem('booksPerPage', perPage.toString());
    currentPage = 1; // Reset to first page
    const searchTerm = document.getElementById('search-input').value;
    if (searchTerm) {
        searchBooks(1);
    } else {
        loadBooks(1);
    }
}

// Load books and categories on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set per page selector to saved value
    const perPageSelect = document.getElementById('pagination-per-page');
    if (perPageSelect) {
        perPageSelect.value = booksPerPage;
    }
    
    loadBooks();
    loadCategories();
    loadAuthors(); // Load authors on page load
    
    // Add Enter key support for new author input
    const newAuthorInput = document.getElementById('new-author-input');
    if (newAuthorInput) {
        newAuthorInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addNewAuthor();
            }
        });
    }
    
    // Add Enter key support for new cover input
    const newCoverInput = document.getElementById('new-cover-input');
    if (newCoverInput) {
        newCoverInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addCover();
            }
        });
    }
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








