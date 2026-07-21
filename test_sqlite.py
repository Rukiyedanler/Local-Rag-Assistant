import json
import sqlite3

def main():
    print("====================================================")
    print("  2. Hafta - Adım 2: SQLite ile Yerel Veri Depolama ")
    print("====================================================")

    # 1. SQLite Veri Tabanı Bağlantısı Oluşturma
    # Sunucusuz, tek dosyalı yerel veri tabanımıza bağlanıyoruz.
    db_name = "local_rag_sandbox.db"
    print(f"[1/4] Yerel SQLite veri tabanına bağlanılıyor ('{db_name}')...")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 2. Tablo Oluşturma (SQL Sandbox)
    # id, content (metin) ve embedding (vektör verisi) kolonları oluşturuluyor.
    print("[2/4] 'documents' tablosu oluşturuluyor...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        embedding TEXT NOT NULL
    );
    """)
    
    # Önceki test verilerini temizleyelim (Sandbox izolasyonu için)
    cursor.execute("DELETE FROM documents;")
    conn.commit()

    # 3. Örnek Veri Ekleme (Text + Serialized Vector)
    # Gerçek senaryoda ürettiğimiz vektör dizilerini JSON formatında metin olarak saklıyoruz.
    sample_data = [
        (
            "Lumina-X kontrol panelinde mavi ışık 102 hatası için Reset butonuna 5 saniye basılı tutun.",
            json.dumps([0.5268, 0.1245, -0.0981, 0.4312])
        ),
        (
            "Kırmızı ışık 404 hatası aldığınızda MicroSD kartı çıkarıp tekrar takın.",
            json.dumps([0.4435, -0.3129, 0.8812, -0.1205])
        ),
        (
            "Güvenlik uyarısı: Cihazı kesinlikle nemli ortamlarda kullanmayın.",
            json.dumps([0.2521, 0.0012, 0.0543, 0.9912])
        )
    ]

    print("[3/4] Örnek metinler ve vektörler 'documents' tablosuna ekleniyor...")
    cursor.executemany(
        "INSERT INTO documents (content, embedding) VALUES (?, ?);",
        sample_data
    )
    conn.commit()
    print(f"-> {len(sample_data)} adet kayıt veri tabanına başarıyla yazıldı.")

    # 4. SELECT Sorgusu ile Veri Çekme Testi
    search_keyword = "mavi ışık"
    print(f"\n[4/4] Veri tabanında anahtar kelime ile arama yapılıyor: '{search_keyword}'...")
    
    cursor.execute(
        "SELECT id, content, embedding FROM documents WHERE content LIKE ?;",
        (f"%{search_keyword}%",)
    )
    results = cursor.fetchall()

    print("\n--- Veri Tabanı Sorgu Sonuçları ---")
    for row in results:
        doc_id, content, raw_embedding = row
        # JSON formatında sakladığımız vektörü tekrar Python listesine dönüştürüyoruz
        embedding_vector = json.loads(raw_embedding)
        
        print(f"ID: {doc_id}")
        print(f"İçerik: '{content}'")
        print(f"Saklanan Vektör (İlk 4 eleman): {embedding_vector}")
        print(f"Vektör Veri Tipi: {type(embedding_vector)} (Uzunluk: {len(embedding_vector)})\n")

    # Bağlantıyı kapatma
    conn.close()
    print("----------------------------------------------------")
    print("SQLite Sandbox testi başarıyla tamamlandı!")

if __name__ == "__main__":
    main()
