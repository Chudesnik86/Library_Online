// Admin Issues Management Script

// Store current issues data for sorting and export
let currentIssuesData = [];
let currentSortColumn = 'date_issued'; // Default sort by "Дата выдачи"
let currentSortDirection = 'desc'; // Default descending (newest first)

async function loadIssues() {
    const status = document.getElementById('status-filter').value;
    try {
        const url = status === 'all' ? '/api/issues' : `/api/issues?status=${status}`;
        const issues = await apiCall(url);
        
        // Store issues data
        currentIssuesData = issues;
        currentSortColumn = 'date_issued';
        currentSortDirection = 'desc';
        
        // Sort by date_issued descending by default
        sortIssuesData();
        
        // Show export button
        document.getElementById('export-csv-btn').style.display = 'inline-block';
        
        displayIssues(currentIssuesData);
    } catch (error) {
        showAlert('Ошибка загрузки: ' + error.message, 'danger');
    }
}

function sortIssuesData() {
    if (!currentIssuesData || currentIssuesData.length === 0) return;
    
    currentIssuesData.sort((a, b) => {
        let aVal = a[currentSortColumn];
        let bVal = b[currentSortColumn];
        
        // Handle date strings
        if (currentSortColumn === 'date_issued' || currentSortColumn === 'date_return' || currentSortColumn === 'return_date') {
            // For return_date, calculate it from date_issued
            if (currentSortColumn === 'return_date') {
                if (a.date_issued) {
                    const aDate = new Date(a.date_issued);
                    aDate.setDate(aDate.getDate() + 21);
                    if (a.extended) {
                        aDate.setDate(aDate.getDate() + 7);
                    }
                    aVal = aDate.toISOString().split('T')[0];
                } else {
                    aVal = '0000-01-01';
                }
                if (b.date_issued) {
                    const bDate = new Date(b.date_issued);
                    bDate.setDate(bDate.getDate() + 21);
                    if (b.extended) {
                        bDate.setDate(bDate.getDate() + 7);
                    }
                    bVal = bDate.toISOString().split('T')[0];
                } else {
                    bVal = '0000-01-01';
                }
            } else {
                aVal = aVal || '0000-01-01'; // Put empty dates at the beginning for desc, end for asc
                bVal = bVal || '0000-01-01';
            }
        }
        
        // Handle numeric values
        if (currentSortColumn === 'id') {
            aVal = parseInt(aVal) || 0;
            bVal = parseInt(bVal) || 0;
        }
        
        // Handle string values
        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }
        
        let comparison = 0;
        if (aVal < bVal) {
            comparison = -1;
        } else if (aVal > bVal) {
            comparison = 1;
        }
        
        return currentSortDirection === 'asc' ? comparison : -comparison;
    });
}

window.sortIssuesTable = function(column) {
    if (currentSortColumn === column) {
        // Toggle direction if same column
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        // New column, default to ascending
        currentSortColumn = column;
        currentSortDirection = 'asc';
    }
    
    sortIssuesData();
    displayIssues(currentIssuesData);
    updateSortIndicators();
}

function updateSortIndicators() {
    // Clear all indicators
    document.querySelectorAll('[id^="sort-indicator-"]').forEach(el => {
        el.textContent = '';
    });
    
    // Set indicator for current column
    const indicatorId = `sort-indicator-${currentSortColumn}`;
    const indicator = document.getElementById(indicatorId);
    if (indicator) {
        indicator.textContent = currentSortDirection === 'asc' ? ' ↑' : ' ↓';
    }
}

function displayIssues(issues) {
    const tbody = document.getElementById('issues-table');
    if (issues.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">Выдачи не найдены</td></tr>';
        return;
    }

    tbody.innerHTML = issues.map(issue => {
        const daysOut = Math.floor((new Date() - new Date(issue.date_issued)) / (1000 * 60 * 60 * 24));
        // Calculate overdue: 21 days + 7 days if extended
        const loanPeriod = 21 + (issue.extended ? 7 : 0);
        const isOverdue = issue.status === 'issued' && daysOut > loanPeriod;
        
        // Calculate return date (date_issued + 21 days, + 7 days if extended)
        let returnDate = '';
        if (issue.date_issued) {
            const issuedDate = new Date(issue.date_issued);
            const returnDateObj = new Date(issuedDate);
            returnDateObj.setDate(returnDateObj.getDate() + 21);
            // Add 7 more days if extended
            if (issue.extended) {
                returnDateObj.setDate(returnDateObj.getDate() + 7);
            }
            returnDate = returnDateObj.toISOString().split('T')[0];
        }
        
        return `
            <tr style="${isOverdue ? 'background-color: #ffebee;' : ''}">
                <td>${issue.id}</td>
                <td>${issue.book_title}</td>
                <td>${issue.customer_name}</td>
                <td>${issue.date_issued}</td>
                <td>${returnDate || 'Не указана'}</td>
                <td>${issue.date_return || 'Не возвращена'}</td>
                <td>
                    <span style="color: ${issue.status === 'issued' ? 'var(--warning-color)' : 'var(--success-color)'}">
                        ${issue.status === 'issued' ? 'На руках' : 'Возвращена'}
                    </span>
                </td>
                <td>
                    ${issue.status === 'issued' ? 
                        `<div style="display: flex; gap: 0.5rem;">
                            <button class="btn btn-success" onclick="returnBook(${issue.id})">Вернуть</button>
                            <button class="btn btn-info" onclick="extendIssue(${issue.id})" ${issue.extended ? 'disabled title="Выдача уже была продлена"' : 'title="Продлить на 7 дней"'}>Продлить</button>
                        </div>` :
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
        
        // Store issues data
        currentIssuesData = issues;
        currentSortColumn = 'date_issued';
        currentSortDirection = 'desc';
        
        // Sort by date_issued descending by default
        sortIssuesData();
        
        displayIssues(currentIssuesData);
        updateSortIndicators();
    } catch (error) {
        showAlert('Ошибка поиска: ' + error.message, 'danger');
    }
}

async function showIssueModal() {
    document.getElementById('issue-modal').classList.add('active');
    
    // Load books
    try {
        const response = await apiCall('/api/books?available=true');
        // API returns paginated response with 'books' array
        const books = response.books || response; // Support both paginated and non-paginated responses
        const bookSelect = document.getElementById('book-select');
        if (Array.isArray(books)) {
        bookSelect.innerHTML = books.map(b => 
            `<option value="${b.id}">${b.title} (${b.available_copies} доступно)</option>`
        ).join('');
        } else {
            bookSelect.innerHTML = '<option value="">Ошибка загрузки книг</option>';
            showAlert('Ошибка: неверный формат данных книг', 'danger');
        }
    } catch (error) {
        showAlert('Ошибка загрузки книг: ' + error.message, 'danger');
        const bookSelect = document.getElementById('book-select');
        bookSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
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
    const confirmed = await confirmAction('Отметить книгу как возвращенную?', 'Возврат книги');
    if (!confirmed) return;

    try {
        await apiCall(`/api/issues/${issueId}/return`, { method: 'POST' });
        showAlert('Книга возвращена!', 'success');
        loadIssues();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
}

async function extendIssue(issueId) {
    if (!issueId) {
        showAlert('Ошибка: запись не выбрана', 'danger');
        return;
    }
    
    const confirmed = await confirmAction('Продлить срок возврата книги на 7 дней?', 'Продление выдачи');
    if (!confirmed) return;

    try {
        const result = await apiCall(`/api/issues/${issueId}/extend`, { method: 'POST' });
        if (result.success) {
            showAlert(result.message || 'Выдача успешно продлена на 7 дней!', 'success');
            loadIssues();
        } else {
            showAlert(result.error || 'Ошибка при продлении', 'danger');
        }
    } catch (error) {
        showAlert('Ошибка: ' + (error.message || 'Не удалось продлить выдачу'), 'danger');
    }
}

window.extendIssue = extendIssue;

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
        
        const response = await fetch('/api/issues/import', {
            method: 'POST',
            headers: headers,
            body: formData
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            resultsDiv.innerHTML = `
                <div style="background: #FFEBEE; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <h3 style="margin-top: 0; color: #D32F2F;">❌ Ошибка</h3>
                    <p>Сервер вернул неверный формат ответа. Статус: ${response.status}</p>
                    <details style="margin-top: 0.5rem;"><summary style="cursor: pointer;">Показать ответ сервера</summary>
                    <pre style="font-size: 0.8rem; overflow: auto; max-height: 200px;">${text.substring(0, 500)}</pre></details>
                </div>
            `;
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            let resultHtml = `
                <div style="background: #E8F5E9; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <h3 style="margin-top: 0; color: #2E7D32;">✅ Импорт завершен</h3>
                    <p><strong>Успешно импортировано:</strong> ${data.imported} из ${data.total} выдач</p>
            `;
            
            if (data.failed > 0) {
                resultHtml += `<p style="color: #D32F2F;"><strong>Не удалось импортировать:</strong> ${data.failed} выдач</p>`;
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
            
            // Reload issues list
            loadIssues();
            
            // Auto-close modal after 3 seconds if all issues imported successfully
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
                errorHtml += `<details style="margin-top: 0.5rem;"><summary style="cursor: pointer;">Показать ошибки</summary><ul style="margin-top: 0.5rem;">`;
                data.errors.forEach(error => {
                    errorHtml += `<li style="font-size: 0.9rem;">${error}</li>`;
                });
                errorHtml += `</ul></details>`;
            }
            
            errorHtml += `</div>`;
            resultsDiv.innerHTML = errorHtml;
        }
    } catch (error) {
        console.error('Import error:', error);
        resultsDiv.innerHTML = `
            <div style="background: #FFEBEE; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <h3 style="margin-top: 0; color: #D32F2F;">❌ Ошибка</h3>
                <p>${error.message || 'Неизвестная ошибка при импорте'}</p>
                <p style="font-size: 0.9rem; color: #666;">Проверьте консоль браузера для подробностей.</p>
            </div>
        `;
    }
});

window.exportIssuesToCSV = function() {
    if (!currentIssuesData || currentIssuesData.length === 0) {
        showAlert('Нет данных для экспорта', 'warning');
        return;
    }

    // CSV headers
    const headers = ['ID', 'Книга', 'Читатель', 'Дата выдачи', 'Вернуть до', 'Дата возврата', 'Статус'];
    const csvRows = [headers.join(',')];

    // Add data rows (already sorted)
    currentIssuesData.forEach(item => {
        // Calculate return date (date_issued + 21 days, + 7 days if extended)
        let returnDate = '';
        if (item.date_issued) {
            const issuedDate = new Date(item.date_issued);
            const returnDateObj = new Date(issuedDate);
            returnDateObj.setDate(returnDateObj.getDate() + 21);
            // Add 7 more days if extended
            if (item.extended) {
                returnDateObj.setDate(returnDateObj.getDate() + 7);
            }
            returnDate = returnDateObj.toISOString().split('T')[0];
        }
        
        const row = [
            item.id || '',
            `"${(item.book_title || '').replace(/"/g, '""')}"`,
            `"${(item.customer_name || '').replace(/"/g, '""')}"`,
            item.date_issued || '',
            returnDate || 'Не указана',
            item.date_return || 'Не возвращена',
            item.status === 'issued' ? 'На руках' : 'Возвращена'
        ];
        csvRows.push(row.join(','));
    });

    // Create CSV content
    const csvContent = csvRows.join('\n');
    
    // Add BOM for UTF-8 to ensure proper encoding in Excel
    const BOM = '\uFEFF';
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
    
    // Create download link
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    // Generate filename with current date
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const filename = `история_выдач_${dateStr}.csv`;
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showAlert('Данные экспортированы в CSV!', 'success');
}

// Add hover effects for sortable headers
function addHeaderHoverEffects() {
    const headers = document.querySelectorAll('.sortable-header');
    headers.forEach(header => {
        header.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#E5E7EB';
        });
        header.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadIssues();
    setTimeout(() => {
        addHeaderHoverEffects();
        updateSortIndicators();
    }, 100);
});

document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') search();
});








