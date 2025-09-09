document.addEventListener('DOMContentLoaded', async () => {
    const statusMessage = document.getElementById('status-message');
    const recordsTable = document.getElementById('records-table');
    const recordsTableBody = document.getElementById('records-table-body');

    const API_URL = 'http://127.0.0.1:8000/admin/records';

    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`API yanıtı başarısız oldu: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        const tables = data.records; // API'den gelen sözlük

        let recordCount = 0;

        // Sözlükteki her bir tabloyu döngüye al
        for (const tableName in tables) {
            if (Object.hasOwnProperty.call(tables, tableName)) {
                const records = tables[tableName];

                records.forEach(record => {
                    const row = document.createElement('tr');
                    const recordType = tableName; // Tablo adı, kayıt tipi olarak kullanılacak

                    // Kaydın ID'sini, zamanını ve detaylarını oluştur
                    let id = record.id || 'N/A';
                    let timestamp = record.timestamp ? new Date(record.timestamp).toLocaleString('tr-TR') : 'N/A';
                    let details = JSON.stringify(record, null, 2); // Tüm kaydı detaylar sütununa yerleştir

                    // Eklenen tablodan bağımsız olarak her kayıt için yeni bir satır oluştur
                    row.innerHTML = `
                        <td>${id}</td>
                        <td>${recordType.charAt(0).toUpperCase() + recordType.slice(1)}</td>
                        <td>${timestamp}</td>
                        <td><pre>${details}</pre></td>
                    `;
                    recordsTableBody.appendChild(row);
                    recordCount++;
                });
            }
        }

        if (recordCount > 0) {
            statusMessage.style.display = 'none';
            recordsTable.style.display = 'table';
        } else {
            statusMessage.textContent = 'Veritabanında henüz kayıt bulunmamaktadır.';
        }

    } catch (error) {
        console.error('Veri çekme hatası:', error);
        statusMessage.textContent = 'Veriler yüklenirken bir hata oluştu. Sunucuya ulaşılamıyor.';
        statusMessage.classList.remove('loading-message');
        statusMessage.classList.add('error-message');
    }
});