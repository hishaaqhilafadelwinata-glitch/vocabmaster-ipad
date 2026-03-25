import streamlit as st
import requests
import random
import re
import time
import google.generativeai as genai

# ==========================================
# KONFIGURASI HALAMAN (Responsif untuk iPad)
# ==========================================
st.set_page_config(page_title="VocabMaster", page_icon="📚", layout="centered")

# CSS Kustom agar tombol dan kartu lebih enak disentuh (Touch-friendly UI)
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 55px;
        font-weight: bold;
        font-size: 16px;
    }
    .card-front {
        background: linear-gradient(135deg, #6155EA, #4A3DD4);
        color: white;
        padding: 60px 20px;
        border-radius: 24px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .card-back {
        background: linear-gradient(135deg, #5C5FEF, #7578F5);
        color: white;
        padding: 40px 20px;
        border-radius: 24px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .word-title { font-size: 42px; font-weight: 800; margin-bottom: 10px; text-transform: uppercase;}
    .word-phonetic { font-size: 18px; color: #DCD9FA; }
    .word-meaning { font-size: 22px; font-weight: 600; margin-bottom: 15px;}
    .word-example { font-size: 16px; font-style: italic; color: #E0E3FF;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# INISIALISASI STATE (Manajemen Memori App)
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
    result = {"word": word, "pronunciation": "", "definition_en": "(Definisi tidak ditemukan)", "example": ""}
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
                result["definition_en"] = d.get("definition", "")
                result["example"] = d.get("example", "")
    except Exception:
        pass
    return result

def change_state(new_state):
    st.session_state.app_state = new_state

# ==========================================
# LAYAR 1: INPUT TEKS
# ==========================================
if st.session_state.app_state == 'input':
    st.title("📚 VocabMaster")
    st.write("Ubah teks bahasa Inggris apapun menjadi Flashcard interaktif!")
    
    text_input = st.text_area("✍️ Masukkan Teks Bahasa Inggris:", height=150, 
                              placeholder="Contoh: The entrepreneur's tenacious pursuit of innovation led to unprecedented breakthroughs...")
    
    if st.button("🚀 Ekstrak Kosakata & Mulai Belajar", type="primary"):
        if not text_input.strip():
            st.warning("Teks tidak boleh kosong!")
        else:
            words = extract_words(text_input)
            if not words:
                st.error("Tidak ada kata bahasa Inggris yang valid ditemukan.")
            else:
                with st.spinner(f"Memproses {len(words)} kata..."):
                    word_data_list = []
                    for w in words:
                        word_data_list.append(fetch_definition(w))
                        time.sleep(0.1)
                    
                    st.session_state.words_data = word_data_list
                    st.session_state.card_idx = 0
                    st.session_state.is_flipped = False
                    change_state('study')
                    st.rerun()

# ==========================================
# LAYAR 2: BELAJAR (FLASHCARD)
# ==========================================
elif st.session_state.app_state == 'study':
    st.button("← Kembali ke Beranda", on_click=change_state, args=('input',))
    
    words = st.session_state.words_data
    current_idx = st.session_state.card_idx
    current_word = words[current_idx]
    
    st.progress((current_idx + 1) / len(words), text=f"Kartu {current_idx + 1} dari {len(words)}")
    
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
            <div style="font-size: 14px; margin-bottom: 20px; color: #E0E3FF;">✦ ARTI KATA ✦</div>
            <div class="word-meaning">{current_word['definition_en']}</div>
            <div class="word-example">"{current_word['example']}"</div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️ Mundur") and current_idx > 0:
            st.session_state.card_idx -= 1
            st.session_state.is_flipped = False
            st.rerun()
            
    with col2:
        if st.button("🔄 Balik Kartu"):
            st.session_state.is_flipped = not st.session_state.is_flipped
            st.rerun()
            
    with col3:
        if st.button("Maju ➡️") and current_idx < len(words) - 1:
            st.session_state.card_idx += 1
            st.session_state.is_flipped = False
            st.rerun()
            
    st.divider()
    if st.button("🎯 Mulai Quiz", type="primary"):
        st.session_state.quiz_idx = 0
        st.session_state.quiz_score = 0
        random.shuffle(st.session_state.words_data)
        change_state('quiz')
        st.rerun()

# ==========================================
# LAYAR 3: QUIZ
# ==========================================
elif st.session_state.app_state == 'quiz':
    st.button("← Berhenti Quiz", on_click=change_state, args=('study',))
    
    words = st.session_state.words_data
    total_q = len(words)
    q_idx = st.session_state.quiz_idx
    current_q = words[q_idx]
    
    st.progress((q_idx) / total_q, text=f"Soal {q_idx + 1} / {total_q}")
    st.subheader("Apa kata yang tepat untuk definisi ini?")
    st.info(current_q['definition_en'])
    
    if 'quiz_options' not in st.session_state or st.session_state.quiz_idx != st.session_state.get('last_q_idx', -1):
        others = [w['word'] for w in words if w['word'] != current_q['word']]
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
            st.error(f"❌ Kurang tepat. Jawaban yang benar adalah: **{current_q['word']}**")
            
        time.sleep(1.5)
        
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
    
    st.balloons()
    st.title("🏆 Quiz Selesai!")
    
    col1, col2 = st.columns(2)
    col1.metric("Skor Kamu", f"{score} / {total}")
    col2.metric("Akurasi", f"{int((score/total)*100)}%")
    
    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Ulangi Quiz"):
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            change_state('quiz')
            st.rerun()
    with col_b:
        if st.button("🏠 Menu Utama"):
            change_state('input')
            st.rerun()
