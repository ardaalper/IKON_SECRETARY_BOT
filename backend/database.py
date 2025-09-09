import sqlite3
import os

# ---- Veritabanı Oluşturma ve Hazırlama Fonksiyonu ----
def setup_database():
    """Kalıcı bir SQLite veritabanı dosyası oluşturur ve verileri yükler.
    
    Bu fonksiyon, veritabanı dosyası yoksa oluşturur ve örnek verileri ekler.
    Var olan verilere dokunmaz.
    """
    if not os.path.exists('data'):
        os.makedirs('data')
        
    conn = sqlite3.connect('data/security_data.db')
    cursor = conn.cursor()

    # Veritabanı tablolarının var olup olmadığını kontrol edin
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guests'")
    if not cursor.fetchone():
        # Misafirler tablosunu oluşturun
        cursor.execute("""
            CREATE TABLE guests (
                id INTEGER PRIMARY KEY,
                name TEXT,
                personnel_name TEXT,
                arrival_date TEXT,
                status TEXT,
                note TEXT
            )
        """)
        
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cargos'")
    if not cursor.fetchone():
        # Kargolar tablosunu oluşturun
        cursor.execute("""
            CREATE TABLE cargos (
                id INTEGER PRIMARY KEY,
                personnel_name TEXT,
                cargo_id TEXT,
                company TEXT,
                status TEXT
            )
        """)

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emergencies'")
    if not cursor.fetchone():
        # Acil durumlar tablosunu oluşturun
        cursor.execute("""
            CREATE TABLE emergencies (
                id INTEGER PRIMARY KEY,
                type TEXT,
                contact TEXT,
                procedure TEXT
            )
        """)

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff'")
    if not cursor.fetchone():
        # Personel/Güvenlik tablosunu oluşturun
        cursor.execute("""
            CREATE TABLE staff (
                id INTEGER PRIMARY KEY,
                name TEXT,
                role TEXT
            )
        """)

    conn.commit()
    return conn

def get_db_connection():
    """Mevcut veritabanı dosyasına bağlantı kurar."""
    # 'data' klasörünün varlığını kontrol et, yoksa oluştur.
    if not os.path.exists('data'):
        os.makedirs('data')
    return sqlite3.connect('data/security_data.db')

# ---- Kayıtları Çekme Fonksiyonu ----
def get_all_records():
    """
    Var olan veritabanındaki tüm tabloların verilerini döndürür.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    tables = ["guests", "cargos", "emergencies", "staff"]
    records = {}

    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            col_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            records[table] = [dict(zip(col_names, row)) for row in rows]
        except sqlite3.OperationalError:
            print(f"Uyarı: '{table}' tablosu bulunamadı.")
            records[table] = []

    conn.close()
    return records
    
# database.py
def add_record(table_name, record_data):
    """Belirtilen tabloya yeni bir kayıt ekler."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL enjeksiyonunu önlemek için güvenli parametre kullanımı
    columns = ', '.join(record_data.keys())
    placeholders = ', '.join(['?' for _ in record_data])
    values = tuple(record_data.values())

    try:
        # Sorguyu yazdırmak hata ayıklamada yardımcı olabilir
        print(f"Executing SQL: INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) with values: {values}")
        cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        return {"success": True, "message": "Kayıt başarıyla eklendi."}
    except sqlite3.OperationalError as e:
        # Hata mesajını daha açıklayıcı yapın
        return {"success": False, "message": f"Kayıt ekleme hatası: {e}. Gönderilen veriler: {record_data}"}
    except Exception as e:
        return {"success": False, "message": f"Beklenmedik bir hata oluştu: {e}"}
    finally:
        conn.close()
        
# ---- YENİ: Kayıt Silme Fonksiyonu ----
def delete_record(table_name, record_id):
    """Belirtilen tablodaki ID'si verilen kaydı siler."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Kayıt başarıyla silindi."}
        else:
            return {"success": False, "message": "Silinecek kayıt bulunamadı."}
    except sqlite3.OperationalError as e:
        return {"success": False, "message": f"Kayıt silme hatası: {e}"}
    finally:
        conn.close()