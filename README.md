# Local RAG Assistant (Yerel RAG Asistanı)

Microsoft **Foundry Local** ve **RAG** (Retrieval-Augmented Generation) mimarisi kullanılarak sıfır internet bağımlılığıyla çalışan, tamamen çevrimdışı (offline) bir yerel Soru-Cevap (Q&A) asistanıdır.

---

## 📅 Proje İlerlemesi

*   **1. Hafta (Kurulum ve LLM):** Geliştirme ortamı kurulumu, `requirements.txt` ve yerel LLM (`qwen2.5-0.5b`) bağlantı testi (`main.py`).
*   **2. Hafta (Temel Teknikler):** Metin yerleştirmeleri (embeddings), kosinüs benzerliği hesabı, SQLite depolama ve istem mühendisliği (prompt engineering) sandbox denemeleri.
*   **3. Hafta (Veri Boru Hattı):** Bilgi tabanı dokümanlarının paragraflara bölünmesi (chunking), toplu vektörleştirilerek SQLite veri tabanına kaydedilmesi (`ingest.py`) ve anlamsal geri getirme fonksiyonunun (`get_top_chunks`) yazılması (`search.py`).

---

## 🚀 Nasıl Çalıştırılır?

1.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Verileri İçeri Aktarın (Ingestion):**
    `data/` klasöründeki dokümanları parçalayıp vektörleştirerek veri tabanına kaydetmek için:
    ```bash
    python ingest.py
    ```
3.  **Arama Yapın (Retrieval):**
    Anlamsal arama motorunu test etmek için:
    ```bash
    python test_search_queries.py
    ```
