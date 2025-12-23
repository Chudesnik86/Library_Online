// Admin Customers Management Script

let isEditMode = false;

async function loadCustomers() {
    try {
        const customers = await apiCall('/api/customers');
        displayCustomers(customers);
    } catch (error) {
        showAlert('Ошибка загрузки: ' + error.message, 'danger');
    }
}

function displayCustomers(customers) {
    const tbody = document.getElementById('customers-table');
    if (customers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Читатели не найдены</td></tr>';
        return;
    }

    tbody.innerHTML = customers.map(c => `
        <tr>
            <td>${c.id}</td>
            <td>${c.name}</td>
            <td>${c.address || '-'}</td>
            <td>${c.city || '-'}</td>
            <td>${c.phone || '-'}</td>
            <td>${c.email || '-'}</td>
            <td>
                <button class="btn btn-warning" onclick='edit(${JSON.stringify(c)})'>✏️</button>
                <button class="btn btn-danger" onclick="deleteCustomer('${c.id}')">🗑️</button>
            </td>
        </tr>
    `).join('');
}

async function search() {
    const searchTerm = document.getElementById('search-input').value;
    try {
        const customers = await apiCall(`/api/customers?search=${encodeURIComponent(searchTerm)}`);
        displayCustomers(customers);
    } catch (error) {
        showAlert('Ошибка поиска: ' + error.message, 'danger');
    }
}

function showAddModal() {
    isEditMode = false;
    document.getElementById('modal-title').textContent = 'Добавить читателя';
    document.getElementById('customer-form').reset();
    document.getElementById('modal').classList.add('active');
}

function edit(customer) {
    isEditMode = true;
    document.getElementById('modal-title').textContent = 'Редактировать читателя';
    // Store customer ID in a hidden field or data attribute
    document.getElementById('customer-form').dataset.customerId = customer.id;
    document.getElementById('customer-name').value = customer.name;
    document.getElementById('customer-address').value = customer.address || '';
    document.getElementById('customer-zip').value = customer.zip || '';
    document.getElementById('customer-city').value = customer.city || '';
    document.getElementById('customer-phone').value = customer.phone || '';
    document.getElementById('customer-email').value = customer.email || '';
    document.getElementById('modal').classList.add('active');
}

function closeModal() {
    document.getElementById('modal').classList.remove('active');
}

document.getElementById('customer-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        name: document.getElementById('customer-name').value,
        address: document.getElementById('customer-address').value,
        zip: parseInt(document.getElementById('customer-zip').value) || null,
        city: document.getElementById('customer-city').value,
        phone: document.getElementById('customer-phone').value,
        email: document.getElementById('customer-email').value
    };

    try {
        if (isEditMode) {
            // Include ID for editing
            data.id = document.getElementById('customer-form').dataset.customerId;
            await apiCall(`/api/customers/${data.id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            showAlert('Читатель обновлен!', 'success');
        } else {
            // Don't send ID for new customers - it will be generated automatically
            await apiCall('/api/customers', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            showAlert('Читатель добавлен!', 'success');
        }
        closeModal();
        loadCustomers();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
});

async function deleteCustomer(id) {
    const confirmed = await confirmAction('Вы уверены, что хотите удалить этого читателя?', 'Удаление читателя');
    if (!confirmed) return;

    try {
        await apiCall(`/api/customers/${id}`, { method: 'DELETE' });
        showAlert('Читатель удален!', 'success');
        loadCustomers();
    } catch (error) {
        showAlert('Ошибка: ' + error.message, 'danger');
    }
}

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
        
        const response = await fetch('/api/customers/import', {
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
                    <p><strong>Успешно импортировано:</strong> ${data.imported} из ${data.total} читателей</p>
            `;
            
            if (data.failed > 0) {
                resultHtml += `<p style="color: #D32F2F;"><strong>Не удалось импортировать:</strong> ${data.failed} читателей</p>`;
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
            
            // Reload customers list
            loadCustomers();
            
            // Auto-close modal after 3 seconds if all customers imported successfully
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

// Close modal on background click
document.getElementById('import-modal').addEventListener('click', function(e) {
    if (e.target === this) closeImportModal();
});

document.addEventListener('DOMContentLoaded', loadCustomers);
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') search();
});








