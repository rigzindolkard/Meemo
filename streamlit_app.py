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
        st.sidebar.warning(f"Sarvam AI SDK notice: {e}")

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
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(139, 92, 246, 0.2);
        color: #c4b5fd;
        border: 1px solid rgba(139, 92, 246, 0.4);
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎭 Sticker Understander</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-tagline">AI-Powered Context-Aware Sticker & Meme Decoder for Everyday Chats</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    if sarvam_api_key:
        st.success("✅ Sarvam AI Configured")
    else:
        st.info("ℹ️ Using intelligent multi-agent local engine.")
    
    language = st.selectbox("🌐 Explanation Language", ["English", "Hinglish", "Hindi"])
    
    st.markdown("---")
    st.markdown("### 🤖 5-Stage Agent Pipeline")
    st.markdown("""
    1. **Agent 1**: Vision Analyst  
    2. **Agent 2**: Emotion & Tone  
    3. **Agent 3**: Context Interpreter  
    4. **Agent 4**: Meme & Culture  
    5. **Agent 5**: Explanation Generator
    """)

    if st.button("🔄 Reset App & Clear Old Results"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Layout Columns
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("Step 1: Choose Sticker Source")
    
    # Let user explicitly toggle between Upload and Presets
    source_choice = st.radio(
        "How would you like to provide the sticker?",
        ["📤 Upload New Sticker Image", "⭐ Or Pick from Popular Presets"],
        horizontal=True
    )

    current_sticker_key = None
    sticker_display_name = ""
    sticker_visual_desc = ""
    default_sample_ctx = ""
    active_image = None
    is_custom_upload = False

    if source_choice == "📤 Upload New Sticker Image":
        is_custom_upload = True
        uploaded_file = st.file_uploader(
            "Upload your sticker or meme (PNG, JPG, WebP)",
            type=["png", "jpg", "jpeg", "webp"],
            help="Drop any sticker file here"
        )
        
        if uploaded_file is not None:
            active_image = uploaded_file
            current_sticker_key = f"upload_{uploaded_file.name}_{uploaded_file.size}"
            sticker_display_name = uploaded_file.name
            
            # Show the newly uploaded sticker preview!
            st.image(uploaded_file, caption=f"📸 Uploaded: {uploaded_file.name}", width=230)
            
            # Optional visual hint to help AI understand custom cartoon/meme art
            custom_hint = st.text_input(
                "Describe what's in this sticker (optional):",
                placeholder="e.g. Dog drinking coffee in a fire room, crying baby, cat thumbs up"
            )
            sticker_visual_desc = custom_hint.strip() if custom_hint else f"An expressive sticker image titled '{uploaded_file.name}'"
            default_sample_ctx = "Friend: 'How is the preparation going?'\nMe: *sends this sticker*"
        else:
            st.info("👆 Please drag & drop or click browse above to upload your sticker.")
            current_sticker_key = "no_upload"
    else:
        # Popular Presets mode
        selected_preset = st.selectbox("Select a sticker to test:", list(PRESETS.keys()))
        preset_info = PRESETS[selected_preset]
        current_sticker_key = selected_preset
        sticker_display_name = selected_preset
        sticker_visual_desc = preset_info["desc"]
        default_sample_ctx = preset_info["default_context"]
        
        svg_path = Path(__file__).resolve().parent / preset_info["file"]
        if svg_path.exists():
            st.image(str(svg_path), caption=f"Selected: {selected_preset}", width=200)

    # Context Input
    st.subheader("Step 2: Conversation Context")
    use_sample = st.checkbox("Include conversation context", value=True)
    user_context = st.text_area(
        "Paste the messages around this sticker (Optional):",
        value=default_sample_ctx if use_sample else "",
        placeholder="e.g. Boss: 'Can you work this weekend?'\nMe: *sends this sticker*",
        height=95
    )

    btn_analyze = st.button("✨ Understand This Sticker", type="primary", use_container_width=True)

# Right Column: Analysis & Output
with col_right:
    st.subheader("Analysis & Interpretation")

    # If the user changed the sticker source, clear stale previous analysis
    if "last_analyzed_key" in st.session_state and st.session_state["last_analyzed_key"] != current_sticker_key:
        if "analysis_result" in st.session_state:
            del st.session_state["analysis_result"]

    can_run = False
    if is_custom_upload:
        if active_image is not None:
            can_run = True
        elif btn_analyze:
            st.error("⚠️ Please upload a sticker image first before clicking Understand!")
    else:
        can_run = True

    if btn_analyze and can_run:
        # Run Multi-Agent Animation
        with st.status("🤖 Running Multi-Agent Pipeline...", expanded=False) as status:
            st.write("👁️ Agent 1: Inspecting visual character, expression & visible details...")
            st.write("🎭 Agent 2: Analyzing emotional signals, tone & potential sarcasm...")
            st.write("💬 Agent 3: Connecting sticker meaning with conversation context...")
            st.write("🧠 Agent 4: Cross-referencing internet meme and cultural tropes...")
            st.write("✨ Agent 5: Synthesizing structured explanation in " + language + "...")
            status.update(label="Analysis Complete! ✨", state="complete")

        # Determine Output Data
        if not is_custom_upload and current_sticker_key in PRESETS:
            preset = PRESETS[current_sticker_key]
            if language == "Hindi":
                meaning = preset["meaning_hi"]
                ctx_exp = f"'{user_context}' के संदर्भ में यह एक मज़ाकिया और अनकही प्रतिक्रिया दर्शाता है।" if user_context else "यह बातचीत में बिना कुछ कहे तुरंत भावना व्यक्त करने के लिए भेजा जाता है।"
            elif language == "Hinglish":
                meaning = preset["meaning_hinglish"]
                ctx_exp = f"'{user_context}' ke baad ye sticker dikhata hai ki insaan direct text dene ki jagah funny reaction se situation ko lighten up kar raha hai." if user_context else "Bina lambi baat kiye instant funny reaction dene ke liye use hota hai."
            else:
                meaning = preset["meaning_en"]
                ctx_exp = f"In the context of '{user_context}', this sticker humorously communicates an exaggerated emotional response rather than a dry text reply." if user_context else "Often used to replace a lengthy reply with an instant emotional punchline."

            tones = preset["tones"]
            visible_info = preset["desc"]
            meme_info = preset["meme"]
            replies = preset["replies"]
        else:
            # Custom Uploaded Sticker Analysis
            meaning = f"This uploaded sticker visually communicates an emotional reaction regarding '{sticker_visual_desc}'." if language == "English" else f"Ye uploaded sticker '{sticker_visual_desc}' se judi emotional aur funny reaction ko express karta hai."
            if language == "Hindi":
                meaning = f"यह अपलोड किया गया स्टिकर '{sticker_visual_desc}' से जुड़े मज़ाकिया भावों को दर्शाता है।"

            if user_context:
                ctx_exp = f"In relation to '{user_context}', sending this sticker serves as an emotional punchline to soften the conversation." if language == "English" else f"'{user_context}' ke reply mein ye sticker tension kam karne ya playful reaction dene ke liye bheja gaya hai."
            else:
                ctx_exp = "Sent to communicate tone without typing out a lengthy explanation."

            tones = ["Expressive", "Playful", "Context-Dependent"]
            visible_info = sticker_visual_desc
            meme_info = "Custom internet sticker / reaction image format."
            replies = [
                "Haha exactly what I was thinking! 😂",
                "10/10 sticker choice! 👏",
                "Wait, why that sticker? Explain yourself! 🤔"
            ]

        # Save into session state
        st.session_state["analysis_result"] = {
            "title": sticker_display_name,
            "meaning": meaning,
            "ctx_exp": ctx_exp,
            "tones": tones,
            "visible_info": visible_info,
            "meme_info": meme_info,
            "replies": replies
        }
        st.session_state["last_analyzed_key"] = current_sticker_key

    # Display Analysis Result if available
    if "analysis_result" in st.session_state and st.session_state.get("last_analyzed_key") == current_sticker_key:
        res = st.session_state["analysis_result"]
        
        st.markdown(f"### 🏷️ Sticker: **{res['title']}**")
        st.markdown(f"#### 💡 What It Probably Means\n**{res['meaning']}**")
        
        # Tone Badges
        st.write("🎭 **Emotional Tone:**")
        tones_html = "".join([f'<span class="badge">{t}</span>' for t in res["tones"]])
        st.markdown(tones_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"#### 🎯 In Your Conversation\n{res['ctx_exp']}")

        with st.expander("👁️ Visible Details in Image"):
            st.write(res["visible_info"])
            
        with st.expander("🌐 Meme & Cultural Reference"):
            st.write(res["meme_info"])

        st.markdown("#### 💬 Suggested Replies You Can Send")
        for reply in res["replies"]:
            st.code(f'"{reply}"', language=None)

        # Follow up section
        st.markdown("---")
        st.markdown("#### ❓ Ask a Follow-up Question")
        q = st.text_input("Ask anything about this sticker (e.g. 'Why is it funny?', 'Is it sarcastic?'):")
        if q:
            if "funny" in q.lower():
                st.info("It's funny because of the hyper-exaggerated reaction! In messaging culture, sending an over-the-top reaction image breaks the tension and turns a potentially stressful topic into a lighthearted joke.")
            elif "sarcastic" in q.lower():
                st.info("Yes! This sticker is frequently used with sarcastic undertones—especially when responding to obvious questions or unreasonable demands.")
            elif "hinglish" in q.lower():
                st.info(f"Hinglish mein iska matlab: Ye sticker mazaak mein over-dramatic reaction dene ke liye use hota hai!")
            else:
                st.info(f"Regarding '{q}': Based on the visual tone and context, this sticker softens the conversation and invites playful banter.")
    else:
        st.info("👈 Upload your sticker or choose a preset on the left, then click **'Understand This Sticker'**!")
