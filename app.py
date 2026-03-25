import streamlit as st
import requests
import random
import re
import time
from deep_translator import GoogleTranslator

# ==========================================
# KONFIGURASI HALAMAN & TEMA EARTH TONE
# ==========================================
st.set_page_config(page_title="VocabMaster", page_icon="📖", layout="centered")

# CSS Kustom: Humanize, Earth Tone, Pastel Beige
st.markdown("""
<style>
    /* Mengubah font global dan warna background utama */
    @import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FAF7F0; /* Linen White */
        color: #4A4A4A; /* Charcoal Brown (Teks utama) */
        font-family: 'Urbanist', sans-serif;
    }

    [data-testid="stHeader"] {
        background-color: rgba(250, 247, 240, 0);
    }

    /* Styling Tombol Utama (Primary) - Sage Green */
    .stButton>button[kind="primary"] {
        background-color: #8DAA91; /* Sage Green */
        color: white;
        border: none;
        border-radius: 12px;
        height: 50px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #7E9981;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Styling Tombol Sekunder/Normal - Muted Beige */
    .stButton>button[kind="secondary"] {
        background-color: #E8E2D5; /* Muted Beige */
        color: #4A4A4A;
        border: 1px solid #D9D2C5;
        border-radius: 12px;
        height: 50px;
        font-weight: 600;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #D9D2C5;
        border-color: #CFC5B4;
    }

    /* Styling Kartu Depan - Pastel Beige/Sand */
    .card-front {
        background-color: #EADCC1; /* Sand Beige */
        color: #4A4A4A; /* Teks cokelat tua */
        padding: 50px 20px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid #D9CBAD;
        margin: 20px 0;
    }

    /* Styling Kartu Belakang - Earthy Sage */
    .card-back {
        background-color: #A7B09E; /* Earthy Green */
        color: #FDFCF5; /* Cream White (Teks terang) */
        padding: 40px 20px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid #97A18D;
        margin: 20px 0;
    }

    /* Tipografi di dalam kartu */
    .word-title { font-size: 40px; font-weight: 800; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;}
    .word-phonetic { font-size: 16px; color: rgba(74, 74, 74, 0.7); font-style: italic; }
    
    /* Untuk teks terang di kartu belakang */
    .card-back .word-meaning { font-size: 20px; font-weight: 600; margin-bottom: 15px; color: #FDFCF5;}
    .card-back .word-example { font-size: 15px; font-style: italic; color: rgba(253, 252, 245, 0.8);}
    .card-back .card-label { font-size: 12px; margin-bottom: 20px; color: rgba(253, 252, 245, 0.7); text-transform: uppercase; letter-spacing: 2px;}

    /* Perbaikan visual area input */
    .stTextArea textarea {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #D9D2C5;
    }

    /* Perbaikan visual Radio buttons */
    div[data-testid="stMarkdownContainer"] p { font-size: 16px; }
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
    # Membersihkan karakter non-huruf dan mengambil kata 4 huruf ke atas
    words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{4,}\b", text)]
    return list(dict.fromkeys(words)) # Hapus duplikat

def fetch_definition(word):
    # Mengambil definisi dasar dan contoh (Bahasa Inggris)
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
                
                # Menerjemahkan definisi ke Bahasa Indonesia
                if def_en:
                    try:
                        result["definition_id"] = GoogleTranslator(source='en', target='id').translate(def_en)
                    except Exception:
                        result["definition_id"] = def_en # Fallback
    except Exception:
        pass
    return result

def change_state(new_state):
    st.session_state.app_state = new_state

# ==========================================
# LAYAR 1: INPUT TEKS
# ==========================================
if st.session_state.app_state == 'input':
    st.title("VocabMaster")
    st.write("Ubah paragraf atau kalimat bahasa Inggris menjadi kartu belajar minimalis.")
    
    text_input = st.text_area("✍️ Teks Bahasa Inggris:", height=180, 
                              placeholder="Ketik atau tempel teks bahasa Inggris di sini...")
    
    # Tombol menggunakan type="primary" untuk warna Sage Green
    if st.button("Mulai Belajar", type="primary"):
        if not text_input.strip():
            st.warning("Silakan masukkan teks terlebih dahulu.")
        else:
            words = extract_words(text_input)
            if not words:
                st.error("Tidak ditemukan kosakata yang valid (minimal 4 huruf).")
            else:
                with st.spinner("Mengambil definisi & menerjemahkan..."):
                    word_data_list = []
                    # Batasi jumlah kata agar tidak terlalu lama (misal 15 kata)
                    limited_words = words[:15]
                    progress_bar = st.progress(0)
                    for i, w in enumerate(limited_words):
                        word_data_list.append(fetch_definition(w))
                        progress_bar.progress((i + 1) / len(limited_words))
                        time.sleep(0.05) # Jeda halus
                    
                    if word_data_list:
                        st.session_state.words_data = word_data_list
                        st.session_state.card_idx = 0
                        st.session_state.is_flipped = False
                        change_state('study')
                        st.rerun()
                    else:
                        st.error("Gagal mengambil data definisi.")

# ==========================================
# LAYAR 2: BELAJAR (FLASHCARD)
# ==========================================
elif st.session_state.app_state == 'study':
    col_back, _ = st.columns([1, 4])
    with col_back:
        # Tombol kembali menggunakan type="secondary" (Beige)
        st.button("Beranda", on_click=change_state, args=('input',), type="secondary")
    
    words = st.session_state.words_data
    current_idx = st.session_state.card_idx
    current_word = words[current_idx]
    
    # Progres bar minimalis
    st.progress((current_idx + 1) / len(words))
    st.caption(f"Kartu {current_idx + 1} dari {len(words)}")
    
    # Render Kartu
    if not st.session_state.is_flipped:
        st.markdown(f"""
        <div class="card-front">
            <div class="word-title">{current_word['word']}</div>
            <div class="word-phonetic">{current_word['pronunciation']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card-back">
            <div class="card-label">✦ ARTI KATA ✦</div>
            <div class="word-meaning">{current_word['definition_id']}</div>
            <div class="word-example">"{current_word['example']}"</div>
        </div>
        """, unsafe_allow_html=True)

    # Tombol Kontrol Flashcard (Menggunakan Kolom agar sejajar di iPad)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Gunakan type="secondary" untuk kontrol navigasi
        if st.button("←", type="secondary") and current_idx > 0:
            st.session_state.card_idx -= 1
            st.session_state.is_flipped = False
            st.rerun()
            
    with col2:
        # Gunakan type="primary" untuk tombol aksi utama
        if st.button("Balik Kartu", type="primary"):
            st.session_state.is_flipped = not st.session_state.is_flipped
            st.rerun()
            
    with col3:
        if st.button("→", type="secondary") and current_idx < len(words) - 1:
            st.session_state.card_idx += 1
            st.session_state.is_flipped = False
            st.rerun()
            
    st.divider()
    if st.button("🎯 Uji Kemampuan (Quiz)", type="secondary"):
        st.session_state.quiz_idx = 0
        st.session_state.quiz_score = 0
        random.shuffle(st.session_state.words_data)
        change_state('quiz')
        st.rerun()

# ==========================================
# LAYAR 3: QUIZ
# ==========================================
elif st.session_state.app_state == 'quiz':
    col_back, _ = st.columns([1, 4])
    with col_back:
        st.button("Tutup Quiz", on_click=change_state, args=('study',), type="secondary")
    
    words = st.session_state.words_data
    total_q = len(words)
    q_idx = st.session_state.quiz_idx
    current_q = words[q_idx]
    
    st.progress((q_idx) / total_q)
    st.caption(f"Soal {q_idx + 1} / {total_q}")
    
    st.subheader("Apa kata yang tepat untuk arti ini?")
    # Menggunakan komponen st.info dengan kustomisasi CSS minimal
    st.info(current_q['definition_id'])
    
    # Buat pilihan ganda (1 Benar, 2 Salah)
    if 'quiz_options' not in st.session_state or st.session_state.quiz_idx != st.session_state.get('last_q_idx', -1):
        others = [w['word'] for w in words if w['word'] != current_q['word']]
        # Ambil maksimal 2 kata lain untuk pengecoh
        wrong_choices = random.sample(others, min(2, len(others))) if others else ["unknown", "n/a"]
        options = [current_q['word']] + wrong_choices
        random.shuffle(options)
        st.session_state.quiz_options = options
        st.session_state.last_q_idx = q_idx

    answer = st.radio("Pilih jawaban:", st.session_state.quiz_options, index=None)
    
    if st.button("Cek Jawaban", type="primary") and answer:
        if answer == current_q['word']:
            st.success("✅ Benar!")
            st.session_state.quiz_score += 1
        else:
            st.error(f"❌ Kurang tepat. Jawaban benar: **{current_q['word']}**")
            
        time.sleep(1.2) # Jeda halus
        
        if q_idx < total_q - 1:
            st.session_state.quiz_idx += 1
        else:
            change_state('result')
        st.rerun()

# ==========================================
# LAYAR 4: HASIL QUIZ
# ==========================================
elif st.session_state.app_state == 'result':
    total = len(st.session_state.words_data)
    score = st.session_state.quiz_score
    
    st.balloons()
    st.title("🏆 Selesai!")
    st.write("Berikut adalah hasil quiz kemampuan kamu.")
    
    col1, col2 = st.columns(2)
    col1.metric("Skor Kamu", f"{score} / {total}")
    col2.metric("Akurasi", f"{int((score/total)*100)}%")
    
    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Ulangi Quiz", type="primary"):
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            # Acak ulang kata
            random.shuffle(st.session_state.words_data)
            change_state('quiz')
            st.rerun()
    with col_b:
        if st.button("Menu Utama", type="secondary"):
            change_state('input')
            st.rerun()
