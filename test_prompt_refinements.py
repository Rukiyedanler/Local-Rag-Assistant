import json
import os
import sys
from foundry_local_sdk import FoundryLocalManager, Configuration
from main import answer_query

def main():
    print("====================================================")
    print(" 4. Hafta - Adım 3: Halüsinasyon ve İstem Testi     ")
    print("====================================================")

    config = Configuration(app_name="LocalRAGAssistant")
    FoundryLocalManager.initialize(config)
    mgr = FoundryLocalManager.instance

    # Test 1: Belgede bulunmayan bir soru (Halüsinasyon Testi)
    question_out_of_bounds = "Lumina-X ile internetten nasıl pizza sipariş edebilirim?"
    print(f"\n[Test 1] Bağlam Dışı Soru: '{question_out_of_bounds}'")
    answer_1 = answer_query(mgr, question_out_of_bounds)
    print(f"Yanıt: {answer_1}")

    # Test 2: Belgede bulunan bir soru (Başarı Testi)
    question_in_bounds = "Cihaz donduğunda ne yapmalıyım?"
    print(f"\n[Test 2] Bağlam İçi Soru: '{question_in_bounds}'")
    answer_2 = answer_query(mgr, question_in_bounds)
    print(f"Yanıt: {answer_2}")

    print("\n====================================================")
    print("[+] Prompt ve son işlem testleri başarıyla tamamlandı!")
    print("====================================================")

if __name__ == "__main__":
    main()
