// Admin Issues Management Script

async function loadIssues() {
    const status = document.getElementById('status-filter').value;
    try {
        const url = status === 'all' ? '/api/issues' : `/api/issues?status=${status}`;
        const issues = await apiCall(url);
        displayIssues(issues);
    } catch (error) {
        showAlert('Ошибка загрузки: ' + error.message, 'danger');
    }
}

function displayIssues(issues) {
    const tbody = document.getElementById('issues-table');
    if (issues.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Выдачи не найдены</td></tr>';
        return;
    }

    tbody.innerHTML = issues.map(issue => {
        const daysOut = Math.floor((new Date() - new Date(issue.date_issued)) / (1000 * 60 * 60 * 24));
        const isOverdue = issue.status === 'issued' && daysOut > 14;
        
        return `
            <tr style="${isOverdue ? 'background-color: #ffebee;' : ''}">
                <td>${issue.id}</td>
                <td>${issue.book_title}</td>
                <td>${issue.customer_name}</td>
                <td>${issue.date_issued}</td>
                <td>${issue.date_return || 'Не возвращена'}</td>
                <td>
                    <span style="color: ${issue.status === 'issued' ? 'var(--warning-color)' : 'var(--success-color)'}">
                        ${issue.status === 'issued' ? 'На руках' : 'Возвращена'}
                    </span>
                </td>
                <td>
                    ${issue.status === 'issued' ? 
                        `<button class="btn btn-success" onclick="returnBook(${issue.id})">Вернуть</button>` :
                        '-'
                    }
                </td>
            </tr>
        `;
    }).join('');
}

async function search() {
    const searchTerm = document.getElementById('search-input').value;
    try {
        const issues = await apiCall(`/api/issues?search=${encodeURIComponent(searchTerm)}`);
        displayIssues(issues);
    } catch (error) {
        showAlert('Ошибка поиска: ' + error.message, 'danger');
    }
}

async function showIssueModal() {
    document.getElementById('issue-modal').classList.add('active');
    
    // Load books
    try {
        const books = await apiCall('/api/books?available=true');
        const bookSelect = document.getElementById('book-select');
        bookSelect.innerHTML = books.map(b => 
            `<option value="${b.id}">${b.title} (${b.available_copies} доступно)</option>`
        ).join('');
    } catch (error) {
        showAlert('Ошибка загрузки книг: ' + error.message, 'danger');
    }

    // Load customers
    try {
        const customers = await apiCall('/api/customers');
        const customerSelect = document.getElementById('customer-select');
        customerSelect.innerHTML = customers.map(c => 
            `<option value="${c.id}">${c.name} (${c.id})</option>`
        ).join('');
    } catch (error) {
        showAlert('Ошибка загрузки читателей: ' + error.message, 'danger');
    }
}

function closeIssueModal() {
    document.getElementById('issue-modal').classList.remove('active');
}

document.getElementById('issue-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        book_id: document.getElementById('book-select').value,
        customer_id: document.getElementById('customer-select').value
    };

    try {
        await apiCall('/api/issues', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        showAlert('Книга выдана!', 'success');
        closeIssueModal();
        loadIssues();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
});

async function returnBook(issueId) {
    if (!confirm('Отметить книгу как возвращенную?')) return;

    try {
        await apiCall(`/api/issues/${issueId}/return`, { method: 'POST' });
        showAlert('Книга возвращена!', 'success');
        loadIssues();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
}

document.addEventListener('DOMContentLoaded', loadIssues);
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') search();
});








