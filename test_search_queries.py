import json
import math
import sqlite3
import sys
from foundry_local_sdk import FoundryLocalManager, Configuration

def cosine_similarity(vec_a, vec_b):
    """İki vektör arasındaki Kosinüs Benzerliğini (Cosine Similarity) hesaplar."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def get_top_chunks(query: str, top_k: int = 2):
    """Kullanıcının sorusuna en yakın top_k adet doküman parçasını veri tabanından getirir (Kaba Kuvvet Arama)."""
    # 1. SDK ve Model Hazırlığı (Güvenli Singleton İlklendirme Deseni)
    mgr = FoundryLocalManager.instance
    if mgr is None:
        config = Configuration(app_name="LocalRAGAssistant")
        FoundryLocalManager.initialize(config)
        mgr = FoundryLocalManager.instance

    model_alias = "qwen3-embedding-0.6b"
    try:
        model = mgr.catalog.get_model(model_alias)
    except Exception as e:
        print(f"Hata: Model bulunamadı: {e}")
        return []

    # Model zaten ingest.py ile önbelleğe alınmıştı, doğrudan yüklüyoruz
    if not model.is_loaded:
        model.load()

    embedding_client = model.get_embedding_client()

    # 2. Arama Sorgusunu Vektörleştirme (Embedding)
    query_res = embedding_client.generate_embeddings([query])
    query_vector = query_res.data[0].embedding

    # 3. Veri Tabanındaki Tüm Dokümanları ve Vektörlerini Çekme (Kaba Kuvvet - Brute Force Yöntemi)
    db_name = "local_rag.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT content, source, chunk_id, embedding FROM documents;")
    rows = cursor.fetchall()
    conn.close()

    # 4. Benzerlik Skorlarını Hesaplama ve Sıralama
    ranked_chunks = []
    for content, source, chunk_id, raw_embedding in rows:
        doc_vector = json.loads(raw_embedding)
        score = cosine_similarity(query_vector, doc_vector)
        ranked_chunks.append({
            "score": score,
            "content": content,
            "source": source,
            "chunk_id": chunk_id
        })

    # Skorlara göre büyükten küçüğe sıralama
    ranked_chunks.sort(key=lambda x: x["score"], reverse=True)

    # Belleği temizleme
    model.unload()

    # En yüksek skora sahip top_k adet parçayı döndürür
    return ranked_chunks[:top_k]

def run_test_query(query_text):
    print(f"\nSorgu: '{query_text}'")
    results = get_top_chunks(query_text, top_k=2)
    print("--- En Alakalı Parçalar (Top 2) ---")
    for idx, chunk in enumerate(results):
        print(f"[{idx+1}] Skor: {chunk['score']:.4f} | Kaynak: {chunk['source']} (Parça: {chunk['chunk_id']})")
        print(f"İçerik: {chunk['content']}")
    print("-" * 60)

def main():
    print("====================================================")
    print(" 3. Hafta - Adım 3: Geri Getirme (Retrieval) Çoklu Test")
    print("====================================================")

    # Belgelerimizde cevabı olduğunu bildiğimiz 4 adet farklı test sorusu
    queries = [
        "Mavi ışık 102 hatası aldığımda ne yapmalıyım?",
        "Kırmızı ışık 404 hatasının çözümü nedir?",
        "Lumina-X cihazını banyoda kullanabilir miyim?",
        "Ekranın dokunmatik kalibrasyonunu nasıl yaparım?"
    ]

    for q in queries:
        run_test_query(q)

if __name__ == "__main__":
    main()
