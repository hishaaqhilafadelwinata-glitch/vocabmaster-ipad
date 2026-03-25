import streamlit as st
import requests
import random
import re
import time
from deep_translator import GoogleTranslator

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="VocabMaster", layout="centered")

# CSS Kustom: Premium Dark Mode & Modern Font
st.markdown("""
<style>
    /* Mengambil Font Modern dari Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500&display=swap');

    /* Terapkan font ke seluruh aplikasi */
    html, body, [class*="css"], .stMarkdown p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* === MENGHILANGKAN WARNA UNGU/MERAH BAWAAN STREAMLIT === */
    /* Ini yang bikin kotak teks dan tombol jadi aneh saat diklik */
    *:focus {
        outline: none !important;
    }
    div[data-baseweb="input"]:focus-within, 
    div[data-baseweb="textarea"]:focus-within {
        border-color: #14B8A6 !important; /* Warna Teal Modern */
        box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.2) !important;
    }

    /* === KOTAK INPUT TEKS === */
    .stTextArea > div {
        border-radius: 16px !important;
        background-color: transparent !important;
    }
    .stTextArea textarea {
        border-radius: 16px !important; 
        border: 1px solid #333333 !important; /* Abu-abu gelap */
        background-color: #121212 !important; /* Hitam */
        color: #FFFFFF !important;
        font-size: 15px;
        padding: 16px;
        transition: all 0.2s ease;
    }
    /* Warna saat kotak teks sedang diketik */
    .stTextArea textarea:focus {
        border-color: #14B8A6 !important;
        box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.2) !important;
    }

    /* Label Input Teks */
    .stTextArea label {
        font-weight: 600 !important;
        color: #A3A3A3 !important; /* Abu-abu terang agar terbaca di dark mode */
        font-size: 16px !important;
        margin-bottom: 8px !important;
    }

    /* === TOMBOL === */
    /* Tombol Utama (Primary) - Warna Teal */
    .stButton>button[kind="primary"] {
        background-color: #14B8A6 !important;
        color: #000000 !important; /* Teks hitam agar kontras dengan background Teal */
        border: none !important;
        border-radius: 14px !important;
        height: 52px;
        font-weight: 700 !important;
        font-size: 16px;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.15) !important;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #0D9488 !important; /* Teal lebih gelap saat di-hover */
        transform: translateY(-2px);
    }

    /* Tombol Sekunder (Secondary) - Warna Hitam/Abu-abu */
    .stButton>button[kind="secondary"] {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 14px !important;
        height: 52px;
        font-weight: 600 !important;
        font-size: 16px;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="secondary"]:hover {
        border-color: #14B8A6 !important;
        color: #14B8A6 !important;
    }

    /* Fokus pada tombol agar tidak jadi pink/ungu */
    .stButton>button:focus {
        box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.4) !important;
        border-color: #14B8A6 !important;
        color: #14B8A6 !important;
    }

    /* === KARTU FLASHCARD HITAM === */
    .vocab-card {
        padding: 40px 25px;
        border-radius: 24px; 
        text-align: center;
        margin: 25px 0;
        min-height: 290px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* Kartu Depan (Hitam Pekat) */
    .card-front {
        background-color: #121212;
        border: 1px solid #2A2A2A;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5); 
    }
    .word-title { 
        font-size: 42px; 
        font-weight: 800; 
        margin-bottom: 8px; 
        text-transform: capitalize; 
        letter-spacing: -1px;
        color: #FFFFFF;
    }
    .word-phonetic { 
        font-size: 17px; 
        color: #14B8A6; /* Aksen Teal di tulisan fonetik */
        font-weight: 500;
        letter-spacing: 1px;
    }

    /* Kartu Belakang (Hitam dengan Garis Teal) */
    .card-back {
        background-color: #0A0A0A; /* Hitam yang sedikit berbeda */
        border: 1px solid #14B8A6; /* Garis aksen Teal */
        box-shadow: 0 8px 32px rgba(20, 184, 166, 0.08);
    }
    .word-label { 
        font-size: 12px; 
        color: #737373; 
        font-weight: 700;
        letter-spacing: 2px; 
        margin-bottom: 25px; 
        text-transform: uppercase;
    }
    .word-meaning { 
        font-size: 22px; 
        font-weight: 600; 
        margin-bottom: 20px; 
        line-height: 1.5;
        color: #FFFFFF;
    }
    .word-example { 
        font-size: 15px; 
        font-style: italic; 
        color: #A3A3A3; 
        max-width: 90%;
        line-height: 1.5;
    }

    /* === LAIN-LAIN === */
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #14B8A6 !important;
        border-radius: 10px;
    }
    /* Peringatan & Status */
    .stAlert {
        border-radius: 12px;
        background-color: #1A1A1A !important;
        border: 1px solid #333333 !important;
        color: #FFFFFF !important;
    }
    /* Memastikan teks biasa terlihat cerah di dark mode */
    h1 { font-weight: 800; letter-spacing: -1.5px; color: #FFFFFF; }
    h2, h3 { font-weight: 700; color: #FFFFFF; }
    p { color: #D4D4D4; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# INISIALISASI STATE
# ==========================================
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'input'
if 'words_data' not in st.session_state:
    st.session_state.words_data = []
if 'card_idx' not in st.session_state:
    st.session_state.card_idx = 0
if 'is_flipped' not in st.session_state:
    st.session_state.is_flipped = False
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_idx' not in st.session_state:
    st.session_state.quiz_idx = 0

# ==========================================
# FUNGSI PEMBANTU
# ==========================================
def extract_words(text):
    words = [w.lower() for w in re.findall(r"[a-zA-Z]{4,}", text)]
    return list(dict.fromkeys(words))

def fetch_definition(word):
    result = {"word": word, "pronunciation": "", "definition_id": "(Definisi tidak ditemukan)", "example": ""}
    try:
        resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()[0]
            for ph in data.get("phonetics", []):
                if ph.get("text"):
                    result["pronunciation"] = ph["text"]
                    break
            meanings = data.get("meanings", [])
            if meanings and meanings[0].get("definitions"):
                d = meanings[0]["definitions"][0]
                def_en = d.get("definition", "")
                result["example"] = d.get("example", "")
                
                # Terjemahkan ke Bahasa Indonesia
                if def_en:
                    try:
                        result["definition_id"] = GoogleTranslator(source='en', target='id').translate(def_en)
                    except Exception:
                        result["definition_id"] = def_en
    except Exception:
        pass
    return result

def change_state(new_state):
    st.session_state.app_state = new_state
    if new_state == 'study':
        st.session_state.is_flipped = False

# ==========================================
# LAYAR 1: INPUT TEKS
# ==========================================
if st.session_state.app_state == 'input':
    st.title("VocabMaster")
    st.write("Ubah teks bahasa Inggris menjadi kartu belajar modern.")
    st.write("")
    
    text_input = st.text_area("Masukkan Teks Bahasa Inggris", height=200, 
                              placeholder="Ketik atau tempel paragraf, kalimat, atau daftar kata di sini...")
    
    st.write("")

    if st.button("Buat Kartu Belajar", type="primary"):
        if not text_input.strip():
            st.warning("Silakan masukkan teks terlebih dahulu.")
        else:
            words = extract_words(text_input)
            if not words:
                st.error("Tidak ada kata bahasa Inggris yang valid ditemukan (minimal 4 huruf).")
            else:
                with st.spinner(f"Menerjemahkan {len(words)} kosakata..."):
                    word_data_list = []
                    for w in words:
                        word_data_list.append(fetch_definition(w))
                        time.sleep(0.05)
                    
                    st.session_state.words_data = word_data_list
                    st.session_state.card_idx = 0
                    st.session_state.is_flipped = False
                    change_state('study')
                    st.rerun()

# ==========================================
# LAYAR 2: BELAJAR (FLASHCARD)
# ==========================================
elif st.session_state.app_state == 'study':
    st.button("Kembali ke Beranda", type="secondary", on_click=change_state, args=('input',))
    
    words = st.session_state.words_data
    current_idx = st.session_state.card_idx
    current_word = words[current_idx]
    
    st.write("")
    st.progress((current_idx + 1) / len(words))
    st.write("") 
    st.caption(f"Kartu {current_idx + 1} dari {len(words)}")
    
    if not st.session_state.is_flipped:
        st.markdown(f"""
        <div class="vocab-card card-front">
            <div class="word-title">{current_word['word']}</div>
            <div class="word-phonetic">{current_word['pronunciation']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        example_text = f'"{current_word["example"]}"' if current_word["example"] else ""
        st.markdown(f"""
        <div class="vocab-card card-back">
            <div class="word-label">ARTI KATA</div>
            <div class="word-meaning">{current_word['definition_id']}</div>
            <div class="word-example">{example_text}</div>
        </div>
        """, unsafe_allow_html=True)

    col_back, col_flip, col_next = st.columns([1, 2, 1])
    
    with col_back:
        if st.button("←", type="secondary") and current_idx > 0:
            st.session_state.card_idx -= 1
            st.session_state.is_flipped = False
            st.rerun()
            
    with col_flip:
        if st.button("Balik Kartu", type="primary"):
            st.session_state.is_flipped = not st.session_state.is_flipped
            st.rerun()
            
    with col_next:
        if st.button("→", type="secondary") and current_idx < len(words) - 1:
            st.session_state.card_idx += 1
            st.session_state.is_flipped = False
            st.rerun()
            
    st.write("")
    st.write("")
    st.divider()
    st.subheader("Uji Kemampuan")
    st.write("Coba kuis singkat berdasarkan kartu yang Anda pelajari.")
    st.write("")
    if st.button("Mulai Kuis", type="primary"):
        st.session_state.quiz_idx = 0
        st.session_state.quiz_score = 0
        random.shuffle(st.session_state.words_data)
        change_state('quiz')
        st.rerun()

# ==========================================
# LAYAR 3: QUIZ
# ==========================================
elif st.session_state.app_state == 'quiz':
    st.button("Hentikan Kuis", type="secondary", on_click=change_state, args=('study',))
    
    words = st.session_state.words_data
    total_q = len(words)
    q_idx = st.session_state.quiz_idx
    current_q = words[q_idx]
    
    st.write("")
    st.progress((q_idx) / total_q)
    st.write("")
    st.caption(f"Soal {q_idx + 1} / {total_q}")
    
    st.write("")
    st.write("Apa kata bahasa Inggris yang tepat untuk arti ini?")
    st.info(current_q['definition_id'])
    
    if 'quiz_options' not in st.session_state or st.session_state.quiz_idx != st.session_state.get('last_q_idx', -1):
        others = [w['word'] for w in words if w['word'] != current_q['word']]
        wrong_choices = random.sample(others, min(1, len(others))) if others else ["unknown"]
        options = [current_q['word']] + wrong_choices
        random.shuffle(options)
        st.session_state.quiz_options = options
        st.session_state.last_q_idx = q_idx

    answer = st.radio("Pilih jawaban:", st.session_state.quiz_options, index=None, label_visibility="collapsed")
    
    st.write("")
    if st.button("Cek Jawaban", type="primary") and answer:
        if answer == current_q['word']:
            st.success("Benar.")
            st.session_state.quiz_score += 1
        else:
            st.error(f"Kurang tepat. Jawaban yang benar: {current_q['word']}")
            
        time.sleep(1.2)
        
        if q_idx < total_q - 1:
            st.session_state.quiz_idx += 1
        else:
            change_state('result')
        st.rerun()

# ==========================================
# LAYAR 4: HASIL
# ==========================================
elif st.session_state.app_state == 'result':
    total = len(st.session_state.words_data)
    score = st.session_state.quiz_score
    
    st.title("Hasil Kuis")
    st.write("")
    
    col_s, col_a = st.columns(2)
    col_s.metric("Skor", f"{score} / {total}")
    col_a.metric("Akurasi", f"{int((score/total)*100)}%")
    
    st.divider()
    
    st.write("")
    col_ulang, col_home = st.columns(2)
    with col_ulang:
        if st.button("Ulangi Kuis", type="primary"):
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            change_state('quiz')
            st.rerun()
    with col_home:
        if st.button("Menu Utama", type="secondary"):
            change_state('input')
            st.rerun()
