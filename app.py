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

# CSS Kustom: Modern Light Mode & Modern Font
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500&display=swap');

    html, body, [class*="css"], .stMarkdown p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #1F2937; 
    }

    *:focus {
        outline: none !important;
    }
    div[data-baseweb="input"]:focus-within, 
    div[data-baseweb="textarea"]:focus-within {
        border-color: #14B8A6 !important; 
        box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.1) !important;
    }

    .stTextArea > div {
        border-radius: 16px !important;
        background-color: transparent !important;
    }
    .stTextArea textarea {
        border-radius: 16px !important; 
        border: 1px solid #E5E7EB !important; 
        background-color: #FFFFFF !important; 
        color: #1F2937 !important;
        font-size: 15px;
        padding: 16px;
        transition: all 0.2s ease;
    }
    .stTextArea textarea:focus {
        border-color: #14B8A6 !important;
        box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.1) !important;
    }
    .stTextArea label {
        font-weight: 600 !important;
        color: #374151 !important; 
        font-size: 16px !important;
        margin-bottom: 8px !important;
    }

    .stButton>button[kind="primary"] {
        background-color: #14B8A6 !important;
        color: #FFFFFF !important; 
        border: none !important;
        border-radius: 14px !important;
        height: 52px;
        font-weight: 700 !important;
        font-size: 16px;
        transition: all 0.2s ease;
        box-shadow: 0 3px 8px rgba(20, 184, 166, 0.1) !important;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #0D9488 !important; 
        transform: translateY(-2px);
    }

    .stButton>button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 14px !important;
        height: 52px;
        font-weight: 600 !important;
        font-size: 16px;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="secondary"]:hover {
        border-color: #14B8A6 !important;
        color: #14B8A6 !important;
        background-color: #F9FAFB !important; 
    }

    .history-btn button {
        height: 40px !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        background-color: #F3F4F6 !important;
        color: #4B5563 !important;
        border: 1px dashed #D1D5DB !important;
    }
    .history-btn button:hover {
        border-color: #14B8A6 !important;
        color: #14B8A6 !important;
        background-color: #F0FDFA !important;
    }

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

    .card-front {
        background-color: #FFFFFF;
        border: 1px solid #F3F4F6;
        box-shadow: 0 8px 24px rgba(0,0,0,0.03); 
    }
    .word-title { 
        font-size: 42px; 
        font-weight: 800; 
        margin-bottom: 8px; 
        text-transform: capitalize; 
        color: #1F2937;
    }
    .word-phonetic { 
        font-size: 17px; 
        color: #14B8A6; 
        font-weight: 500;
        letter-spacing: 1px;
    }

    .card-back {
        background-color: #FFFFFF; 
        border: 1px solid #14B8A6; 
        box-shadow: 0 8px 32px rgba(20, 184, 166, 0.05);
    }
    .word-label { 
        font-size: 12px; 
        color: #6B7280; 
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
        color: #1F2937;
    }
    .word-example { 
        font-size: 15px; 
        font-style: italic; 
        color: #4B5563; 
        max-width: 90%;
        line-height: 1.5;
    }

    .stProgress > div > div > div > div {
        background-color: #14B8A6 !important;
        border-radius: 10px;
    }
    .stAlert {
        border-radius: 12px;
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        color: #1F2937 !important;
    }
    h1 { font-weight: 800; letter-spacing: -1.5px; color: #1F2937; }
    h2, h3 { font-weight: 700; color: #1F2937; }
    p { color: #4B5563; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DAFTAR KATA UMUM YANG AKAN DIBUANG
# ==========================================
COMMON_WORDS = {
    "about", "above", "after", "again", "against", "almost", "along", "already", "also", "although",
    "always", "among", "another", "anyone", "anything", "around", "because", "become", "before", 
    "behind", "being", "below", "beside", "between", "beyond", "could", "doing", "during", "either", 
    "enough", "everyone", "everything", "everywhere", "except", "first", "further", "great", "herself", 
    "himself", "however", "itself", "little", "might", "myself", "never", "nothing", "nowhere", 
    "other", "ourselves", "please", "quite", "rather", "really", "right", "second", "shall", "should", 
    "someone", "something", "somewhere", "still", "their", "theirs", "themselves", "there", "therefore", 
    "these", "thing", "think", "those", "though", "through", "throughout", "together", "under", "until", 
    "whatever", "whenever", "where", "whether", "which", "while", "whoever", "whole", "whose", "within", 
    "without", "would", "yours", "yourself", "yourselves", "found", "using", "makes", "takes", "gives"
}

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
if 'text_history' not in st.session_state:
    st.session_state.text_history = []
if 'input_text_widget' not in st.session_state:
    st.session_state.input_text_widget = ""

# ==========================================
# FUNGSI PEMBANTU
# ==========================================
def extract_words(text, max_words):
    words = [w.lower() for w in re.findall(r"[a-zA-Z]{5,}", text)]
    unique_words = list(dict.fromkeys(words))
    filtered_words = [w for w in unique_words if w not in COMMON_WORDS]
    filtered_words.sort(key=len, reverse=True)
    
    top_complex = filtered_words[:40]
    random.shuffle(top_complex)
    
    return top_complex[:max_words]

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

def set_input_from_history(text):
    st.session_state.input_text_widget = text

# ==========================================
# LAYAR 1: INPUT TEKS
# ==========================================
if st.session_state.app_state == 'input':
    st.title("VocabMaster")
    st.write("Ubah teks bahasa Inggris menjadi kartu belajar modern.")
    st.write("")
    
    text_input = st.text_area(
        "Masukkan Teks Bahasa Inggris", 
        height=200, 
        key="input_text_widget",
        placeholder="Ketik atau tempel paragraf, kalimat, atau daftar kata di sini..."
    )
    
    st.write("")
    max_vocab = st.slider(
        "🎯 Ingin belajar berapa kata dari teks ini?", 
        min_value=5, max_value=30, value=10, step=1,
        help="Sistem akan otomatis mencarikan kata-kata paling rumit/panjang dari teksmu."
    )
    
    if st.session_state.text_history:
        st.markdown("<p style='font-size: 14px; font-weight: 600; margin-top: 5px; margin-bottom: 5px; color:#6B7280;'>🕒 Riwayat Teks Sesi Ini:</p>", unsafe_allow_html=True)
        for i, past_text in enumerate(st.session_state.text_history):
            preview_text = past_text[:50] + "..." if len(past_text) > 50 else past_text
            st.markdown('<div class="history-btn">', unsafe_allow_html=True)
            st.button(f"📄 {preview_text}", key=f"hist_{i}", on_click=set_input_from_history, args=(past_text,))
            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    if st.button("Buat Kartu Belajar", type="primary"):
        if not text_input.strip():
            st.warning("Silakan masukkan teks terlebih dahulu.")
        else:
            words = extract_words(text_input, max_words=max_vocab)
            
            if not words:
                st.error("Tidak ada kosakata level menengah/lanjut yang ditemukan di teks tersebut.")
            else:
                if text_input.strip() not in st.session_state.text_history:
                    if len(st.session_state.text_history) >= 5:
                        st.session_state.text_history.pop(0)
                    st.session_state.text_history.append(text_input.strip())
                
                with st.spinner(f"Menerjemahkan {len(words)} kata tersulit untukmu..."):
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
