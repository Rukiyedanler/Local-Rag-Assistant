# Local RAG Assistant (Yerel RAG Asistanı)

Bu proje, **Microsoft Foundry Local** ve **RAG (Retrieval-Augmented Generation)** mimarisini kullanarak sıfır internet bağımlılığı ile (tamamen çevrimdışı/offline) çalışan yerel bir Soru-Cevap (Q&A) asistanıdır.

---

## 📅 Yol Haritası & İlerleme

### 🔹 Aşama 1: Temeller
*   [x] **1. Hafta:** RAG Konsepti, Manuel Simülasyon, Geliştirme Ortamı ve Basit LLM Bağlantısı (`main.py`)
*   [x] **2. Hafta:** Temel Teknikler (Embeddings, Vektör Araması, SQLite ve İstem Mühendisliği)

### 🔹 Aşama 2: Proje Uygulaması
*   [x] **3. Hafta:** Veri Alımı ve Geri Getirme Boru Hattı (Data Ingestion & Retrieval Pipeline) (`3-hafta` Dalı)

---

## 📚 3. Hafta - Ingestion & Retrieval Pipeline Raporu (`3-hafta` Dalı)

Bu hafta projenin veri toplama (Ingestion) ve anlamsal geri getirme (Retrieval) boru hatlarını kurduk.

### 1. Bilgi Tabanı Tasarımı & Parçalama (Chunking) (`chunker.py`)
*   **Klasör:** `data/` dizini altına Lumina-X cihazına ait 6 adet kılavuz metin dosyası (`wifi_errors.txt`, `storage_errors.txt` vb.) eklendi.
*   **Parçalama Mantığı:** Metinler anlamsal bütünlüğün bozulmaması için paragraf düzeyinde (`\n\n` ile) bölünmüştür. Toplamda **12 adet metin parçası (chunk)** elde edilmiştir.

### 2. Toplu Veri Alımı ve Depolama (`ingest.py`)
*   **Model:** `qwen3-embedding-0.6b` yerel embedding modeli.
*   **İşlem:** Üretilen 12 parça tek bir hamlede (batch) modele gönderilerek 1024 boyutlu vektörleri hesaplanmıştır.
*   **SQLite Kaydı:** Parçalar, metaverileri (kaynak dosya adı, parça sırası) ve JSON'a serileştirilmiş vektörleri ile birlikte `local_rag.db` veri tabanına toplu olarak (`executemany`) yazılmıştır.
*   **Doğrulama:** Kayıt adedi veri tabanından `COUNT(*)` sorgusu ile kontrol edilerek doğrulanmıştır (12 / 12 kayıt).

### 3. Geri Getirme (Retrieval) Algoritması (`search.py` & `test_search_queries.py`)
*   **Metot:** RAM üzerinde **Kaba Kuvvet (Brute Force)** benzerlik karşılaştırması. Küçük veri setlerinde yüksek performans verir.
*   **Fonksiyon:** `get_top_chunks(query, top_k)` ile kullanıcının sorgusu anlık olarak vektöre çevrilir, veri tabanındaki tüm vektörlerle kosinüs benzerliği hesaplanır ve en yüksek puanlı `top_k` kayıt döndürülür.
*   **Çoklu Senaryo Testi:**
    *   *Sorgu:* "Mavi ışık 102 hatası aldığımda ne yapmalıyım?" -> En yüksek skorla `wifi_errors.txt (Parça 1)` getirildi.
    *   *Sorgu:* "Lumina-X cihazını banyoda kullanabilir miyim?" -> En yüksek skorla `safety_warnings.txt (Parça 0)` getirildi.
    *   *Sorgu:* "Ekranın dokunmatik kalibrasyonunu nasıl yaparım?" -> En yüksek skorla `screen_issues.txt (Parça 1)` getirildi.
