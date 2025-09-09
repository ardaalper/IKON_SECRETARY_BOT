document.addEventListener('DOMContentLoaded', async () => {
    const statusMessage = document.getElementById('status-message');
    const adminContainer = document.querySelector('.admin-container'); // Ana kapsayıcıyı seçin
    
    const API_URL = 'http://127.0.0.1:8000/admin/records';

    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`API yanıtı başarısız oldu: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        const tables = data.records;
        
        // Veritabanı bağlantısında hata varsa veya veri gelmezse
        if (!tables || Object.keys(tables).length === 0) {
            statusMessage.textContent = 'Veritabanında henüz kayıt bulunmamaktadır.';
            return;
        }

        // Başlangıç mesajını gizle
        statusMessage.style.display = 'none';

        // Gelen her tablo için ayrı bir HTML tablosu oluştur
        for (const tableName in tables) {
            if (Object.hasOwnProperty.call(tables, tableName)) {
                const records = tables[tableName];

                // Yeni tablo için başlık ve kapsayıcı oluştur
                const tableTitle = document.createElement('h2');
                tableTitle.textContent = tableName.charAt(0).toUpperCase() + tableName.slice(1);
                adminContainer.appendChild(tableTitle);

                const tableContainer = document.createElement('div');
                tableContainer.classList.add('record-table-container');

                const table = document.createElement('table');
                table.classList.add('records-table');

                // Tablo başlıklarını (columns) oluştur
                if (records.length > 0) {
                    const headerRow = document.createElement('thead');
                    const headers = Object.keys(records[0]);
                    headerRow.innerHTML = `<tr>${headers.map(header => `<th>${header.charAt(0).toUpperCase() + header.slice(1)}</th>`).join('')}</tr>`;
                    table.appendChild(headerRow);
                }

                // Tablo gövdesini (rows) oluştur
                const tableBody = document.createElement('tbody');
                records.forEach(record => {
                    const row = document.createElement('tr');
                    const cells = Object.values(record);
                    row.innerHTML = cells.map(cell => `<td>${cell}</td>`).join('');
                    tableBody.appendChild(row);
                });
                table.appendChild(tableBody);
                
                tableContainer.appendChild(table);
                adminContainer.appendChild(tableContainer);
            }
        }
        
    } catch (error) {
        console.error('Veri çekme hatası:', error);
        statusMessage.textContent = 'Veriler yüklenirken bir hata oluştu. Sunucuya ulaşılamıyor.';
        statusMessage.classList.remove('loading-message');
        statusMessage.classList.add('error-message');
    }
});