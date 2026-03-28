const API_BASE = '/api/';
let modal = null;

document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('transactionModal');
    if (modalElement) {
        modal = new bootstrap.Modal(modalElement);
    }
    loadStatuses();
    loadTypes();
    loadTransactions();
    loadCategoriesForFilter();
    loadSubcategoriesForFilter();
    
    const typeSelect = document.getElementById('type');
    const categorySelect = document.getElementById('category');
    if (typeSelect) typeSelect.addEventListener('change', loadCategories);
    if (categorySelect) categorySelect.addEventListener('change', loadSubcategories);
});

async function loadStatuses() {
    const resp = await fetch(API_BASE + 'statuses/');
    const data = await resp.json();
    const items = data.results || data;  // ← ЭТО КЛЮЧЕВОЕ!
    
    const select = document.getElementById('status');
    const filter = document.getElementById('filter-status');
    
    select.innerHTML = '<option value="">Выберите статус</option>';
    filter.innerHTML = '<option value="">Все статусы</option>';
    
    items.forEach(s => {
        select.innerHTML += `<option value="${s.id}">${s.name}</option>`;
        filter.innerHTML += `<option value="${s.id}">${s.name}</option>`;
    });
}

async function loadTypes() {
    const resp = await fetch(API_BASE + 'types/');
    const data = await resp.json();
    const items = data.results || data;
    
    const select = document.getElementById('type');
    const filter = document.getElementById('filter-type');
    
    select.innerHTML = '<option value="">Выберите тип</option>';
    filter.innerHTML = '<option value="">Все типы</option>';
    
    items.forEach(t => {
        select.innerHTML += `<option value="${t.id}">${t.name}</option>`;
        filter.innerHTML += `<option value="${t.id}">${t.name}</option>`;
    });
}

async function loadCategoriesForFilter() {
    const resp = await fetch(API_BASE + 'categories/');
    const data = await resp.json();
    const items = data.results || data;
    
    const filter = document.getElementById('filter-category');
    filter.innerHTML = '<option value="">Все категории</option>';
    
    items.forEach(c => {
        filter.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });
}

async function loadSubcategoriesForFilter() {
    const resp = await fetch(API_BASE + 'subcategories/');
    const data = await resp.json();
    const items = data.results || data;
    
    const filter = document.getElementById('filter-subcategory');
    filter.innerHTML = '<option value="">Все подкатегории</option>';
    
    items.forEach(s => {
        filter.innerHTML += `<option value="${s.id}">${s.name}</option>`;
    });
}

async function loadCategories() {
    const typeId = document.getElementById('type').value;
    const categorySelect = document.getElementById('category');
    if (!typeId) {
        categorySelect.innerHTML = '<option value="">Сначала выберите тип</option>';
        return;
    }
    const resp = await fetch(API_BASE + 'categories/?transaction_type=' + typeId);
    const data = await resp.json();
    const items = data.results || data;
    
    categorySelect.innerHTML = '<option value="">Выберите категорию</option>';
    items.forEach(c => {
        categorySelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });
}

async function loadSubcategories() {
    const catId = document.getElementById('category').value;
    const subSelect = document.getElementById('subcategory');
    if (!catId) {
        subSelect.innerHTML = '<option value="">Сначала выберите категорию</option>';
        return;
    }
    const resp = await fetch(API_BASE + 'subcategories/?category=' + catId);
    const data = await resp.json();
    const items = data.results || data;
    
    subSelect.innerHTML = '<option value="">Выберите подкатегорию</option>';
    items.forEach(s => {
        subSelect.innerHTML += `<option value="${s.id}">${s.name}</option>`;
    });
}

async function loadTransactions() {
    let url = API_BASE + 'transactions/';
    const params = new URLSearchParams();
    const dateFrom = document.getElementById('filter-date-from').value;
    const dateTo = document.getElementById('filter-date-to').value;
    const statusId = document.getElementById('filter-status').value;
    const typeId = document.getElementById('filter-type').value;
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    if (statusId) params.append('status_id', statusId);
    if (typeId) params.append('transaction_type_id', typeId);
    if (params.toString()) url += '?' + params.toString();
    
    const resp = await fetch(url);
    const data = await resp.json();
    const transactions = data.results || data;
    const tbody = document.getElementById('transactions-list');
    
    if (transactions.length === 0) {
        tbody.innerHTML = '有人<td colspan="8" class="text-center">Нет операций</tr>';
        return;
    }
    
    tbody.innerHTML = transactions.map(t => `
        <tr>
            <td>${t.date}</td>
            <td>${t.status_name || t.status}</td>
            <td>${t.type_name || t.transaction_type}</td>
            <td>${t.category_name || t.category}</td>
            <td>${t.subcategory_name || t.subcategory}</td>
            <td class="${t.transaction_type === 2 ? 'negative' : 'positive'}">${t.amount} ₽</td>
            <td>${t.comment || '-'}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editTransaction(${t.id})">✏️</button>
                <button class="btn btn-sm btn-danger" onclick="deleteTransaction(${t.id})">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function showAddForm() {
    if (!modal) {
        modal = new bootstrap.Modal(document.getElementById('transactionModal'));
    }
    document.getElementById('modalTitle').innerText = 'Добавить операцию';
    document.getElementById('transactionForm').reset();
    document.getElementById('edit-id').value = '';
    modal.show();
}

async function editTransaction(id) {
    const resp = await fetch(API_BASE + `transactions/${id}/`);
    const t = await resp.json();
    
    document.getElementById('modalTitle').innerText = 'Редактировать операцию';
    document.getElementById('edit-id').value = t.id;
    document.getElementById('date').value = t.date;
    document.getElementById('status').value = t.status;
    document.getElementById('type').value = t.transaction_type;
    document.getElementById('amount').value = t.amount;
    document.getElementById('comment').value = t.comment || '';
    
    await loadCategories();
    document.getElementById('category').value = t.category;
    await loadSubcategories();
    document.getElementById('subcategory').value = t.subcategory;
    
    if (!modal) {
        modal = new bootstrap.Modal(document.getElementById('transactionModal'));
    }
    modal.show();
}

async function saveTransaction() {
    const id = document.getElementById('edit-id').value;
    const data = {
        date: document.getElementById('date').value,
        status: parseInt(document.getElementById('status').value),
        transaction_type: parseInt(document.getElementById('type').value),
        category: parseInt(document.getElementById('category').value),
        subcategory: parseInt(document.getElementById('subcategory').value),
        amount: parseFloat(document.getElementById('amount').value),
        comment: document.getElementById('comment').value
    };
    
    const url = id ? API_BASE + `transactions/${id}/` : API_BASE + 'transactions/';
    const method = id ? 'PUT' : 'POST';
    
    const resp = await fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    
    if (resp.ok) {
        modal.hide();
        loadTransactions();
    } else {
        const err = await resp.json();
        alert('Ошибка: ' + JSON.stringify(err));
    }
}

async function deleteTransaction(id) {
    if (confirm('Удалить операцию?')) {
        await fetch(API_BASE + `transactions/${id}/`, {method: 'DELETE'});
        loadTransactions();
    }
}

function applyFilters() {
    loadTransactions();
}

function resetFilters() {
    document.getElementById('filter-date-from').value = '';
    document.getElementById('filter-date-to').value = '';
    document.getElementById('filter-status').value = '';
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-category').value = '';
    document.getElementById('filter-subcategory').value = '';
    loadTransactions();
}