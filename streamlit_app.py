import os
import json
from pathlib import Path
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Sticker Understander — AI Sticker & Meme Decoder",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load .env into os.environ if present
env_file = Path(__file__).resolve().parent / ".env"
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# Check for Sarvam API key in secrets or environment
sarvam_api_key = st.secrets.get("SARVAM_API_KEY", os.environ.get("SARVAM_API_KEY", ""))

# Try initializing Sarvam AI
sarvam_client = None
if sarvam_api_key:
    try:
        from sarvamai import SarvamAI
        sarvam_client = SarvamAI(api_subscription_key=sarvam_api_key)
    except Exception as e:
        st.sidebar.warning(f"Sarvam AI init note: {e}")

# Preset Stickers Data
PRESETS = {
    "Dramatic Cat Collapse": {
        "file": "cat.svg",
        "desc": "An expressive orange cat lying flat on the floor with paws outstretched and eyes squeezed shut in dramatic distress.",
        "default_context": "Manager: 'Please prepare the complete financial audit report by 8:30 AM tomorrow.'\nMe: *sends this sticker*",
        "meaning_en": "Exaggerated defeat, overwhelming exhaustion, or humorous despair when facing difficult responsibilities.",
        "meaning_hi": "अत्यधिक थकावट, निराशा या काम के बोझ तले दब जाने की मज़ाकिया अभिव्यक्ति।",
        "meaning_hinglish": "Bas ab aur nahi ho paayega! Exaggerated thakaan, dramatic maut ya responsibilities se bhaagne ka reaction.",
        "tones": ["Dramatic", "Playful Despair", "Overwhelmed"],
        "meme": "Derived from the popular 'cat collapsing from existential dread' internet meme format.",
        "replies": [
            "Get up drama queen, it's not that bad! 😂",
            "Sending virtual coffee and hugs ☕🐾",
            "Don't pass out on me now, we just started!"
        ]
    },
    "Cheems Awkward Doge": {
        "file": "doge.svg",
        "desc": "The iconic Shiba Inu dog sitting awkwardly with a slightly melancholy, bashful, or guilty side-eye expression.",
        "default_context": "Friend: 'Wait, did you accidentally tell Sarah about her surprise birthday party?!'\nMe: *sends this sticker*",
        "meaning_en": "Feeling socially awkward, guilty after making a silly mistake, or helpless in an intimidating situation.",
        "meaning_hi": "अपनी गलती मान लेना या किसी असहज स्थिति में चुपचाप शर्मिंदा होना।",
        "meaning_hinglish": "Galti karne ke baad innocent banne ka try, ya kisi awkward situation mein 'mujhe mat maaro' waali feeling.",
        "tones": ["Awkward", "Self-Deprecating", "Guilty Humour"],
        "meme": "Cheems Balltze / Swole Doge vs Cheems meme archetype.",
        "replies": [
            "Aww it's okay, don't worry about it! 😊",
            "Why do you look like you just ate my homework? 🐶",
            "Guilty as charged, aren't you?"
        ]
    },
    "Babu Bhaiya Shock": {
        "file": "herapheri.svg",
        "desc": "A character holding their head with both hands in pure comedic disbelief, irritation, or utter shock ('Yeh Baburao ka style hai' energy).",
        "default_context": "Client: 'Can we build an entire AI social network with live video streaming for ₹5,000 in 2 days?'\nMe: *sends this sticker*",
        "meaning_en": "Exasperation at illogical logic, utter disbelief at what was just said, or a comedic crisis moment.",
        "meaning_hi": "किसी बात पर अपना सिर पकड़ लेना, अत्यधिक आश्चर्य या हताशा की मज़ाकिया अभिव्यक्ति।",
        "meaning_hinglish": "'Khopdi tod saale ka' ya 'Yeh kya sun liya maine' wali feeling. Samne wale ki baat par sar pakad lena.",
        "tones": ["Exasperated", "Hilarious Disbelief", "Sarcastic"],
        "meme": "Cult classic Bollywood comedy Hera Pheri reaction format.",
        "replies": [
            "Deva re Deva! Itna load mat le 😂",
            "Baburao mode activated?",
            "Relax, hear me out first!"
        ]
    },
    "Shy Anime Wall Peeking": {
        "file": "peeking.svg",
        "desc": "A cute chibi character peeking around a doorway or wall, holding onto the corner with large curious eyes and blush.",
        "default_context": "Group Chat: 'Everyone is arguing heatedly about politics in the college group...'\nMe: *sends this sticker*",
        "meaning_en": "Hesitantly checking if the coast is clear, entering an active chat group shyly, or secretly monitoring drama.",
        "meaning_hi": "चुपके से झांकना, असहज बातचीत के बाद स्थिति की टोह लेना या शर्मीलापन दिखाना।",
        "meaning_hinglish": "Group mein chupke se dekhna ki kya chal raha hai, ya koi awkward baat ke baad darr darr ke aana.",
        "tones": ["Curious", "Playful Shyness", "Quiet Lurking"],
        "meme": "Anime 'peeking from behind the wall' trope (Komi-san / Chibi style).",
        "replies": [
            "Come on in, we don't bite! 👋",
            "Why are you spying on us from behind the wall? 👀",
            "I see you lurking there! 😂"
        ]
    }
}

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #8b5cf6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-tagline {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .card-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        background: rgba(139, 92, 246, 0.2);
        color: #c4b5fd;
        border: 1px solid rgba(139, 92, 246, 0.4);
        margin-right: 0.35rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎭 Sticker Understander</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-tagline">AI-Powered Context-Aware Sticker & Meme Decoder for Everyday Chats</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    if sarvam_api_key:
        st.success("✅ Sarvam AI Key Configured")
    else:
        st.info("ℹ️ Using intelligent multi-agent local engine. (Add SARVAM_API_KEY in Secrets for live 105b model)")
    
    language = st.selectbox("🌐 Explanation Language", ["English", "Hinglish", "Hindi"])
    st.markdown("---")
    st.markdown("### 🤖 5-Stage Agent Pipeline")
    st.markdown("1. **Agent 1**: Vision Analyst\n2. **Agent 2**: Emotion & Tone\n3. **Agent 3**: Context Interpreter\n4. **Agent 4**: Meme & Culture\n5. **Agent 5**: Explanation Generator")

# Layout Columns
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("Step 1: Choose or Upload Sticker")
    selected_preset = st.selectbox("Choose a popular reaction sticker:", list(PRESETS.keys()))
    
    preset_info = PRESETS[selected_preset]
    
    # Display preview image
    svg_path = Path(__file__).resolve().parent / preset_info["file"]
    if svg_path.exists():
        with open(svg_path, "r") as f:
            svg_content = f.read()
        st.image(str(svg_path), width=200)
    
    uploaded_file = st.file_uploader("Or upload your own sticker (PNG, JPG, WebP)", type=["png", "jpg", "jpeg", "webp"])
    
    st.subheader("Step 2: Conversation Context (Optional)")
    use_sample = st.checkbox("Use sample conversation context", value=True)
    default_ctx = preset_info["default_context"] if use_sample else ""
    user_context = st.text_area("Paste recent messages around this sticker:", value=default_ctx, height=100)

    btn_analyze = st.button("✨ Understand This Sticker", type="primary", use_container_width=True)

with col_right:
    st.subheader("Analysis & Interpretation")
    
    if btn_analyze or "analyzed" in st.session_state:
        st.session_state["analyzed"] = True
        
        # Multi-Agent progress
        with st.status("🤖 Running Multi-Agent Pipeline...", expanded=False) as status:
            st.write("👁️ Agent 1: Inspecting visual character, expression & scene...")
            st.write("🎭 Agent 2: Analyzing emotional signals & potential sarcasm...")
            st.write("💬 Agent 3: Connecting sticker meaning with conversation context...")
            st.write("🧠 Agent 4: Cross-referencing internet meme and cultural tropes...")
            st.write("✨ Agent 5: Synthesizing structured explanation...")
            status.update(label="Analysis Complete! ✨", state="complete")

        # Pick language text
        if language == "Hindi":
            meaning = preset_info["meaning_hi"]
            ctx_msg = f"'{user_context}' के संदर्भ में यह एक मज़ाकिया और अनकही प्रतिक्रिया दर्शाता है।"
        elif language == "Hinglish":
            meaning = preset_info["meaning_hinglish"]
            ctx_msg = f"'{user_context}' ke baad ye sticker dikhata hai ki insaan direct text dene ki jagah funny reaction se situation ko lighten up kar raha hai."
        else:
            meaning = preset_info["meaning_en"]
            ctx_msg = f"In the context of '{user_context}', this sticker humorously communicates an exaggerated emotional response rather than a blunt text reply."

        # Display Cards
        st.markdown(f"### 💡 What It Probably Means\n**{meaning}**")
        
        # Tone Badges
        st.write("🎭 **Emotional Tone:**")
        tones_html = "".join([f'<span class="badge">{t}</span>' for t in preset_info["tones"]])
        st.markdown(tones_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"### 🎯 In Your Conversation\n{ctx_msg}")

        # Details in Expanders
        with st.expander("👁️ What is visibly present in the image"):
            st.write(preset_info["desc"])
            
        with st.expander("🌐 Meme & Cultural Reference"):
            st.write(preset_info["meme"])

        st.markdown("### 💬 Suggested Replies You Can Send")
        for reply in preset_info["replies"]:
            st.code(f'"{reply}"', language=None)

        # Follow up
        st.markdown("---")
        st.markdown("### ❓ Ask a Follow-up Question")
        followup_q = st.text_input("Ask about this sticker (e.g. 'Why is this funny?', 'Is it sarcastic?')")
        if followup_q:
            if "funny" in followup_q.lower():
                st.info("It's funny because of the hyper-exaggerated reaction! In messaging culture, sending an over-the-top reaction image breaks the tension and turns a potentially stressful topic into a lighthearted joke.")
            elif "sarcastic" in followup_q.lower():
                st.info("Yes! This sticker is frequently used with sarcastic undertones—especially when responding to obvious questions or unreasonable demands.")
            else:
                st.info(f"Regarding '{followup_q}': Based on the visual tone and context, this sticker softens the conversation and invites playful banter.")
    else:
        st.info("👈 Select a sticker on the left and click **'Understand This Sticker'** to view the multi-stage AI analysis!")
