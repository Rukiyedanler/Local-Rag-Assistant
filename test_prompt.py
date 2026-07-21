import sys
from foundry_local_sdk import FoundryLocalManager, Configuration

# Güçlü ve Katı Sistem İstemi (System Prompt) Şablonu
SYSTEM_PROMPT = """Sen Lumina-X teknik destek asistanısın. Görevin kullanıcının sorularını YALNIZCA sana sağlanan Bağlam (Context) bilgilerine dayanarak yanıtlamaktır.

Aşağıdaki katı kurallara KESİNLİKLE uymalısın:
1. Yalnızca sağlanan bağlamdaki bilgileri kullan. Kendi genel bilginle veya uydurma tahminlerle asla cevap verme.
2. Eğer sorulan sorunun cevabı verilen bağlamda GEÇMİYORSA, tam olarak şu cümleyi söyle: "Üzgünüm, sağlanan belgelerde bu konu hakkında bilgi bulunmamaktadır."
3. Verdiğin yanıtın sonuna bilgi kaynağını gösteren etiket ekle (Örn: [Kaynak: Dosya_Adı]).
"""

def generate_rag_response(chat_client, context: str, user_question: str) -> str:
    """Sistem ve Kullanıcı istemlerini birleştirerek LLM çıkarımı yapar."""
    user_content = f"""BAĞLAM:
{context}

KULLANICI SORUSU:
{user_question}"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    response = chat_client.complete_chat(messages)
    return response.choices[0].message.content

def main():
    print("====================================================")
    print(" 2. Hafta - Adım 3: İstem Mühendisliği (Prompt Test) ")
    print("====================================================")

    # 1. SDK ve Model Hazırlığı
    config = Configuration(app_name="LocalRAGAssistant")
    FoundryLocalManager.initialize(config)
    mgr = FoundryLocalManager.instance

    model_alias = "qwen2.5-0.5b"
    print(f"[1/3] Yerel model ('{model_alias}') hazırlanıyor...")
    
    try:
        model = mgr.catalog.get_model(model_alias)
    except Exception as e:
        print(f"Hata: Model bulunamadı: {e}")
        sys.exit(1)

    if not model.is_cached:
        print(f"[2/3] '{model_alias}' yerel diskte bulunamadı. İndiriliyor...")
        model.download()

    if not model.is_loaded:
        print("[2/3] Model belleğe yükleniyor...")
        model.load()
    
    chat_client = model.get_chat_client()
    print("[3/3] Çıkarım testleri başlatılıyor...\n")

    # 2. Test İçin Örnek Bağlam (Mock Context)
    mock_context = """[Kaynak: LuminaX_Kılavuz_v2.txt]
Lumina-X cihazında Mavi ışık 102 hatası oluştuğunda Wi-Fi bağlantısı kopmuştur. Çözüm için cihazın arkasındaki Reset düğmesine bir ataş yardımıyla 5 saniye basılı tutun. Cihaz kendini yeniden başlatacaktır.
"""

    # TEST 1: Bağlamda Cevabı Olan Soru
    print("--- TEST 1: Bağlamda Var Olan Soru ---")
    q1 = "Mavi ışık 102 hatası aldığımda ne yapmalıyım?"
    print(f"Soru: '{q1}'")
    a1 = generate_rag_response(chat_client, mock_context, q1)
    print(f"\nModel Yanıtı:\n{a1}")
    print("----------------------------------------------------\n")

    # TEST 2: Bağlamda Cevabı Olmayan Soru (Halüsinasyon Engelleme Testi)
    print("--- TEST 2: Bağlamda Olmayan Soru (Halüsinasyon Testi) ---")
    q2 = "Lumina-X cihazının pil değişimi garanti kapsamına girer mi?"
    print(f"Soru: '{q2}'")
    a2 = generate_rag_response(chat_client, mock_context, q2)
    print(f"\nModel Yanıtı:\n{a2}")
    print("----------------------------------------------------")

    # Belleği temizleme
    model.unload()
    print("\nTest tamamlandı. Bellek temizlendi.")

if __name__ == "__main__":
    main()
