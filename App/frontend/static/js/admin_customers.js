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

document.addEventListener('DOMContentLoaded', loadCustomers);
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') search();
});








