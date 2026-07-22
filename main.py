import json
import math
import os
import sqlite3
import sys
from foundry_local_sdk import FoundryLocalManager, Configuration

# 1. Benzerlik Hesaplama (Kosinüs Benzerliği)
def cosine_similarity(vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

# 2. Geri Getirme (Retrieval) Fonksiyonu
def get_top_chunks(mgr, query: str, top_k: int = 2):
    """Sorguyu vektörleştirir ve SQLite'dan en yakın metinleri getirir."""
    embed_alias = "qwen3-embedding-0.6b"
    
    # Embedding modelini yükleme
    model = mgr.catalog.get_model(embed_alias)
    if not model.is_loaded:
        model.load()
    
    # Sorgu vektörünü alma
    embedding_client = model.get_embedding_client()
    query_res = embedding_client.generate_embeddings([query])
    query_vector = query_res.data[0].embedding
    
    # Model belleğini boşaltma
    model.unload()

    # Veri tabanından dokümanları çekme
    db_name = "local_rag.db"
    if not os.path.exists(db_name):
        print(f"Hata: Veri tabanı bulunamadı ('{db_name}'). Lütfen önce 'ingest.py' betiğini çalıştırın.")
        sys.exit(1)
        
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT content, source, chunk_id, embedding FROM documents;")
    rows = cursor.fetchall()
    conn.close()

    # Benzerlik skorlarını hesaplama
    ranked = []
    for content, source, chunk_id, raw_embedding in rows:
        doc_vector = json.loads(raw_embedding)
        score = cosine_similarity(query_vector, doc_vector)
        ranked.append({
            "score": score,
            "content": content,
            "source": source,
            "chunk_id": chunk_id
        })
        
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]

# 3. İstem ve Cevap Üretim (Generation) Fonksiyonu
def answer_query(mgr, user_question: str) -> str:
    """Kullanıcı sorusuna karşılık en yakın metinleri bulur ve yerel LLM ile cevaplandırır."""
    # 1. Adım: Benzer doküman parçalarını (bağlam) bul
    print("[1/3] Veri tabanında ilgili bağlam aranıyor...")
    top_chunks = get_top_chunks(mgr, user_question, top_k=2)
    
    if not top_chunks:
        return "Soruya yanıt vermek için ilgili belge bulunamadı."

    # Bağlamı ve kaynakları oluşturma
    context_text = "\n\n".join([f"[{c['source']} - Parça {c['chunk_id']}]: {c['content']}" for c in top_chunks])
    
    # 2. Adım: Yerel LLM modelini yükleme
    # 3-5B sınıfındaki başarılı yerel model olan 'phi-3.5-mini' modelini seçiyoruz.
    chat_alias = "phi-3.5-mini"
    print(f"[2/3] Yerel LLM '{chat_alias}' çıkarım için hazırlanıyor...")
    
    chat_model = mgr.catalog.get_model(chat_alias)
    
    if not chat_model.is_cached:
        print(f"-> '{chat_alias}' yerel önbellekte bulunamadı. İndiriliyor (Yaklaşık 2.2 GB)...")
        print("Not: Bu işlem internet hızınıza bağlı olarak birkaç dakika sürebilir...")
        chat_model.download()
        print("Model indirme tamamlandı.")
        
    if not chat_model.is_loaded:
        print("-> Model çıkarım motoruna yükleniyor...")
        chat_model.load()
        
    chat_client = chat_model.get_chat_client()
    chat_client.settings.max_tokens = 256
    chat_client.settings.temperature = 0.3
    chat_client.settings.top_p = 0.9

    # 3. Adım: Katı Sistem İstem Mühendisliği
    system_prompt = """Sen Lumina-X akıllı ev kontrol paneli teknik destek asistanısın. Görevin, kullanıcının sorularını YALNIZCA aşağıdaki BAĞLAM metnine dayanarak Türkçe olarak yanıtlamaktır.

Katı Kurallar:
1. Sadece sana sunulan bağlamdaki bilgilere dayanarak cevap ver. Dış kaynaklı bilgileri veya kendi tahminlerini kesinlikle ekleme.
2. Sorunun cevabı bağlamda açıkça yoksa tam olarak şu yanıtı ver: "Üzgünüm, sağlanan belgelerde bu konu hakkında bilgi bulunmamaktadır."
3. Yanıtının sonuna mutlaka hangi bilgi kaynağını (Örn: [wifi_errors.txt - Parça 1]) kullandığını ekle.
"""

    user_content = f"""BAĞLAM:
{context_text}

KULLANICI SORUSU:
{user_question}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    # 4. Adım: Çıkarım (Inference)
    print("[3/3] Yerel LLM ile cevap sentezleniyor...")
    try:
        response = chat_client.complete_chat(messages)
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Çıkarım hatası: {e}"

    # Belleği boşaltma (Donanım kaynaklarını serbest bırakma)
    chat_model.unload()
    
    return answer

def main():
    print("====================================================")
    print("   Lumina-X Yerel RAG Asistanı - Uçtan Uca Test     ")
    print("====================================================")

    # SDK Konfigürasyonu
    config = Configuration(app_name="LocalRAGAssistant")
    FoundryLocalManager.initialize(config)
    mgr = FoundryLocalManager.instance

    # Uçtan Uca RAG Testi
    test_question = "Mavi ışık 102 hatası aldığımda ne yapmalıyım?"
    print(f"Kullanıcı Sorusu: '{test_question}'\n")
    
    final_answer = answer_query(mgr, test_question)
    
    print("\n================== ASİSTAN YANITI ==================")
    print(final_answer)
    print("====================================================")

if __name__ == "__main__":
    main()
