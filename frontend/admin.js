document.addEventListener('DOMContentLoaded', async () => {
    const statusMessage = document.getElementById('status-message');
    const adminContainer = document.querySelector('.admin-container');
    const API_URL = 'http://127.0.0.1:8000/admin/records';
    const ADD_API_URL = 'http://127.0.0.1:8000/admin/records/add';
    const DELETE_API_URL = 'http://127.0.0.1:8000/admin/records/delete';

    // Verilerin sütun başlıklarını manuel olarak tanımla
    const tableHeaders = {
        guests: ['name', 'personnel_name', 'arrival_date', 'status', 'note'],
        cargos: ['personnel_name', 'cargo_id', 'company', 'status'],
        emergencies: ['type', 'contact', 'procedure'],
        staff: ['name', 'role']
    };

    // Verileri API'den çekme ve tabloları oluşturma fonksiyonu
    const fetchAndRenderTables = async () => {
        try {
            statusMessage.textContent = 'Veriler yükleniyor...';
            statusMessage.style.display = 'block';
            
            const response = await fetch(API_URL);
            if (!response.ok) {
                throw new Error(`API yanıtı başarısız oldu: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            const tables = data.records;
            
            // Mevcut tabloları temizle
            adminContainer.querySelectorAll('.record-table-container, h2, .add-form, .message-container').forEach(el => el.remove());

            if (!tables || Object.keys(tables).length === 0) {
                statusMessage.textContent = 'Veritabanında henüz kayıt bulunmamaktadır.';
                return;
            }

            statusMessage.style.display = 'none';

            for (const tableName in tables) {
                if (Object.hasOwnProperty.call(tables, tableName)) {
                    const records = tables[tableName];

                    const tableTitle = document.createElement('h2');
                    tableTitle.textContent = tableName.charAt(0).toUpperCase() + tableName.slice(1);
                    adminContainer.appendChild(tableTitle);

                    const tableContainer = document.createElement('div');
                    tableContainer.classList.add('record-table-container');

                    const table = document.createElement('table');
                    table.classList.add('records-table');

                    // Tablo başlıklarını (columns) oluştur
                    // Düzeltme: Eğer kayıt yoksa, manuel olarak tanımlanan başlıkları kullan
                    const headers = records.length > 0 ? Object.keys(records[0]) : tableHeaders[tableName];
                    
                    if (headers) {
                        const headerRow = document.createElement('thead');
                        headerRow.innerHTML = `<tr>${headers.filter(h => h !== 'id').map(header => `<th>${header.charAt(0).toUpperCase() + header.slice(1)}</th>`).join('')}<th>İşlemler</th></tr>`;
                        table.appendChild(headerRow);
                    }

                    // Tablo gövdesini (rows) oluştur
                    const tableBody = document.createElement('tbody');
                    records.forEach(record => {
                        const row = document.createElement('tr');
                        const cells = Object.values(record);
                        row.innerHTML = cells.map(cell => `<td>${cell}</td>`).join('') +
                                        `<td><button class="delete-btn" data-id="${record.id}" data-table="${tableName}">Sil</button></td>`;
                        tableBody.appendChild(row);
                    });
                    table.appendChild(tableBody);
                    
                    tableContainer.appendChild(table);
                    adminContainer.appendChild(tableContainer);

                    // Ekleme formu oluştur
                    const addFormTemplate = document.getElementById('add-form-template');
                    const addFormClone = addFormTemplate.content.cloneNode(true);
                    const addForm = addFormClone.querySelector('.add-form');
                    
                    addForm.dataset.tableName = tableName;
                    
                    // Düzeltme: Eğer kayıt yoksa, manuel olarak tanımlanan başlıkları kullan
                    const formHeaders = records.length > 0 ? Object.keys(records[0]) : tableHeaders[tableName];
                    
                    if (formHeaders) {
                        formHeaders.forEach(header => {
                            if (header !== 'id') {
                                const input = document.createElement('input');
                                input.type = 'text';
                                input.name = header;
                                input.placeholder = header.charAt(0).toUpperCase() + header.slice(1);
                                addForm.insertBefore(input, addForm.lastElementChild);
                            }
                        });
                    }

                    adminContainer.appendChild(addFormClone);
                }
            }
        } catch (error) {
            console.error('Veri çekme hatası:', error);
            statusMessage.textContent = 'Veriler yüklenirken bir hata oluştu. Sunucuya ulaşılamıyor.';
            statusMessage.classList.remove('loading-message');
            statusMessage.classList.add('error-message');
        }
    };

    // Mesaj gösterme fonksiyonu
    const showMessage = (container, message, type) => {
        const messageContainer = document.createElement('div');
        messageContainer.textContent = message;
        messageContainer.className = `message-container ${type}`;
        container.appendChild(messageContainer);
        setTimeout(() => {
            container.removeChild(messageContainer);
        }, 3000);
    };

    // Kayıt ekleme fonksiyonu
    const addRecord = async (tableName, record) => {
        try {
            const response = await fetch(ADD_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ table_name: tableName, record: record })
            });

            const result = await response.json();
            if (response.ok) {
                showMessage(adminContainer, result.message, 'success');
                fetchAndRenderTables(); // Tabloyu yeniden yükle
            } else {
                showMessage(adminContainer, result.detail, 'error');
            }
        } catch (error) {
            showMessage(adminContainer, 'Kayıt eklenirken bir hata oluştu.', 'error');
            console.error('Kayıt ekleme hatası:', error);
        }
    };

    // Kayıt silme fonksiyonu
    const deleteRecord = async (tableName, recordId) => {
        if (confirm(`Bu kaydı silmek istediğinizden emin misiniz?`)) {
            try {
                const response = await fetch(DELETE_API_URL, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ table_name: tableName, record_id: parseInt(recordId) })
                });

                const result = await response.json();
                if (response.ok) {
                    showMessage(adminContainer, result.message, 'success');
                    fetchAndRenderTables(); // Tabloyu yeniden yükle
                } else {
                    showMessage(adminContainer, result.detail, 'error');
                }
            } catch (error) {
                showMessage(adminContainer, 'Kayıt silinirken bir hata oluştu.', 'error');
                console.error('Kayıt silme hatası:', error);
            }
        }
    };
    
    // Olay dinleyicisi: Form gönderme ve silme butonlarına tıklama
    adminContainer.addEventListener('submit', async (e) => {
        if (e.target.classList.contains('add-form')) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const newRecord = {};
            formData.forEach((value, key) => {
                newRecord[key] = value;
            });
            
            const currentTableName = e.target.dataset.tableName;
            await addRecord(currentTableName, newRecord);
        }
    });

    adminContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-btn')) {
            const table = e.target.dataset.table;
            const id = e.target.dataset.id;
            deleteRecord(table, id);
        }
    });

    // Sayfa yüklendiğinde tabloları getir
    fetchAndRenderTables();
});