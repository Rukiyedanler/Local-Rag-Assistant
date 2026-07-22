import json
import math
import os
import sqlite3
import streamlit as st
from foundry_local_sdk import FoundryLocalManager, Configuration
from main import answer_query, get_top_chunks

# 1. Sayfa Yapılandırması ve Premium Tema Özelleştirmeleri
st.set_page_config(
    page_title="Lumina-X Yerel RAG Asistanı",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Koyu Arka Plan Teması */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Yan Menü (Sidebar) Arka Planı */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Başlık ve Metin Renkleri */
    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 700;
    }
    
    /* Doküman Kart Tasarımı */
    .doc-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    
    .doc-card:hover {
        border-color: rgba(6, 182, 212, 0.4);
        background: rgba(30, 41, 59, 0.8);
    }
    
    /* Kaynak Gösterim Badge'i */
    .citation-badge {
        background: rgba(6, 182, 212, 0.1);
        border: 1px dashed rgba(6, 182, 212, 0.3);
        color: #06b6d4;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 2. SDK ve Manager İlklendirme (Session State korumalı Cache)
@st.cache_resource
def get_foundry_manager():
    config = Configuration(app_name="LocalRAGAssistant")
    FoundryLocalManager.initialize(config)
    return FoundryLocalManager.instance

try:
    mgr = get_foundry_manager()
except Exception:
    mgr = FoundryLocalManager.instance

# Sohbet Geçmişi Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: SQLite Veri Tabanındaki Dokümanların Listesi
with st.sidebar:
    st.markdown("### ⚡ Lumina-X Yerel RAG")
    st.markdown("<small style='color:#94a3b8;'>Çevrimdışı Soru-Cevap Asistanı</small>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("#### 📂 SQLite Bilgi Tabanı Belgeleri")
    
    docs = [
        ("wifi_errors.txt", "Wi-Fi Hataları & Reset Çözümü"),
        ("storage_errors.txt", "SD Kart ve Depolama Hataları"),
        ("safety_warnings.txt", "Çevre & Elektrik Güvenliği"),
        ("screen_issues.txt", "Ekran Hassasiyeti & Titreme"),
        ("smart_home_integration.txt", "HA & Alexa Entegrasyonu"),
        ("power_reset.txt", "Cihaz Sıfırlama Menüsü")
    ]
    
    for filename, desc in docs:
        st.markdown(f"""
        <div class="doc-card">
            <strong>📄 {filename}</strong><br>
            <span style="font-size: 11px; color: #94a3b8;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

# Ana Panel
st.title("⚡ Lumina-X Teknik Destek Asistanı")
st.write("Cihazınız ile ilgili soruları girin. Yerel LLM (Phi-3.5) sadece bilgi tabanını kullanarak yanıtlayacaktır.")

# Sohbet Geçmişini Görüntüleme
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "source" in msg and msg["source"]:
            st.markdown(f'<span class="citation-badge">Kaynak: {msg["source"]}</span>', unsafe_allow_html=True)

# Kullanıcıdan Soru Alma ve RAG Süreci
if user_question := st.chat_input("Lumina-X ile ilgili bir soru sorun..."):
    # Kullanıcı mesajını çizdir ve kaydet
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})
    
    # Asistan Yanıtı
    with st.chat_message("assistant"):
        with st.spinner("SQLite veri tabanından en yakın bağlam çekiliyor ve yanıt sentezleniyor..."):
            # 1. Adım: Benzerlik araması ile metaveri dosyasını bul
            top_chunks = get_top_chunks(mgr, user_question, top_k=1)
            source_file = "Genel Kılavuz"
            if top_chunks:
                source_file = f"{top_chunks[0]['source']} (Parça {top_chunks[0]['chunk_id']})"
                
            # 2. Adım: RAG Çıkarımı
            answer = answer_query(mgr, user_question)
            
            # Ekran Çıktıları
            st.write(answer)
            st.markdown(f'<span class="citation-badge">Kaynak: {source_file}</span>', unsafe_allow_html=True)
            
            # Sohbet geçmişine kaydet
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "source": source_file
            })
