import streamlit as st
import numpy as np
import tensorflow as tf
import pickle
import requests


# ---------------- CONFIG ----------------
st.set_page_config(page_title="HELP-ML", layout="centered")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

/* Glass effect */
.block-container {
    background: rgba(255, 255, 255, 0.12);
    padding: 1.5rem;
    border-radius: 20px;
    backdrop-filter: blur(12px);
}

/* Titles */
h1, h2, h3 {
    text-align: center;
    color: white;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(45deg, #ff4b4b, #ff8c00);
    color: white;
    border-radius: 14px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    border: none;
}

/* Inputs */
.stCheckbox label {
    font-size: 18px !important;
}

textarea {
    font-size: 16px !important;
}

/* Center fix */
.main-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    text-align: center;
}

.title {
    font-size: 42px;
    font-weight: bold;
}

.subtitle {
    font-size: 18px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
model = tf.keras.models.load_model("model.h5")

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# ---------------- FUNCTIONS ----------------
def get_location():
    try:
        res = requests.get("https://ipinfo.io/json")
        data = res.json()
        return data.get("city", "Unknown")
    except:
        return "Unknown"

def voice_to_text():
    return "Voice input not supported in web version"

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = 1

if "cases" not in st.session_state:
    st.session_state.cases = []

# ---------------- PAGE 1 ----------------
if st.session_state.page == 1:

    st.markdown("""
    <div class="main-container">
        <div class="title">🚑 HELP-ML</div>
        <div class="subtitle">Human Emergency Priority Prediction</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Start ➡️"):
        st.session_state.page = 2
        st.rerun()

# ---------------- PAGE 2 ----------------
elif st.session_state.page == 2:

    st.title("Enter Emergency Cases")

    num_cases = st.number_input(
        "Number of cases",
        min_value=2,
        max_value=10,
        value=2
    )

    cases = []

    for i in range(num_cases):
        st.markdown(f"### Case {i+1}")

        fever = st.checkbox("Fever", key=f"f{i}")
        injury = st.checkbox("Injury", key=f"i{i}")
        bleeding = st.checkbox("Bleeding", key=f"b{i}")
        unconscious = st.checkbox("Unconscious", key=f"u{i}")
        breathing = st.checkbox("Breathing Issue", key=f"br{i}")

        col1, col2 = st.columns([3,1])

        with col1:
            text = st.text_area("Description", key=f"t{i}")

        with col2:
            if st.button("🎤", key=f"mic{i}"):
                spoken = voice_to_text()
                st.session_state[f"t{i}"] = spoken
                st.rerun()

        st.markdown("---")

        cases.append((fever, injury, bleeding, unconscious, breathing, text))

    if st.button("Submit Cases 🚀"):
        st.session_state.cases = cases
        st.session_state.page = 3
        st.rerun()

# ---------------- PAGE 3 ----------------
elif st.session_state.page == 3:

    st.title("Result")

    location = get_location()
    st.info(f"📍 Your Location: {location}")

    max_level = -1
    max_case = -1
    classes = ["LOW", "MEDIUM", "HIGH"]

    with st.spinner("Analyzing cases..."):
        for idx, data in enumerate(st.session_state.cases):

            symptoms = np.array([data[:5]])
            text_vec = vectorizer.transform([data[5]]).toarray()

            input_data = np.concatenate((symptoms, text_vec), axis=1)

            pred = model.predict(input_data)
            level = np.argmax(pred)

            if level > max_level:
                max_level = level
                max_case = idx + 1

    st.markdown("---")

    st.success(f"✅ Highest Emergency Case: Case {max_case}")
    st.error(f"🚑 Level: {classes[max_level]}")

    # ---------------- SMART SUGGESTION ----------------
    if classes[max_level] == "HIGH":
        st.error("🚨 Immediate action required! Call ambulance!")
    elif classes[max_level] == "MEDIUM":
        st.warning("⚠️ Visit nearest hospital soon.")
    else:
        st.success("✅ Low risk. Monitor patient.")

    # ---------------- EMERGENCY CALL ----------------
    st.markdown("### 🚑 Emergency Help")

    st.markdown("""
    <a href="tel:108">
    <button style="
    width:100%;
    height:50px;
    background:red;
    color:white;
    font-size:20px;
    border:none;
    border-radius:10px;">
    📞 Call Ambulance (108)
    </button>
    </a>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Restart"):
        st.session_state.page = 1
        st.rerun()
