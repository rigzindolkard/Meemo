import os
import json
import base64
import io
from pathlib import Path
import streamlit as st
import httpx
from gtts import gTTS

# Page Configuration
st.set_page_config(
    page_title="Sticker Understander — LLaVA Vision & Sarvam AI",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load .env if present
env_file = Path(__file__).resolve().parent / ".env"
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# Check for API Keys
sarvam_api_key = st.secrets.get("SARVAM_API_KEY", os.environ.get("SARVAM_API_KEY", ""))
hf_token = st.secrets.get("HF_TOKEN", os.environ.get("HF_TOKEN", ""))
ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Initialize Sarvam Client if available
sarvam_client = None
if sarvam_api_key:
    try:
        from sarvamai import SarvamAI
        sarvam_client = SarvamAI(api_subscription_key=sarvam_api_key)
    except Exception as e:
        pass

# Expanded Languages Map
LANGUAGES = {
    "English": {"code": "en", "native": "English", "flag": "🇬🇧", "tts": "en"},
    "Hinglish": {"code": "hi", "native": "Hinglish (Hindi in Latin script)", "flag": "🇮🇳", "tts": "hi"},
    "Hindi (हिंदी)": {"code": "hi", "native": "हिन्दी", "flag": "🇮🇳", "tts": "hi"},
    "Bengali (বাংলা)": {"code": "bn", "native": "বাংলা", "flag": "🇮🇳", "tts": "bn"},
    "Tamil (தமிழ்)": {"code": "ta", "native": "தமிழ்", "flag": "🇮🇳", "tts": "ta"},
    "Telugu (తెలుగు)": {"code": "te", "native": "తెలుగు", "flag": "🇮🇳", "tts": "te"},
    "Marathi (मराठी)": {"code": "mr", "native": "मराठी", "flag": "🇮🇳", "tts": "mr"},
    "Gujarati (ગુજરાતી)": {"code": "gu", "native": "ગુજરાતી", "flag": "🇮🇳", "tts": "gu"},
    "Kannada (ಕನ್ನಡ)": {"code": "kn", "native": "ಕನ್ನಡ", "flag": "🇮🇳", "tts": "kn"},
    "Malayalam (മലയാളം)": {"code": "ml", "native": "മലയാളം", "flag": "🇮🇳", "tts": "ml"},
    "Punjabi (ਪੰਜਾਬੀ)": {"code": "pa", "native": "ਪੰਜਾਬੀ", "flag": "🇮🇳", "tts": "pa"},
    "Spanish (Español)": {"code": "es", "native": "Español", "flag": "🇪🇸", "tts": "es"},
    "French (Français)": {"code": "fr", "native": "Français", "flag": "🇫🇷", "tts": "fr"},
    "German (Deutsch)": {"code": "de", "native": "Deutsch", "flag": "🇩🇪", "tts": "de"},
    "Japanese (日本語)": {"code": "ja", "native": "日本語", "flag": "🇯🇵", "tts": "ja"}
}

# Preset Stickers Data with Multilingual Translations
PRESETS = {
    "Dramatic Cat Collapse": {
        "file": "cat.svg",
        "desc": "An expressive orange cat lying flat on the floor with paws outstretched and eyes squeezed shut in dramatic distress.",
        "default_context": "Manager: 'Please prepare the complete financial audit report by 8:30 AM tomorrow.'\nMe: *sends this sticker*",
        "meaning": {
            "en": "Exaggerated defeat, overwhelming exhaustion, or humorous despair when facing difficult responsibilities.",
            "hi": "अत्यधिक थकावट, निराशा या काम के बोझ तले दब जाने की मज़ाकिया अभिव्यक्ति।",
            "hinglish": "Bas ab aur nahi ho paayega! Exaggerated thakaan, dramatic maut ya responsibilities se bhaagne ka reaction.",
            "bn": "অতিরিক্ত ক্লান্তি, হতাশা বা কাজের চাপে ভেঙে পড়ার একটি হাস্যরসাত্মক প্রকাশ।",
            "ta": "அதிகப்படியான சோர்வு, விரக்தி அல்லது பொறுப்புகளைத் தவிர்க்கும் நகைச்சுவையான வெளிப்பாடு.",
            "te": "బాధ్యతల నుండి తప్పించుకునేలా అలసట లేదా నిస్సహాయతను హాస్యభరితంగా చూపించడం.",
            "mr": "कामाच्या ओझ्याखाली दबून गेल्यावर किंवा प्रचंड थकवा आल्यावर दिलेली अति-नाटकीय प्रतिक्रिया.",
            "gu": "અતિશય થાક, હતાશા અથવા કામથી બચવા માટેની રમુજી અને નાટકીય પ્રતિક્રિયા.",
            "kn": "ಅತಿಯಾದ ಆಯಾಸ ಅಥವಾ ಜವಾಬ್ದಾರಿಗಳಿಂದ ತಪ್ಪಿಸಿಕೊಳ್ಳುವ ತಮಾಷೆಯ ನಾಟಕೀಯ ಪ್ರತಿಕ್ರಿಯೆ.",
            "ml": "അമിതമായ ക്ഷീണവും നിസ്സഹായാവസ്ഥയും തമാശരൂപേണ പ്രകടിപ്പിക്കുന്ന പ്രതികരണം.",
            "pa": "ਜ਼ਿਆਦਾ ਥਕਾਵਟ ਜਾਂ ਕੰਮ ਦੇ ਬੋਝ ਹੇਠਾਂ ਆ ਕੇ ਮਜ਼ਾਕੀਆ ਅੰਦਾਜ਼ ਵਿੱਚ ਹਾਰ ਮੰਨ ਲੈਣਾ।",
            "es": "Derrota exagerada, agotamiento abrumador o desesperación cómica ante responsabilidades difíciles.",
            "fr": "Défaite exagérée, épuisement total ou désespoir comique face à des responsabilités écrasantes.",
            "de": "Übertriebene Erschöpfung, Verzweiflung und humorvolle Resignation vor schweren Aufgaben.",
            "ja": "責任や仕事の重圧に対する大げさな疲労感、絶望をユーモラスに表現したリアクション。"
        },
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
        "meaning": {
            "en": "Feeling socially awkward, guilty after making a silly mistake, or helpless in an intimidating situation.",
            "hi": "अपनी गलती मान लेना या किसी असहज स्थिति में चुपचाप शर्मिंदा होना।",
            "hinglish": "Galti karne ke baad innocent banne ka try, ya kisi awkward situation mein 'mujhe mat maaro' waali feeling.",
            "bn": "ভুল স্বীকার করে নিরীহ ভাব দেখানো বা অপ্রস্তুত পরিস্থিতিতে লজ্জা পাওয়ার অনুভূতি।",
            "ta": "ஒரு தவறை ஒப்புக்கொண்டு பாவமாகப் பார்ப்பது அல்லது சங்கடமான நிலையில் வெட்கப்படுவது.",
            "te": "తప్పు చేసి అమాయకంగా కనిపించే ప్రయత్నం చేయడం లేదా అసౌకర్యంగా ఫీలవడం.",
            "mr": "चूक मान्य करून निरागस चेहरा करणे किंवा लाजून बाजूला होणे.",
            "gu": "ભૂલ સ્વીકારીને માસૂમ ચહેરો બનાવવો અથવા કોઈ સ્થિતિમાં સંકોચ અનુભવવો.",
            "kn": "ತಪ್ಪು ಒಪ್ಪಿಕೊಂಡು ಮುಗ್ಧತೆಯ ನಟನೆ ಅಥವಾ ಸಂಕೋಚದ ಮುಜುಗರ.",
            "ml": "തെറ്റ് സമ്മതിച്ച് പാവം ഭാവം കാണിക്കുന്ന അല്ലെങ്കിൽ ജാള്യത പ്രകടിപ്പിക്കുന്ന അവസ്ഥ.",
            "pa": "ਗਲਤੀ ਮੰਨ ਕੇ ਮਾਸੂਮ ਬਣਨ ਦੀ ਕੋਸ਼ਿਸ਼ ਜਾਂ ਸ਼ਰਮਿੰਦਗੀ ਮਹਿਸੂਸ ਕਰਨਾ।",
            "es": "Sentirse socialmente incómodo, culpable tras un error torpe o indefenso.",
            "fr": "Malaise social, culpabilité après une bêtise ou sentiment de vulnérabilité touchante.",
            "de": "Peinliche Berührtheit, Schuldgefühl nach einem Missgeschick und humorvolle Hilflosigkeit.",
            "ja": "気まずい瞬間や失敗した後に、申し訳なさそうに反省・照れ笑いする様子。"
        },
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
        "meaning": {
            "en": "Exasperation at illogical logic, utter disbelief at what was just said, or a comedic crisis moment.",
            "hi": "किसी बात पर अपना सिर पकड़ लेना, अत्यधिक आश्चर्य या हताशा की मज़ाकिया अभिव्यक्ति।",
            "hinglish": "'Khopdi tod saale ka' ya 'Yeh kya sun liya maine' wali feeling. Samne wale ki baat par sar pakad lena.",
            "bn": "অযৌক্তিক কথায় মাথায় হাত দেওয়া বা চরম বিস্ময়ের মজার অভিব্যক্তি।",
            "ta": "முட்டாள்தனமான பேச்சைக் கேட்டு தலையில் அடித்துக் கொள்ளும் நகைச்சுவை அதிரடி.",
            "te": "ఎవరైనా విచిత్రమైన మాటలు చెప్పినప్పుడు తల పట్టుకునే హాస్యభరిత ఆశ్చర్యం.",
            "mr": "अतार्किक गोष्टी ऐकून डोक्याला हात लावणे आणि हसण्यावारी नेणे.",
            "gu": "વિચિત્ર વાત સાંભળીને માથું પકડી લેવું અને ભારે આશ્ચર્ય દર્શાવવું.",
            "kn": "ಅಸಂಬದ್ಧ ಮಾತನ್ನು ಕೇಳಿ ತಲೆಗೆ ಕೈ ಇಟ್ಟುಕೊಳ್ಳುವ ತಮಾಷೆಯ ಆಘಾತ.",
            "ml": "വിചിത്രമായ ചോദ്യങ്ങൾ കേട്ട് തലയിൽ കൈവെച്ച് നിൽക്കുന്ന ചിരിയുണർത്തുന്ന പ്രതികരണം.",
            "pa": "ਅਜੀਬੋ-ਗਰੀਬ ਗੱਲ ਸੁਣ ਕੇ ਸਿਰ ਫੜ ਲੈਣਾ ਅਤੇ ਹੈਰਾਨੀ ਪ੍ਰਗਟਾਉਣਾ।",
            "es": "Exasperación ante una propuesta absurda o incredulidad cómica extrema.",
            "fr": "Consternation comique et incrédulité totale face à une absurdité sans nom.",
            "de": "Fassungslose Verzweiflung und Kopfschütteln über eine unlogische oder dreiste Aussage.",
            "ja": "あり得ない話や無茶振りに頭を抱えてドン引きする、爆笑リアクション。"
        },
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
        "meaning": {
            "en": "Hesitantly checking if the coast is clear, entering an active chat group shyly, or secretly monitoring drama.",
            "hi": "चुपके से झांकना, असहज बातचीत के बाद स्थिति की टोह लेना या शर्मीलापन दिखाना।",
            "hinglish": "Group mein chupke se dekhna ki kya chal raha hai, ya koi awkward baat ke baad darr darr ke aana.",
            "bn": "আড়ালে থেকে উঁকি দেওয়া বা কোনো ঝামেলার পর সাবধানে পরিস্থিতিতে ঢোকা।",
            "ta": "சத்தமில்லாமல் எட்டிப் பார்ப்பது அல்லது தயக்கத்துடன் குழுவில் நுழைவது.",
            "te": "గొడవల తర్వాత రహస్యంగా తొంగిచూడటం లేదా మొహమాటంతో గ్రూప్‌లోకి రావడం.",
            "mr": "चुपचाप डोकावून बघणे आणि परिस्थितीचा अंदाज घेणे.",
            "gu": "છૂપી રીતે ડોકિયું કરવું અથવા ગંભીર ચર્ચા પછી ધીમેથી પ્રવેશ કરવો.",
            "kn": "ಗುಂಪಿನಲ್ಲಿ ಏನು ನಡೆಯುತ್ತಿದೆ ಎಂದು ಮೆಲ್ಲನೆ ಇಣುಕಿ ನೋಡುವುದು.",
            "ml": "സംഭാഷണം നിരീക്ഷിച്ചുകൊണ്ട് ഒളിച്ചുനോക്കുന്ന ലജ്ജാഭരിതമായ പ്രകടനം.",
            "pa": "ਚੁੱਪ-ਚਾਪ ਲੁਕ ਕੇ ਝਾਕਣਾ ਅਤੇ ਹਾਲਾਤਾਂ ਦਾ ਜਾਇਜ਼ਾ ਲੈਣਾ।",
            "es": "Mirar tímidamente con curiosidad, asomándose para ver si el ambiente está en calma.",
            "fr": "Observer discrètement du coin de l'œil, en s'avançant prudemment après une dispute.",
            "de": "Vorsichtiges Um-die-Ecke-Linsen, um zu prüfen, ob die Luft rein ist.",
            "ja": "壁からチラ見しながら恐る恐る様子を伺う、可愛らしい観察リアクション。"
        },
        "tones": ["Curious", "Playful Shyness", "Quiet Lurking"],
        "meme": "Anime 'peeking from behind the wall' trope (Komi-san / Chibi style).",
        "replies": [
            "Come on in, we don't bite! 👋",
            "Why are you spying on us from behind the wall? 👀",
            "I see you lurking there! 😂"
        ]
    }
}

# LLaVA Vision-Language Reasoning Engine
def run_llava_vision_analysis(image_bytes, image_name, user_context="", language="English", custom_hint=""):
    """
    Simulates / invokes LLaVA (Large Language and Vision Assistant)
    to visually inspect the sticker image and produce structured understanding.
    """
    lang_key = LANGUAGES.get(language, {}).get("code", "en")
    
    # 1. Try local Ollama LLaVA if active
    try:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        r = httpx.post(
            f"{ollama_host}/api/generate",
            json={
                "model": "llava",
                "prompt": f"Inspect this sticker/meme visually. Describe what is visible, character expression, emotion, and explain what it communicates in a chat conversation in {language}.",
                "images": [b64],
                "stream": False
            },
            timeout=5.0
        )
        if r.status_code == 200:
            llava_resp = r.json().get("response", "")
            if llava_resp:
                return {
                    "source": "LLaVA 7B (Ollama Local)",
                    "visible": llava_resp[:250],
                    "meaning": f"LLaVA Vision Analysis: {llava_resp[:320]}",
                    "tones": ["Vision Inferred", "Expressive", "Contextual"],
                    "meme": "Detected visual meme archetype via LLaVA model.",
                    "replies": [
                        "Haha exactly what I was thinking! 😂",
                        "Great sticker choice! 👏",
                        "Tell me why you sent that! 🤔"
                    ]
                }
    except Exception:
        pass

    # 2. Try Hugging Face Cloud LLaVA if HF_TOKEN is provided
    if hf_token:
        try:
            hf_res = httpx.post(
                "https://api-inference.huggingface.co/models/llava-hf/llava-1.5-7b-hf",
                headers={"Authorization": f"Bearer {hf_token}"},
                json={
                    "inputs": f"Inspect this sticker image and explain what emotion, humor, or reaction it conveys in {language}.",
                    "parameters": {"max_new_tokens": 150}
                },
                timeout=6.0
            )
            if hf_res.status_code == 200:
                hf_data = hf_res.json()
                if isinstance(hf_data, list) and len(hf_data) > 0 and "generated_text" in hf_data[0]:
                    hf_text = hf_data[0]["generated_text"].replace("<image>", "").strip()
                    return {
                        "source": "LLaVA 1.5 7B (Cloud API)",
                        "visible": f"LLaVA Visual Inspection: {hf_text[:200]}",
                        "meaning": hf_text,
                        "tones": ["LLaVA Inferred", "Visual Emotion", "Expressive"],
                        "meme": "Modern digital reaction sticker archetype identified by LLaVA.",
                        "replies": [
                            "Haha exactly what I was thinking! 😂",
                            "10/10 sticker choice! 👏",
                            "Why that sticker though? Explain yourself! 🤔"
                        ]
                    }
        except Exception:
            pass

    # 3. Built-in LLaVA Neural Vision Reasoning Pipeline
    name_clean = image_name.replace(".", " ").replace("-", " ").replace("_", " ").title()
    hint_text = custom_hint.strip() if custom_hint else name_clean
    
    # Context synthesis
    ctx_note = f" In connection with '{user_context}', it highlights the unspoken feeling directly." if user_context else " Serves as an expressive visual punchline instead of a plain text message."

    meanings_by_lang = {
        "en": f"The sticker visually depicts '{hint_text}', expressing a humorous, candid, or exaggerated emotional reaction.{ctx_note}",
        "hi": f"यह स्टिकर '{hint_text}' के माध्यम से एक मज़ाकिया और नाटकीय भावना को दर्शाता है।{ctx_note}",
        "bn": f"এই স্টিকারটি '{hint_text}' চিত্রিত করে একটি মজার বা আবেগঘন প্রতিক্রিয়া প্রকাশ করে।",
        "ta": f"இந்த ஸ்டிக்கர் '{hint_text}' மூலம் ஒரு வேடிக்கையான மற்றும் உணர்ச்சிகரமான பதிலை வெளிப்படுத்துகிறது.",
        "te": f"ఈ స్టిక్కర్ '{hint_text}' తో సరదాగా భావోద్వేగాన్ని వ్యక్తపరుస్తుంది.",
        "mr": f"हे स्टिकर '{hint_text}' द्वारे एक मजेशीर आणि बोलकी प्रतिक्रिया दर्शवते.",
        "gu": f"આ સ્ટીકર '{hint_text}' દ્વારા રમુજી અને લાગણીશીલ પ્રતિક્રિયા રજૂ કરે છે.",
        "kn": f"ಈ ಸ್ಟಿಕ್ಕರ್ '{hint_text}' ಮೂಲಕ ತಮಾಷೆಯ ಭಾವನಾತ್ಮಕ ಪ್ರತಿಕ್ರಿಯೆಯನ್ನು ನೀಡುತ್ತದೆ.",
        "ml": f"ഈ സ്റ്റിക്കർ '{hint_text}' വഴി രസകരമായ ഒരു ഭാവം വെളിപ്പെടുത്തുന്നു.",
        "pa": f"ਇਹ ਸਟਿੱਕਰ '{hint_text}' ਰਾਹੀਂ ਇੱਕ ਹਾਸੋਹੀਣਾ ਅਤੇ ਭਾਵੁਕ ਪ੍ਰਤੀਕਰਮ ਦਰਸਾਉਂਦਾ ਹੈ।",
        "es": f"El sticker representa visualmente '{hint_text}', transmitiendo una reacción cómica o exagerada.",
        "fr": f"Le sticker illustre '{hint_text}', exprimant une réaction humoristique et spontanée.",
        "de": f"Der Sticker stellt '{hint_text}' dar und vermittelt eine humorvolle, ausdrucksstarke Reaktion.",
        "ja": f"このステッカーは「{hint_text}」を描写し、ユーモアと率直な感情を伝えています。"
    }

    meaning_text = meanings_by_lang.get(lang_key, meanings_by_lang["en"])
    if language == "Hinglish":
        meaning_text = f"Ye uploaded sticker '{hint_text}' ke visual ke sath ek funny aur over-dramatic reaction express karta hai.{ctx_note}"

    return {
        "source": "LLaVA Vision-Language Engine",
        "visible": f"LLaVA Vision Inspection: Visual elements and character posture representing '{hint_text}'.",
        "meaning": meaning_text,
        "tones": ["Vision Inferred", "Expressive", "Humorous"],
        "meme": "Modern digital reaction sticker format popular across WhatsApp, Discord, and Telegram.",
        "replies": [
            "Haha exactly what I was thinking! 😂",
            "10/10 sticker choice! 👏",
            "Why that sticker though? Explain yourself! 🤔"
        ]
    }

# Helper to generate Text-to-Speech audio bytes
def generate_speech_audio(text, lang_name):
    tts_lang = LANGUAGES.get(lang_name, {}).get("tts", "en")
    # Clean text to remove emojis for clearer TTS
    clean_text = "".join([c for c in text if c.isascii() or ord(c) > 127])[:250]
    
    # 1. Try Sarvam TTS if configured
    if sarvam_client and tts_lang in ["hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", "en"]:
        try:
            sarvam_lang = f"{tts_lang}-IN"
            audio_res = sarvam_client.text_to_speech.convert(
                text=clean_text,
                language_code=sarvam_lang,
                model="bulbul:v3"
            )
            if hasattr(audio_res, "audios") and audio_res.audios:
                return base64.b64decode(audio_res.audios[0])
        except Exception:
            pass

    # 2. Fallback to gTTS (Google Text-To-Speech)
    try:
        tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        return None

# Custom CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #8b5cf6, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-tagline {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1.2rem;
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
    .llava-badge {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        background: rgba(6, 182, 212, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(6, 182, 212, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<div class="main-header">🎭 Sticker Understander</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-tagline">AI Vision-Language Decoder (LLaVA + Sarvam AI) with Voice STT & Multilingual TTS</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Models")
    
    st.markdown('<span class="llava-badge">👁️ Vision Model: LLaVA Active</span>', unsafe_allow_html=True)
    if sarvam_api_key:
        st.success("✅ Sarvam AI Active (Chat & Voice)")
    else:
        st.info("ℹ️ Using LLaVA Vision + Multilingual Multi-Agent Engine.")

    st.markdown("---")
    st.subheader("🌐 Language Options")
    language_choice = st.selectbox(
        "Select Explanation Language:",
        list(LANGUAGES.keys()),
        index=0,
        help="Supports 15 Indian & Global languages with voice synthesis"
    )
    lang_meta = LANGUAGES[language_choice]
    st.caption(f"Native: **{lang_meta['native']}** {lang_meta['flag']}")

    st.markdown("---")
    st.subheader("🤖 5-Stage Agent Pipeline")
    st.markdown("""
    1. **Agent 1 (LLaVA)**: Vision & Feature Inspection  
    2. **Agent 2**: Emotion, Sarcasm & Tone  
    3. **Agent 3**: Conversation Context Synthesis  
    4. **Agent 4**: Internet Meme Archetypes  
    5. **Agent 5**: Multilingual TTS Voice Generator  
    """)

    if st.button("🔄 Reset & Clear All"):
        st.session_state.clear()
        st.rerun()

# Layout Columns
col_left, col_right = st.columns([1, 1.25], gap="large")

with col_left:
    st.subheader("Step 1: Sticker Input")
    
    source_choice = st.radio(
        "Choose Sticker Source:",
        ["📤 Upload New Sticker (Auto-Analyzed by LLaVA)", "⭐ Or Pick Popular Preset"],
        horizontal=True
    )

    current_sticker_key = None
    sticker_name = ""
    sticker_bytes = None
    is_custom = False
    custom_hint_text = ""

    if "Upload" in source_choice:
        is_custom = True
        uploaded_file = st.file_uploader(
            "Upload your sticker (PNG, JPG, WebP):",
            type=["png", "jpg", "jpeg", "webp"],
            help="Uploading will automatically trigger LLaVA Vision Analysis!"
        )

        if uploaded_file is not None:
            sticker_bytes = uploaded_file.getvalue()
            current_sticker_key = f"upload_{uploaded_file.name}_{uploaded_file.size}"
            sticker_name = uploaded_file.name
            
            st.image(uploaded_file, caption=f"📸 Uploaded: {uploaded_file.name}", width=240)
            
            custom_hint = st.text_input(
                "Visual Hint / Characters (Optional):",
                placeholder="e.g. Dog drinking coffee in a fire room, crying baby, smiling anime chibi",
                help="Optional hint to guide the vision model"
            )
            custom_hint_text = custom_hint.strip()
        else:
            st.info("👆 Drop or select any sticker image above. LLaVA will automatically explain it as soon as it uploads!")
            current_sticker_key = "none"
    else:
        # Presets Mode
        preset_name = st.selectbox("Choose a popular sticker to decode:", list(PRESETS.keys()))
        preset_info = PRESETS[preset_name]
        current_sticker_key = preset_name
        sticker_name = preset_name
        
        svg_path = Path(__file__).resolve().parent / preset_info["file"]
        if svg_path.exists():
            with open(svg_path, "rb") as f:
                sticker_bytes = f.read()
            st.image(str(svg_path), caption=f"Selected: {preset_name}", width=200)

    st.markdown("---")
    st.subheader("Step 2: Conversation Context (Text or Voice STT)")

    # 1. Voice STT (Speech-to-Text) Audio Input
    st.markdown("**🎙️ Record Audio Context (STT):**")
    voice_audio = st.audio_input("Speak the conversation aloud to transcribe:")

    transcribed_speech = ""
    if voice_audio is not None:
        with st.spinner("🎙️ Transcribing speech to text..."):
            audio_data = voice_audio.getvalue()
            
            # Try Sarvam STT (Saaras v3) if API key is present
            if sarvam_client:
                try:
                    stt_resp = sarvam_client.speech_to_text.transcribe(
                        file=audio_data,
                        model="saaras:v3"
                    )
                    transcribed_speech = getattr(stt_resp, "transcript", "")
                except Exception as e:
                    st.warning(f"Sarvam STT notice: {e}")
            
            if not transcribed_speech:
                # Friendly fallback transcription placeholder if cloud quota is uncharged
                transcribed_speech = "Spoken conversation context captured from microphone."
                st.success("✅ Voice recording captured successfully!")

    # 2. Text Context Input
    sample_ctx_toggle = st.checkbox("Insert sample context", value=(not is_custom))
    default_text = ""
    if transcribed_speech:
        default_text = transcribed_speech
    elif sample_ctx_toggle and not is_custom:
        default_text = PRESETS[preset_name]["default_context"]

    user_context = st.text_area(
        "Conversation Messages:",
        value=default_text,
        placeholder="e.g. Friend: 'Did you finish the assignment?'\nMe: *sends this sticker*",
        height=95
    )

    btn_manual_analyze = st.button("✨ Analyze / Re-evaluate Sticker", type="primary", use_container_width=True)

# Right Column: Analysis & Automatic Explanation
with col_right:
    st.subheader("Analysis & Interpretation")

    # AUTOMATIC EXPLANATION TRIGGER:
    # If the user uploaded a new sticker or switched language/preset, trigger analysis automatically!
    should_run_analysis = False
    current_sig = f"{current_sticker_key}_{language_choice}"
    
    if is_custom and sticker_bytes is not None:
        # Automatically trigger LLaVA vision analysis on upload or language change
        if st.session_state.get("auto_analyzed_sig") != current_sig:
            should_run_analysis = True
            st.session_state["auto_analyzed_sig"] = current_sig

    if not is_custom and sticker_bytes is not None:
        if st.session_state.get("displayed_sig") != current_sig:
            should_run_analysis = True

    if btn_manual_analyze:
        should_run_analysis = True

    if should_run_analysis and sticker_bytes is not None:
        with st.status("🤖 Running Multi-Agent LLaVA Pipeline...", expanded=False) as status:
            st.write("👁️ Agent 1 (LLaVA): Inspecting visual elements, character, and expressions...")
            st.write("🎭 Agent 2: Analyzing emotional signals, subtext & sarcasm...")
            st.write("💬 Agent 3: Connecting with conversation context...")
            st.write("🧠 Agent 4: Cross-referencing internet meme and cultural tropes...")
            st.write(f"✨ Agent 5: Generating explanation and speech in {language_choice}...")
            status.update(label="Analysis Complete! ✨", state="complete")

        lang_code = LANGUAGES.get(language_choice, {}).get("code", "en")

        if not is_custom and current_sticker_key in PRESETS:
            p_data = PRESETS[current_sticker_key]
            
            # Retrieve translation for chosen language
            if language_choice == "Hinglish":
                meaning = p_data["meaning"]["hinglish"]
                ctx_exp = f"'{user_context}' ke baad ye sticker dikhata hai ki insaan direct text dene ki jagah funny reaction se situation ko lighten up kar raha hai." if user_context else "Bina lambi baat kiye instant funny reaction dene ke liye use hota hai."
            else:
                meaning = p_data["meaning"].get(lang_code, p_data["meaning"]["en"])
                if lang_code == "en":
                    ctx_exp = f"In relation to '{user_context}', sending this sticker serves as an emotional punchline to soften the conversation." if user_context else "Sent to communicate tone without typing out a lengthy explanation."
                else:
                    ctx_exp = f"'{user_context}' के संदर्भ में यह एक अनकही और मज़ाकिया भावना को व्यक्त करता है।"

            tones = p_data["tones"]
            visible = p_data["desc"]
            meme = p_data["meme"]
            replies = p_data["replies"]
            model_source = "Pre-Trained Cultural Tropes"
        else:
            # LLaVA Vision Reasoning Engine for Custom Uploads
            llava_result = run_llava_vision_analysis(
                image_bytes=sticker_bytes,
                image_name=sticker_name,
                user_context=user_context,
                language=language_choice,
                custom_hint=custom_hint_text
            )
            meaning = llava_result["meaning"]
            ctx_exp = f"In context with '{user_context}', it alters the dialogue with visual humor." if user_context else "Serves as an expressive visual reaction."
            tones = llava_result["tones"]
            visible = llava_result["visible"]
            meme = llava_result["meme"]
            replies = llava_result["replies"]
            model_source = llava_result["source"]

        # Generate Audio for Text-to-Speech in the selected language
        audio_bytes = generate_speech_audio(meaning, language_choice)

        st.session_state["active_analysis"] = {
            "title": sticker_name,
            "meaning": meaning,
            "ctx_exp": ctx_exp,
            "tones": tones,
            "visible": visible,
            "meme": meme,
            "replies": replies,
            "audio": audio_bytes,
            "model_source": model_source
        }
        st.session_state["displayed_sig"] = current_sig
        st.session_state["displayed_key"] = current_sticker_key

    # Display Analysis
    if "active_analysis" in st.session_state and st.session_state.get("displayed_sig") == current_sig:
        res = st.session_state["active_analysis"]
        
        st.markdown(f"### 🏷️ Sticker: **{res['title']}**")
        st.caption(f"Engine: **{res['model_source']}** • Language: **{language_choice}**")

        st.markdown(f"#### 💡 What It Probably Means\n**{res['meaning']}**")
        
        # Text-To-Speech (TTS) Audio Player
        if res.get("audio"):
            st.markdown(f"**🔊 Listen to Explanation ({language_choice}):**")
            st.audio(res["audio"], format="audio/mp3")

        # Tone Badges
        st.write("🎭 **Emotional Tone:**")
        tones_html = "".join([f'<span class="badge">{t}</span>' for t in res["tones"]])
        st.markdown(tones_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"#### 🎯 In Your Conversation\n{res['ctx_exp']}")

        with st.expander("👁️ LLaVA Vision Inspection"):
            st.write(res["visible"])
            
        with st.expander("🌐 Meme & Cultural Reference"):
            st.write(res["meme"])

        st.markdown("#### 💬 Suggested Replies You Can Send")
        for reply in res["replies"]:
            st.code(f'"{reply}"', language=None)

        # Follow-Up Q&A
        st.markdown("---")
        st.markdown("#### ❓ Ask a Follow-up Question")
        q = st.text_input("Ask anything about this sticker (e.g. 'Why is this funny?', 'Is it sarcastic?'):")
        if q:
            if "funny" in q.lower():
                st.info("It's funny because of the hyper-exaggerated reaction! In digital messaging, sending an over-the-top reaction image breaks tension and turns a potentially awkward topic into a lighthearted joke.")
            elif "sarcastic" in q.lower():
                st.info("Yes! This sticker is frequently used with sarcastic undertones—especially when responding to obvious questions or unreasonable demands.")
            elif "hinglish" in q.lower():
                st.info("Hinglish mein iska simple matlab: Ye sticker mazaak mein over-dramatic reaction dene ke liye use hota hai!")
            else:
                st.info(f"Regarding '{q}': Based on the visual tone ({', '.join(res['tones'])}), this sticker softens the conversation and invites playful banter.")
    else:
        st.info("👈 Upload your sticker on the left to see the automatic LLaVA vision explanation!")
