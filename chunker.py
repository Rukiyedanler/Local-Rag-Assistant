import os

def chunk_text_by_paragraphs(file_path):
    """Metin dosyasını okur ve çift satır sonlarına (\n\n) göre paragraflara (parçalara) böler."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Paragraflara ayır
    raw_paragraphs = content.split('\n\n')
    
    chunks = []
    for index, paragraph in enumerate(raw_paragraphs):
        cleaned = paragraph.strip()
        if cleaned:  # Boş paragrafları atla
            chunks.append({
                "chunk_id": index,
                "text": cleaned,
                "source": os.path.basename(file_path)
            })
    return chunks

def main():
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Hata: '{data_dir}' dizini bulunamadı.")
        return
        
    print("====================================================")
    print(" 3. Hafta - Adım 1: Bilgi Hazırlığı ve Parçalama (Chunking)")
    print("====================================================")
    
    # Veri klasöründeki tüm .txt dosyalarını oku
    files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    print(f"Belge Klasörü: '{data_dir}/' - Tespit edilen dosya sayısı: {len(files)}\n")
    
    all_chunks = []
    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        file_chunks = chunk_text_by_paragraphs(file_path)
        all_chunks.extend(file_chunks)
        print(f"-> '{file_name}' dosyasından {len(file_chunks)} adet parça üretildi.")
        
    print(f"\nTüm bilgi tabanından toplam üretilen parça (chunk) sayısı: {len(all_chunks)}")
    print("\n--- İlk 3 Parça (Chunk) Gösterimi ve Metaverileri ---")
    
    for i, chunk in enumerate(all_chunks[:3]):
        print(f"\n[Parça #{i+1}] | Kaynak: {chunk['source']} | ID: {chunk['chunk_id']}")
        print(f"İçerik:\n{chunk['text']}")
        print("-" * 50)

if __name__ == "__main__":
    main()
