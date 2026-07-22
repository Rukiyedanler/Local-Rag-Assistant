import json
import os
import sqlite3
import sys
from foundry_local_sdk import FoundryLocalManager, Configuration
from chunker import chunk_text_by_paragraphs

def main():
    print("====================================================")
    print(" 3. Hafta - Adım 2: Veri Alımı (Ingestion) Boru Hattı")
    print("====================================================")

    # 1. Adım 1'deki Belgeleri Parçalama (Chunking)
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Hata: '{data_dir}' dizini bulunamadı. Lütfen önce belgeleri hazırlayın.")
        sys.exit(1)

    print("[1/5] 'data/' dizinindeki belgeler okunuyor ve parçalanıyor...")
    files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    all_chunks = []
    
    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        chunks = chunk_text_by_paragraphs(file_path)
        all_chunks.extend(chunks)
        
    print(f"-> Toplam {len(all_chunks)} adet metin parçası (chunk) oluşturuldu.")

    # 2. SDK ve Embedding Modeli Başlatma
    config = Configuration(app_name="LocalRAGAssistant")
    FoundryLocalManager.initialize(config)
    mgr = FoundryLocalManager.instance

    model_alias = "qwen3-embedding-0.6b"
    print(f"[2/5] Yerel embedding modeli '{model_alias}' yükleniyor...")
    
    try:
        model = mgr.catalog.get_model(model_alias)
    except Exception as e:
        print(f"Hata: Model bulunamadı: {e}")
        sys.exit(1)

    if not model.is_cached:
        print(f"-> '{model_alias}' modeli indiriliyor (bir kerelik)...")
        model.download()

    if not model.is_loaded:
        model.load()

    embedding_client = model.get_embedding_client()

    # 3. Metin Parçalarını Toplu Olarak Vektörleştirme (Batch Embedding)
    print("[3/5] Tüm parçalar toplu olarak vektörleştiriliyor (Embedding)...")
    chunk_texts = [chunk["text"] for chunk in all_chunks]
    
    try:
        res = embedding_client.generate_embeddings(chunk_texts)
        # Her parça için üretilen vektörleri alıyoruz
        for idx, item in enumerate(res.data):
            all_chunks[idx]["embedding"] = item.embedding
        print("-> Vektörleştirme işlemi başarıyla tamamlandı.")
    except Exception as e:
        print(f"Vektörleştirme sırasında hata oluştu: {e}")
        model.unload()
        sys.exit(1)

    # 4. SQLite Veri Tabanına Kayıt
    db_name = "local_rag.db"
    print(f"[4/5] Vektörler '{db_name}' SQLite veri tabanına yazılıyor...")
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # documents tablosunu kurguluyoruz
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        source TEXT NOT NULL,
        chunk_id INTEGER NOT NULL,
        embedding TEXT NOT NULL
    );
    """)

    # Sandbox izolasyonu: Önceki verileri silelim
    cursor.execute("DELETE FROM documents;")

    # Kayıt verilerini hazırlama (Vektörü JSON string olarak serileştiriyoruz)
    insert_data = [
        (
            chunk["text"],
            chunk["source"],
            chunk["chunk_id"],
            json.dumps(chunk["embedding"])  # SQLite içinde vektörü JSON metni olarak saklama
        )
        for chunk in all_chunks
    ]

    cursor.executemany(
        "INSERT INTO documents (content, source, chunk_id, embedding) VALUES (?, ?, ?, ?);",
        insert_data
    )
    conn.commit()
    conn.close()
    
    print(f"-> {len(insert_data)} adet kayıt veri tabanına başarıyla yazıldı.")

    # 5. Doğrulama / Test Aşaması
    print("\n[5/5] SQLite Veri Tabanı Kayıt Doğrulaması...")
    verify_conn = sqlite3.connect(db_name)
    verify_cursor = verify_conn.cursor()
    verify_cursor.execute("SELECT COUNT(*) FROM documents;")
    count = verify_cursor.fetchone()[0]
    verify_conn.close()

    print("----------------------------------------------------")
    print(f"[+] Doğrulama Başarılı! Veri tabanındaki kayıt sayısı: {count} / {len(all_chunks)}")
    print("----------------------------------------------------")

    # Belleği temizleme
    model.unload()
    print("Veri alımı (Ingestion) tamamlandı. Bellek temizlendi.")

if __name__ == "__main__":
    main()
