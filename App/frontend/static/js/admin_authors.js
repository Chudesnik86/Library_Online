// Admin Authors Management Script

let isEditMode = false;

// Load all authors
async function loadAuthors() {
    try {
        const authors = await apiCall('/api/authors');
        displayAuthors(authors);
    } catch (error) {
        showAlert('Ошибка загрузки авторов: ' + error.message, 'danger');
    }
}

// Display authors in table
function displayAuthors(authors) {
    const tbody = document.getElementById('authors-table');
    if (authors.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Авторы не найдены</td></tr>';
        return;
    }

    tbody.innerHTML = authors.map(author => `
        <tr>
            <td>${author.id}</td>
            <td><strong>${author.full_name}</strong></td>
            <td>${author.birth_date || '-'}</td>
            <td>${author.death_date || '-'}</td>
            <td>${author.biography ? (author.biography.length > 50 ? author.biography.substring(0, 50) + '...' : author.biography) : '-'}</td>
            <td>${author.wikipedia_url ? '<a href="' + author.wikipedia_url + '" target="_blank">🔗</a>' : '-'}</td>
            <td>
                <button class="btn btn-primary" onclick="editAuthor(${JSON.stringify(author).replace(/"/g, '&quot;')})">✏️ Редактировать</button>
                <button class="btn btn-danger" onclick="deleteAuthor(${author.id}, '${author.full_name.replace(/'/g, "\\'")}')">🗑️ Удалить</button>
            </td>
        </tr>
    `).join('');
}

// Search authors
async function searchAuthors() {
    const searchTerm = document.getElementById('search-input').value;
    try {
        const authors = await apiCall('/api/authors');
        const filtered = authors.filter(a => 
            a.full_name.toLowerCase().includes(searchTerm.toLowerCase())
        );
        displayAuthors(filtered);
    } catch (error) {
        showAlert('Ошибка поиска: ' + error.message, 'danger');
    }
}

// Show add author modal
function showAddAuthorModal() {
    isEditMode = false;
    document.getElementById('modal-title').textContent = 'Добавить автора';
    document.getElementById('author-form').reset();
    document.getElementById('author-id').value = '';
    document.getElementById('author-modal').classList.add('active');
}

// Edit author
function editAuthor(author) {
    isEditMode = true;
    document.getElementById('modal-title').textContent = 'Редактировать автора';
    document.getElementById('author-id').value = author.id;
    document.getElementById('author-name').value = author.full_name || '';
    document.getElementById('author-birth-date').value = author.birth_date || '';
    document.getElementById('author-death-date').value = author.death_date || '';
    document.getElementById('author-biography').value = author.biography || '';
    document.getElementById('author-wikipedia').value = author.wikipedia_url || '';
    document.getElementById('author-modal').classList.add('active');
}

// Close modal
function closeModal() {
    document.getElementById('author-modal').classList.remove('active');
}

// Handle form submission
document.getElementById('author-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const authorData = {
        full_name: document.getElementById('author-name').value,
        birth_date: document.getElementById('author-birth-date').value || null,
        death_date: document.getElementById('author-death-date').value || null,
        biography: document.getElementById('author-biography').value || null,
        wikipedia_url: document.getElementById('author-wikipedia').value || null
    };

    try {
        if (isEditMode) {
            const authorId = document.getElementById('author-id').value;
            await apiCall(`/api/authors/${authorId}`, {
                method: 'PUT',
                body: JSON.stringify(authorData)
            });
            showAlert('Автор обновлен!', 'success');
        } else {
            await apiCall('/api/authors', {
                method: 'POST',
                body: JSON.stringify(authorData)
            });
            showAlert('Автор добавлен!', 'success');
        }
        closeModal();
        loadAuthors();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
});

// Delete author
async function deleteAuthor(authorId, authorName) {
    const confirmed = await confirmAction(`Вы уверены, что хотите удалить автора "${authorName}"?`, 'Удалить автора');
    if (!confirmed) return;

    try {
        await apiCall(`/api/authors/${authorId}`, { method: 'DELETE' });
        showAlert('Автор удален!', 'success');
        loadAuthors();
    } catch (error) {
        showAlert('Ошибка удаления: ' + error.message, 'danger');
    }
}

// Load authors on page load
document.addEventListener('DOMContentLoaded', loadAuthors);

// Search on Enter
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchAuthors();
});


