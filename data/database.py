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

#setup_database()
