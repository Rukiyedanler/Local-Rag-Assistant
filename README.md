# Local RAG Assistant (Yerel RAG Asistanı)

Bu proje, **Microsoft Foundry Local** ve **RAG (Retrieval-Augmented Generation)** mimarisini kullanarak sıfır internet bağımlılığı ile (tamamen çevrimdışı/offline) çalışan yerel bir Soru-Cevap (Q&A) asistanıdır.

---

## 📅 Yol Haritası & İlerleme

### 🔹 Aşama 1: Temeller
*   [x] **1. Hafta:** RAG Konsepti, Manuel Simülasyon, Geliştirme Ortamı ve Basit LLM Bağlantısı (`main.py`)
*   [x] **2. Hafta:** Temel Teknikler (Embeddings, Vektör Araması, SQLite ve İstem Mühendisliği)

---

## 📚 2. Hafta - Sandbox Test Raporları (`hafta-2` Dalı)

### 1. Metin Yerleştirmeleri & Kosinüs Benzerliği (`test_embeddings.py`)
*   **Model:** `qwen3-embedding-0.6b` (1024 boyutlu vektörler üretir)
*   **Amaç:** Metinleri sayısal vektör uzayına taşıyarak anlamsal benzerliği (semantic similarity) hesaplamak.
*   **Test Sonucu:** *"sıfırlama"* kelimesini içeren arama sorgusu, birebir kelime eşleşmesi olmamasına rağmen *"Reset"* geçen ilgili doküman ile **0.5268** oranında en yüksek benzerlik skorunu almıştır.

### 2. SQLite ile Yerel Depolama (`test_sqlite.py`)
*   **Veri Tabanı:** `local_rag_sandbox.db` (Sunucusuz, tek dosyalı yerel SQLite)
*   **Amaç:** Üretilen embedding vektörlerini JSON olarak SQLite tablosunda saklamak ve sorgulamak.
*   **Test Sonucu:** Tabloya metin ve vektör çiftleri kaydedilmiş, `SELECT` sorgusu ile başarıyla geriye dönüştürülmüştür.

### 3. Soru-Cevap İçin İstem Mühendisliği (`test_prompt.py`)
*   **Sistem İstemi (System Prompt):** Modele *"Yalnızca verilen bağlama dayanarak cevap ver, bilmiyorsan belirt ve kaynak göster"* kuralları tanımlanmıştır.
*   **Halüsinasyon Engelleme Testi:**
    *   **Bağlamda Olan Soru:** Doğru cevap verilmiş ve `[Kaynak: LuminaX_Kılavuz_v2.txt]` bilgisi eklenmiştir.
    *   **Bağlamda Olmayan Soru:** Model uydurma yapmayıp *"Üzgünüm, sağlanan belgelerde bu konu hakkında bilgi bulunmamaktadır."* demiştir.
