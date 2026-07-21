import math
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

def main():
    print("====================================================")
    print("  2. Hafta - Adım 1: Metin Yerleştirmeleri (Embeddings) ")
    print("====================================================")

    # 1. SDK Konfigürasyonu ve Başlatma
    config = Configuration(app_name="LocalRAGAssistant")
    FoundryLocalManager.initialize(config)
    mgr = FoundryLocalManager.instance

    # 2. Embedding Modelini Seçme
    model_alias = "qwen3-embedding-0.6b"
    print(f"[1/4] Embedding modeli ('{model_alias}') hazırlanıyor...")
    
    try:
        model = mgr.catalog.get_model(model_alias)
    except Exception as e:
        print(f"Hata: Model kataloğunda '{model_alias}' bulunamadı: {e}")
        sys.exit(1)

    # 3. Model İndirme ve Belleğe Yükleme
    if not model.is_cached:
        print(f"[2/4] '{model_alias}' indiriliyor (Yaklaşık 400 MB)...")
        model.download()
        print("İndirme tamamlandı!")
    else:
        print(f"[2/4] '{model_alias}' yerel önbellekte hazır.")

    if not model.is_loaded:
        print("[3/4] Embedding modeli belleğe yükleniyor...")
        model.load()
    
    embedding_client = model.get_embedding_client()

    # 4. Örnek Bilgi Tabanı Cümleleri ve Arama Sorgusu
    documents = [
        "Lumina-X kontrol panelinde mavi ışık 102 hatası için Reset butonuna 5 saniye basılı tutun.",
        "Kırmızı ışık 404 hatası aldığınızda MicroSD kartı çıkarıp tekrar takın.",
        "Güvenlik uyarısı: Cihazı kesinlikle nemli ortamlarda kullanmayın.",
        "Yemek yaparken zeytinyağı kullanmak yemeğin lezzetini ve besin değerini artırır."
    ]

    query = "Mavi ışık hatasında sıfırlama işlemi nasıl yapılır?"

    print(f"\n[4/4] Vektörler üretiliyor ve benzerlik hesaplanıyor...")
    print(f"\nArama Sorgusu: '{query}'\n")

    # 5. Vektörleri Üretme (Embeddings Generation)
    # Sorgunun ve belgelerin sayısal vektör karşılıklarını alıyoruz
    query_res = embedding_client.generate_embeddings([query])
    query_vector = query_res.data[0].embedding

    doc_res = embedding_client.generate_embeddings(documents)
    doc_vectors = [item.embedding for item in doc_res.data]

    print(f"-> Vektör Boyutu (Dimension): {len(query_vector)} elemanlı sayısal dizi.\n")

    # 6. Kosinüs Benzerliği Hesaplama Döngüsü
    results = []
    for idx, (doc, doc_vec) in enumerate(zip(documents, doc_vectors)):
        score = cosine_similarity(query_vector, doc_vec)
        results.append((score, doc))
        print(f"Doküman [{idx+1}] Skoru: {score:.4f} | Metin: '{doc}'")

    # En yüksek skora sahip dokümanı bulma
    results.sort(key=lambda x: x[0], reverse=True)
    best_score, best_doc = results[0]

    print("\n----------------------------------------------------")
    print(f"[+] En Alakalı Doküman (En Yüksek Skora Sahip):")
    print(f"Skor: {best_score:.4f}")
    print(f"İlgili Metin: '{best_doc}'")
    print("----------------------------------------------------")

    # Belleği temizleme
    model.unload()
    print("\nTest tamamlandı. Bellek temizlendi.")

if __name__ == "__main__":
    main()
