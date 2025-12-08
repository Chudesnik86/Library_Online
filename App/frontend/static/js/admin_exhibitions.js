// Admin Exhibitions Management Script

let currentExhibitionId = null;
let currentExhibitionBooks = [];
let draggedElement = null;

// Load all exhibitions
async function loadExhibitions() {
    try {
        const exhibitions = await apiCall('/api/exhibitions');
        displayExhibitions(exhibitions);
    } catch (error) {
        showAlert('Ошибка загрузки выставок: ' + error.message, 'danger');
    }
}

// Display exhibitions in table
function displayExhibitions(exhibitions) {
    const tbody = document.getElementById('exhibitions-table');
    if (exhibitions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Выставки не найдены</td></tr>';
        return;
    }

    tbody.innerHTML = exhibitions.map(exhibition => {
        const startDate = exhibition.start_date ? new Date(exhibition.start_date).toLocaleDateString('ru-RU') : 'Не указана';
        const endDate = exhibition.end_date ? new Date(exhibition.end_date).toLocaleDateString('ru-RU') : 'Не указана';
        const period = `${startDate} - ${endDate}`;
        const bookCount = exhibition.books ? exhibition.books.length : 0;
        const isActive = exhibition.is_active;
        const statusClass = isActive ? 'success' : 'warning';
        const statusText = isActive ? 'Активна' : 'Неактивна';
        
        // Check if currently active based on dates
        const today = new Date();
        const start = exhibition.start_date ? new Date(exhibition.start_date) : null;
        const end = exhibition.end_date ? new Date(exhibition.end_date) : null;
        const currentlyActive = isActive && 
            (!start || today >= start) && 
            (!end || today <= end);

        return `
            <tr>
                <td>${exhibition.id}</td>
                <td><strong>${exhibition.title}</strong></td>
                <td>${exhibition.description || '-'}</td>
                <td>${period}</td>
                <td>${bookCount}</td>
                <td>
                    <span class="badge badge-${statusClass}">
                        ${statusText}${currentlyActive ? ' (активна сейчас)' : ''}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="manageBooks(${exhibition.id})" title="Управление книгами">
                        📚
                    </button>
                    <button class="btn btn-sm btn-info" onclick="previewExhibition(${exhibition.id})" title="Предпросмотр">
                        👁️
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="editExhibition(${JSON.stringify(exhibition).replace(/"/g, '&quot;')})" title="Редактировать">
                        ✏️
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="toggleExhibition(${exhibition.id}, ${!isActive})" title="${isActive ? 'Деактивировать' : 'Активировать'}">
                        ${isActive ? '⏸️' : '▶️'}
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteExhibition(${exhibition.id})" title="Удалить">
                        🗑️
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Show add exhibition modal
function showAddExhibitionModal() {
    currentExhibitionId = null;
    document.getElementById('exhibition-modal-title').textContent = 'Создать выставку';
    document.getElementById('exhibition-form').reset();
    document.getElementById('exhibition-id').value = '';
    document.getElementById('exhibition-is-active').checked = true;
    document.getElementById('exhibition-modal').classList.add('active');
}

// Edit exhibition
function editExhibition(exhibition) {
    currentExhibitionId = exhibition.id;
    document.getElementById('exhibition-modal-title').textContent = 'Редактировать выставку';
    document.getElementById('exhibition-id').value = exhibition.id;
    document.getElementById('exhibition-title').value = exhibition.title;
    document.getElementById('exhibition-description').value = exhibition.description || '';
    document.getElementById('exhibition-start-date').value = exhibition.start_date || '';
    document.getElementById('exhibition-end-date').value = exhibition.end_date || '';
    document.getElementById('exhibition-is-active').checked = exhibition.is_active;
    document.getElementById('exhibition-modal').classList.add('active');
}

// Close exhibition modal
function closeExhibitionModal() {
    document.getElementById('exhibition-modal').classList.remove('active');
    currentExhibitionId = null;
}

// Save exhibition
document.getElementById('exhibition-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const data = {
        title: document.getElementById('exhibition-title').value,
        description: document.getElementById('exhibition-description').value,
        start_date: document.getElementById('exhibition-start-date').value || null,
        end_date: document.getElementById('exhibition-end-date').value || null,
        is_active: document.getElementById('exhibition-is-active').checked
    };

    try {
        if (currentExhibitionId) {
            data.id = currentExhibitionId;
            const result = await apiCall(`/api/exhibitions/${currentExhibitionId}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            showAlert(result.message || 'Выставка обновлена', 'success');
        } else {
            const result = await apiCall('/api/exhibitions', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            showAlert(result.message || 'Выставка создана', 'success');
            // Open books management modal for new exhibition
            if (result.exhibition_id) {
                closeExhibitionModal();
                setTimeout(() => manageBooks(result.exhibition_id), 500);
            }
        }
        closeExhibitionModal();
        loadExhibitions();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
});

// Delete exhibition
async function deleteExhibition(exhibitionId) {
    const confirmed = await confirmAction('Вы уверены, что хотите удалить эту выставку?', 'Удаление выставки');
    if (!confirmed) return;

    try {
        const result = await apiCall(`/api/exhibitions/${exhibitionId}`, {
            method: 'DELETE'
        });
        showAlert(result.message || 'Выставка удалена', 'success');
        loadExhibitions();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
}

// Toggle exhibition status
async function toggleExhibition(exhibitionId, newStatus) {
    try {
        const result = await apiCall(`/api/exhibitions/${exhibitionId}/toggle`, {
            method: 'POST'
        });
        showAlert(result.message || 'Статус выставки изменен', 'success');
        loadExhibitions();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
}

// Manage books in exhibition
async function manageBooks(exhibitionId) {
    currentExhibitionId = exhibitionId;
    document.getElementById('books-modal-title').textContent = 'Управление книгами выставки';
    document.getElementById('book-search-results').style.display = 'none';
    document.getElementById('book-search-input').value = '';
    
    try {
        const exhibitionData = await apiCall(`/api/exhibitions/${exhibitionId}`);
        currentExhibitionBooks = exhibitionData.books || [];
        displayExhibitionBooks();
        document.getElementById('books-modal').classList.add('active');
    } catch (error) {
        showAlert('Ошибка загрузки выставки: ' + error.message, 'danger');
    }
}

// Close books modal
function closeBooksModal() {
    document.getElementById('books-modal').classList.remove('active');
    currentExhibitionId = null;
    currentExhibitionBooks = [];
}

// Display books in exhibition
function displayExhibitionBooks() {
    const list = document.getElementById('exhibition-books-list');
    if (currentExhibitionBooks.length === 0) {
        list.innerHTML = '<p style="color: #666; text-align: center; padding: 2rem;">В выставке пока нет книг. Используйте поиск выше, чтобы добавить книги.</p>';
        return;
    }

    list.innerHTML = currentExhibitionBooks.map((book, index) => `
        <div class="book-card" draggable="true" data-book-id="${book.id}" data-order="${index}">
            <div class="book-card-content">
                ${book.cover_image ? `<img src="${book.cover_image}" alt="${book.title}" class="book-cover-small" />` : '<div class="book-cover-placeholder">📖</div>'}
                <div class="book-info">
                    <h4>${book.title}</h4>
                    <p>${book.author || 'Автор не указан'}</p>
                    ${book.description ? `<p class="book-description-small">${book.description.substring(0, 100)}${book.description.length > 100 ? '...' : ''}</p>` : ''}
                </div>
                <div class="book-actions">
                    <button class="btn btn-sm btn-danger" onclick="removeBookFromExhibition('${book.id}')" title="Удалить">
                        🗑️
                    </button>
                    <span class="drag-handle" title="Перетащите для изменения порядка">☰</span>
                </div>
            </div>
        </div>
    `).join('');

    // Make list sortable
    initSortable();
}

// Initialize drag and drop
function initSortable() {
    const list = document.getElementById('exhibition-books-list');
    const items = list.querySelectorAll('.book-card');
    
    items.forEach(item => {
        item.addEventListener('dragstart', function(e) {
            draggedElement = this;
            this.style.opacity = '0.5';
        });

        item.addEventListener('dragend', function(e) {
            this.style.opacity = '1';
            draggedElement = null;
        });

        item.addEventListener('dragover', function(e) {
            e.preventDefault();
            if (draggedElement && draggedElement !== this) {
                const rect = this.getBoundingClientRect();
                const midpoint = rect.top + rect.height / 2;
                if (e.clientY < midpoint) {
                    list.insertBefore(draggedElement, this);
                } else {
                    list.insertBefore(draggedElement, this.nextSibling);
                }
            }
        });

        item.addEventListener('drop', function(e) {
            e.preventDefault();
            if (draggedElement && draggedElement !== this) {
                const rect = this.getBoundingClientRect();
                const midpoint = rect.top + rect.height / 2;
                if (e.clientY < midpoint) {
                    list.insertBefore(draggedElement, this);
                } else {
                    list.insertBefore(draggedElement, this.nextSibling);
                }
                updateBookOrder();
            }
        });
    });
}

// Update book order after drag and drop
function updateBookOrder() {
    const list = document.getElementById('exhibition-books-list');
    const items = list.querySelectorAll('.book-card');
    const newOrder = Array.from(items).map((item, index) => ({
        book_id: item.dataset.bookId,
        display_order: index + 1
    }));
    
    // Update local array order
    currentExhibitionBooks = newOrder.map(order => {
        return currentExhibitionBooks.find(b => b.id === order.book_id);
    }).filter(Boolean);
}

// Save book order
async function saveBookOrder() {
    if (!currentExhibitionId) return;
    
    updateBookOrder();
    const list = document.getElementById('exhibition-books-list');
    const items = list.querySelectorAll('.book-card');
    const bookOrders = Array.from(items).map((item, index) => ({
        book_id: item.dataset.bookId,
        display_order: index + 1
    }));

    try {
        const result = await apiCall(`/api/exhibitions/${currentExhibitionId}/books/order`, {
            method: 'PUT',
            body: JSON.stringify({ book_orders: bookOrders })
        });
        showAlert(result.message || 'Порядок книг сохранен', 'success');
        displayExhibitionBooks();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
}

// Search books for exhibition
async function searchBooksForExhibition() {
    const searchTerm = document.getElementById('book-search-input').value;
    if (!searchTerm) {
        document.getElementById('book-search-results').style.display = 'none';
        return;
    }

    try {
        const books = await apiCall(`/api/books?search=${encodeURIComponent(searchTerm)}`);
        displayBookSearchResults(books);
    } catch (error) {
        showAlert('Ошибка поиска: ' + error.message, 'danger');
    }
}

// Display book search results
function displayBookSearchResults(books) {
    const resultsDiv = document.getElementById('book-search-results');
    const list = document.getElementById('book-search-list');
    
    // Filter out books already in exhibition
    const existingBookIds = currentExhibitionBooks.map(b => b.id);
    const availableBooks = books.filter(b => !existingBookIds.includes(b.id));
    
    if (availableBooks.length === 0) {
        list.innerHTML = '<p style="color: #666; text-align: center; padding: 1rem;">Книги не найдены или все уже добавлены</p>';
        resultsDiv.style.display = 'block';
        return;
    }

    list.innerHTML = availableBooks.map(book => `
        <div class="book-card">
            <div class="book-card-content">
                ${book.cover_image ? `<img src="${book.cover_image}" alt="${book.title}" class="book-cover-small" />` : '<div class="book-cover-placeholder">📖</div>'}
                <div class="book-info">
                    <h4>${book.title}</h4>
                    <p>${book.author || 'Автор не указан'}</p>
                    ${book.description ? `<p class="book-description-small">${book.description.substring(0, 100)}${book.description.length > 100 ? '...' : ''}</p>` : ''}
                </div>
                <div class="book-actions">
                    <button class="btn btn-sm btn-success" onclick="addBookToExhibition('${book.id}')" title="Добавить">
                        ➕
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    resultsDiv.style.display = 'block';
}

// Add book to exhibition
async function addBookToExhibition(bookId) {
    if (!currentExhibitionId) return;
    
    // Check limit
    if (currentExhibitionBooks.length >= 12) {
        showAlert('В выставке может быть максимум 12 книг', 'warning');
        return;
    }

    try {
        const result = await apiCall(`/api/exhibitions/${currentExhibitionId}/books`, {
            method: 'POST',
            body: JSON.stringify({ book_id: bookId })
        });
        showAlert(result.message || 'Книга добавлена', 'success');
        
        // Reload exhibition books
        const exhibitionData = await apiCall(`/api/exhibitions/${currentExhibitionId}`);
        currentExhibitionBooks = exhibitionData.books || [];
        displayExhibitionBooks();
        
        // Clear search
        document.getElementById('book-search-input').value = '';
        document.getElementById('book-search-results').style.display = 'none';
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
}

// Remove book from exhibition
async function removeBookFromExhibition(bookId) {
    if (!currentExhibitionId) return;
    
    const confirmed = await confirmAction('Удалить эту книгу из выставки?', 'Удаление книги');
    if (!confirmed) return;

    try {
        const result = await apiCall(`/api/exhibitions/${currentExhibitionId}/books/${bookId}`, {
            method: 'DELETE'
        });
        showAlert(result.message || 'Книга удалена', 'success');
        
        // Reload exhibition books
        const exhibitionData = await apiCall(`/api/exhibitions/${currentExhibitionId}`);
        currentExhibitionBooks = exhibitionData.books || [];
        displayExhibitionBooks();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
}

// Preview exhibition
async function previewExhibition(exhibitionId) {
    try {
        const exhibitionData = await apiCall(`/api/exhibitions/${exhibitionId}`);
        const exhibition = exhibitionData.exhibition;
        const books = exhibitionData.books || [];
        
        const previewContent = document.getElementById('preview-content');
        previewContent.innerHTML = `
            <div class="exhibition-preview">
                <h2>${exhibition.title}</h2>
                ${exhibition.description ? `<p style="color: #666; margin-bottom: 1.5rem;">${exhibition.description}</p>` : ''}
                <div class="exhibition-books-grid">
                    ${books.map(book => `
                        <div class="book-card-preview">
                            ${book.cover_image ? `<img src="${book.cover_image}" alt="${book.title}" class="book-cover" />` : '<div class="book-cover-placeholder-large">📖</div>'}
                            <h4>${book.title}</h4>
                            <p>${book.author || 'Автор не указан'}</p>
                            ${book.description ? `<p class="book-description">${book.description.substring(0, 150)}${book.description.length > 150 ? '...' : ''}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.getElementById('preview-modal').classList.add('active');
    } catch (error) {
        showAlert('Ошибка загрузки выставки: ' + error.message, 'danger');
    }
}

// Close preview modal
function closePreviewModal() {
    document.getElementById('preview-modal').classList.remove('active');
}

// Close modals on background click
document.getElementById('exhibition-modal').addEventListener('click', function(e) {
    if (e.target === this) closeExhibitionModal();
});

document.getElementById('books-modal').addEventListener('click', function(e) {
    if (e.target === this) closeBooksModal();
});

document.getElementById('preview-modal').addEventListener('click', function(e) {
    if (e.target === this) closePreviewModal();
});

// Enter key for search
document.getElementById('book-search-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        searchBooksForExhibition();
    }
});

// Load exhibitions on page load
document.addEventListener('DOMContentLoaded', loadExhibitions);

