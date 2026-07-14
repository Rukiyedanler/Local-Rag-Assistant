import sys
from foundry_local_sdk import FoundryLocalManager, Configuration

def main():
    print("====================================================")
    print("   Local RAG Assistant - Yerel LLM Bağlantı Testi  ")
    print("====================================================")

    # 1. Konfigürasyon Ayarları
    # Foundry Local motorunu başlatmak için benzersiz bir uygulama adı veriyoruz.
    # Bu ad, model önbelleklerinin ve yerel verilerin saklanacağı dizini belirler.
    config = Configuration(app_name="LocalRAGAssistant")
    
    print("[1/5] Foundry Local SDK'sı başlatılıyor...")
    FoundryLocalManager.initialize(config)
    mgr = FoundryLocalManager.instance

    # 2. Modeli Seçme
    # 1. Hafta hedeflerimiz için en küçük ve hızlı model olan 'qwen2.5-0.5b' modelini seçiyoruz.
    model_alias = "qwen2.5-0.5b"
    print(f"[2/5] Model kataloğundan '{model_alias}' aranıyor...")
    
    try:
        model = mgr.catalog.get_model(model_alias)
    except Exception as e:
        print(f"Hata: Model bulunamadı veya yüklenemedi: {e}")
        sys.exit(1)

    # 3. Model İndirme Kontrolü
    # Eğer model yerel olarak önbelleğe alınmamışsa, otomatik olarak indirilir.
    # İndirme işlemi bir kereliktir; sonraki tüm çıkarımlar tamamen çevrimdışı (offline) çalışır.
    if not model.is_cached:
        print(f"[3/5] '{model_alias}' modeli yerel diskte bulunamadı. İndiriliyor...")
        print("Not: Bu işlem internet hızınıza bağlı olarak birkaç dakika sürebilir (Yaklaşık 350 MB)...")
        model.download()
        print("İndirme tamamlandı!")
    else:
        print(f"[3/5] '{model_alias}' modeli yerel önbellekte hazır.")

    # 4. Modeli Belleğe Yükleme
    if not model.is_loaded:
        print("[4/5] Model çıkarım motoruna (ONNX Runtime) yükleniyor...")
        model.load()
        print("Model başarıyla yüklendi.")
    else:
        print("[4/5] Model zaten yüklü durumda.")

    # 5. Çıkarım (Inference) Yapma
    print("[5/5] Yerel model ile ilk test çıkarımı yapılıyor...")
    chat_client = model.get_chat_client()
    
    messages = [
        {"role": "user", "content": "Hello, world!"}
    ]
    
    print("\nİstem (Prompt): 'Hello, world!'")
    print("Modelden yanıt bekleniyor...\n")
    
    try:
        response = chat_client.complete_chat(messages)
        # OpenAI uyumlu yapı: response.choices[0].message.content
        content = response.choices[0].message.content
        print("--- Model Yanıtı ---")
        print(content)
        print("--------------------")
    except Exception as e:
        print(f"Çıkarım sırasında hata oluştu: {e}")
        
    # Modeli bellekten boşaltma (Kıdemli mühendis en iyi uygulaması)
    print("\nBellek temizleniyor...")
    model.unload()
    print("Test tamamlandı!")

if __name__ == "__main__":
    main()
