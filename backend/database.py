import sqlite3


# ---- Veritabanı Oluşturma ve Hazırlama Fonksiyonu ----
def setup_database():
    """Kalıcı bir SQLite veritabanı dosyası oluşturur ve verileri yükler.
    
    Bu fonksiyon, veritabanı dosyası yoksa oluşturur ve örnek verileri ekler.
    Var olan verilere dokunmaz.
    """
    conn = sqlite3.connect('security_data.db')
    cursor = conn.cursor()

    # Veritabanı tablolarının var olup olmadığını kontrol edin
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guests'")
    if not cursor.fetchone():
        # Misafirler tablosunu oluşturun ve verileri ekleyin
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
        # Kargolar tablosunu oluşturun ve verileri ekleyin
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
        # Acil durumlar tablosunu oluşturun ve verileri ekleyin
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
        # Personel/Güvenlik tablosunu oluşturun ve verileri ekleyin
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
    # security_data.db dosyasının var olan konumunu belirtin
    return sqlite3.connect('data/security_data.db')

# ---- Kayıtları Çekme Fonksiyonu ----
def get_all_records():
    """
    Var olan veritabanındaki tüm tabloların verilerini döndürür.
    """
    # Her seferinde sıfırdan database oluşturmak yerine var olan dosyaya bağlanır.
    # Bu satırı değiştirdik: `conn = setup_database()` yerine `get_db_connection()` kullanıldı.
    conn = get_db_connection()
    cursor = conn.cursor()

    # Eğer database.py dosyanızda bu tablolar varsa
    tables = ["guests", "cargos", "emergencies", "staff"]
    records = {}

    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            col_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            records[table] = [dict(zip(col_names, row)) for row in rows]
        except sqlite3.OperationalError:
            # Eğer tablo bulunamazsa, bu hatayı yakala ve atla
            print(f"Uyarı: '{table}' tablosu bulunamadı.")
            records[table] = [] # Boş bir liste ekle

    conn.close()
    return records