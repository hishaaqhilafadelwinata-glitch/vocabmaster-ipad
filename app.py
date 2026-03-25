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

# CSS Kustom untuk Tampilan yang Lebih Humanize & Bersih
st.markdown("""
<style>
    /* Mengubah font dasar Streamlit menjadi lebih clean */
    html, body, [class*="css"]  {
        font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #1F2937; /* Charcoal gelap, lebih nyaman di mata dibanding hitam pekat */
    }

    /* Styling tombol utama (Primary) */
    .stButton>button[kind="primary"] {
        background-color: #4F46E5; /* Indigo hangat */
        color: white;
        border: none;
        border-radius: 8px; /* Sedikit melengkung, tidak terlalu kotak/bulat */
        height: 48px;
        font-weight: 600;
        font-size: 15px;
        letter-spacing: 0.3px;
        transition: background-color 0.2s;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #4338CA;
    }

    /* Styling tombol sekunder (Secondary) */
    .stButton>button[kind="secondary"] {
        background-color: #FFFFFF;
        color: #4F46E5;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        height: 48px;
        font-weight: 500;
        font-size: 15px;
        transition: all 0.2s;
    }
    .stButton>button[kind="secondary"]:hover {
        border-color: #4F46E5;
        background-color: #F9FAFB;
    }

    /* Styling Kotak Input Teks */
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border-color: #E5E7EB;
        font-size: 15px;
        padding: 12px;
    }
    .stTextArea>div>div>textarea:focus {
        border-color: #4F46E5;
        box-shadow: 0 0 0 1px #4F46E5;
    }

    /* Label Input */
    .stTextArea label {
        font-weight: 600;
        color: #374151;
        font-size: 16px;
        margin-bottom: 8px;
    }

    /* --- Styling Kartu Flashcard --- */
    /* Container dasar kartu */
    .vocab-card {
        padding: 40px 25px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); /* Bayangan sangat tipis, organik */
        margin: 20px 0;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* Kartu Depan (Putih Bersih) */
    .card-front {
        background-color: #FFFFFF;
        color: #1F2937;
        border: 1px solid #F3F4F6;
    }
    .word-title { 
        font-size: 38px; 
        font-weight: 700; 
        margin-bottom: 8px; 
        text-transform: capitalize; 
        letter-spacing: -1px;
    }
    .word-phonetic { 
        font-size: 16px; 
        color: #6B7280; /* Muted gray */
        font-weight: 400;
    }

    /* Kartu Belakang (Indigo Solid) */
    .card-back {
        background-color: #4F46E5;
        color: #FFFFFF;
    }
    .word-label { 
        font-size: 12px; 
        opacity: 0.7; 
        letter-spacing: 1px; 
        margin-bottom: 25px; 
        text-transform: uppercase;
    }
    .word-meaning { 
        font-size: 20px; 
        font-weight: 500; 
        margin-bottom: 20px; 
        line-height: 1.5;
    }
    .word-example { 
        font-size: 15px; 
        font-style: italic; 
        color: #E0E7FF; /* Light indigo text */
        max-width: 90%;
        line-height: 1.4;
    }

    /* Indikator Progres */
    .stProgress > div > div > div > div {
        background-color: #4F46E5;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 14px;
        color: #6B7280;
    }

    /* Styling Judul Halaman */
    h1 {
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 10px;
        font-size: 2.2rem;
    }
    h2 {
        font-weight: 700;
        font-size: 1.5rem;
        margin-top: 1.5rem;
    }
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
    st.write("Ubah teks bahasa Inggris menjadi kartu belajar sederhana.")
    st.write("")
    
    text_input = st.text_area("Masukkan Teks Bahasa Inggris", height=180, 
                              placeholder="Ketik atau tempel paragraf, kalimat, atau daftar kata di sini...")
    
    # Menghapus emoji dan mengubah teks tombol agar lebih bersih
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
                        time.sleep(0.05) # Jeda sangat singkat
                    
                    st.session_state.words_data = word_data_list
                    st.session_state.card_idx = 0
                    st.session_state.is_flipped = False
                    change_state('study')
                    st.rerun()

# ==========================================
# LAYAR 2: BELAJAR (FLASHCARD)
# ==========================================
elif st.session_state.app_state == 'study':
    # Menghapus ikon panah, menggunakan teks bersahaja
    st.button("Kembali ke Beranda", type="secondary", on_click=change_state, args=('input',))
    
    words = st.session_state.words_data
    current_idx = st.session_state.card_idx
    current_word = words[current_idx]
    
    # Progress bar tanpa emoji, ukuran teks lebih kecil
    st.write("")
    st.progress((current_idx + 1) / len(words))
    st.caption(f"Kartu {current_idx + 1} dari {len(words)}")
    
    # Render Kartu yang Sudah Disederhanakan
    if not st.session_state.is_flipped:
        st.markdown(f"""
        <div class="vocab-card card-front">
            <div class="word-title">{current_word['word']}</div>
            <div class="word-phonetic">{current_word['pronunciation']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Menghapus emoji, menyederhanakan teks label
        example_text = f'"{current_word["example"]}"' if current_word["example"] else ""
        st.markdown(f"""
        <div class="vocab-card card-back">
            <div class="word-label">ARTI</div>
            <div class="word-meaning">{current_word['definition_id']}</div>
            <div class="word-example">{example_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # Tombol Kontrol (Gunakan type="secondary" untuk Mundur/Maju agar visual tidak berat)
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
            
    # Area Mulai Kuis yang Lebih Bersih
    st.write("")
    st.write("")
    st.divider()
    st.subheader("Uji Kemampuan")
    st.write("Jika sudah merasa siap, coba kuis singkat berdasarkan kartu yang Anda pelajari.")
    if st.button("Mulai Kuis Sekarang", type="primary"):
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
    st.caption(f"Soal {q_idx + 1} / {total_q}")
    
    # Pertanyaan Kuis Sederhana
    st.write("")
    st.write("Apa kata bahasa Inggris yang tepat untuk arti ini?")
    st.info(current_q['definition_id'])
    
    if 'quiz_options' not in st.session_state or st.session_state.quiz_idx != st.session_state.get('last_q_idx', -1):
        others = [w['word'] for w in words if w['word'] != current_q['word']]
        # Mengurangi jumlah pilihan ganda agar tidak pusing
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
    
    # Gunakan st.snow() bukan balloons, lebih tenang visualnya
    st.snow()
    st.title("Hasil Kuis")
    
    col_s, col_a = st.columns(2)
    # Menghapus label metrik yang berlebihan
    col_s.metric("Skor", f"{score} / {total}")
    col_a.metric("Akurasi", f"{int((score/total)*100)}%")
    
    st.divider()
    
    col_ulang, col_home = st.columns(2)
    with col_ulang:
        # Menghapus emoji dari tombol
        if st.button("Ulangi Kuis", type="primary"):
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            change_state('quiz')
            st.rerun()
    with col_home:
        if st.button("Menu Utama", type="secondary"):
            change_state('input')
            st.rerun()
