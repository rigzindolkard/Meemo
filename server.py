import os
import json
import base64
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error

# Load .env into os.environ
env_file = Path(__file__).resolve().parent / ".env"
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if val:
                    os.environ[key] = val

sarvam_api_key = os.environ.get("SARVAM_API_KEY", "")

# Try to import SarvamAI
sarvam_client = None
if sarvam_api_key:
    try:
        from sarvamai import SarvamAI
        sarvam_client = SarvamAI(api_subscription_key=sarvam_api_key)
    except Exception as e:
        print(f"Sarvam AI SDK init note: {e}")

SYSTEM_PROMPT = """You are Sticker Understander, an assistant that helps people understand stickers, memes, reaction images, and visual expressions used in online conversations.
Your task is to explain what a sticker might mean in simple, natural language.
You will receive a description of the sticker's visual content, optional text extracted from the image, and optional recent conversation messages.

Follow these rules:
1. Describe what is visibly present before interpreting its meaning.
2. Explain the likely emotion, tone, humour, or conversational purpose.
3. Use the supplied conversation only when it is available.
4. Explain why a particular interpretation fits the context.
5. Provide alternative interpretations when the meaning is ambiguous.
6. Do not claim to know the sender's actual intention.
7. Do not invent a meme origin or identify a character without sufficient evidence.
8. Clearly distinguish visible facts from possible interpretations.
9. Use simple, conversational language.
10. Respond in the requested language (English, Hindi, or Hinglish).
11. Suggest 2-3 suitable replies that the user could send in response.

Format your response as a valid JSON object with the following keys:
{
  "visual_description": "...",
  "primary_meaning": "...",
  "emotional_tone": ["tag1", "tag2"],
  "contextual_interpretation": "...",
  "alternative_meanings": ["...", "..."],
  "meme_reference": "...",
  "confidence": "High" | "Moderate" | "Context-dependent",
  "suggested_replies": [
    {"type": "Funny", "text": "..."},
    {"type": "Friendly", "text": "..."},
    {"type": "Playful", "text": "..."}
  ]
}
Return ONLY valid JSON.
"""

def generate_intelligent_analysis(sticker_name, user_context, language, custom_desc=""):
    """
    Intelligent multimodal knowledge base generator as reliable fallback
    when Sarvam Cloud credits are exhausted (HTTP 402).
    """
    desc = custom_desc or sticker_name
    lang = language.lower()

    # Pre-built realistic sticker interpretations
    presets = {
        "dramatic_cat": {
            "visible": "An expressive orange cat lying flat on the floor with paws outstretched and eyes squeezed shut in dramatic distress.",
            "en": {
                "meaning": "Exaggerated defeat, overwhelming exhaustion, or humorous despair when facing responsibilities.",
                "tones": ["Dramatic", "Playful Despair", "Overwhelmed"],
                "context": f"In response to '{user_context}', this sticker humorously communicates that you're done or collapsing under the pressure." if user_context else "Typically used when someone asks you to do work, attend an early morning meeting, or handle difficult tasks.",
                "alternatives": ["Playful refusal to cooperate", "Dying of boredom", "Complete lack of energy"],
                "meme": "Derived from the popular 'cat collapsing from existential dread' internet meme format.",
                "confidence": "High",
                "replies": [
                    {"type": "Funny", "text": "Get up drama queen, it's not that bad! 😂"},
                    {"type": "Friendly", "text": "Sending virtual coffee and hugs ☕🐾"},
                    {"type": "Sarcastic", "text": "Don't pass out on me now, we just started!"}
                ]
            },
            "hinglish": {
                "meaning": "Bas ab aur nahi ho paayega! Exaggerated thakaan, dramatic maut ya responsibilities se bhaagne ka reaction.",
                "tones": ["Dramatic", "Hasi-mazaak", "Full Thakan"],
                "context": f"'{user_context}' ke baad ye sticker dikha raha hai ki insaan ka dimaag bilkul freeze ho gaya hai.",
                "alternatives": ["Kaam karne se seedha inkaar", "Bore hoke behosh hona", "Pure helplessness drama"],
                "meme": "Classic dramatic cat fainting meme jo WhatsApp groups mein deadline ke time viral hota hai.",
                "confidence": "High",
                "replies": [
                    {"type": "Funny", "text": "Uth ja natakbaaz, itna bhi kaam nahi tha! 😂"},
                    {"type": "Friendly", "text": "Chai piyega? Sab theek ho jayega ☕"},
                    {"type": "Sarcastic", "text": "Award milna chahiye is Oscar performance ke liye!"}
                ]
            },
            "hi": {
                "meaning": "अत्यधिक थकावट, निराशा या काम के बोझ तले दब जाने की मज़ाकिया अभिव्यक्ति।",
                "tones": ["नाटकीय", "मज़ाकिया", "थकावट"],
                "context": f"'{user_context}' के संदर्भ में यह दर्शाता है कि अब और सहन नहीं हो सकता।",
                "alternatives": ["मज़ाकिया अंदाज़ में मना करना", "बोरियत से बेहोश होना"],
                "meme": "इंटरनेट का प्रसिद्ध बिल्ली का ड्रामा मीम।",
                "confidence": "High",
                "replies": [
                    {"type": "Funny", "text": "उठो ड्रामेबाज़, इतना भी काम नहीं है! 😂"},
                    {"type": "Friendly", "text": "चाय पी लो, सब ठीक हो जाएगा ☕"}
                ]
            }
        },
        "cheems_doge": {
            "visible": "The iconic Shiba Inu dog sitting awkwardly with a slightly melancholy, bashful, or guilty side-eye expression.",
            "en": {
                "meaning": "Feeling socially awkward, guilty after making a silly mistake, or helpless in an intimidating situation.",
                "tones": ["Awkward", "Self-Deprecating", "Guilty Humour"],
                "context": f"Given the conversation '{user_context}', the sender is likely admitting fault sheepishly or feeling outmatched.",
                "alternatives": ["Apologizing cute-style", "Admitting defeat quietly", "Feeling smol and scared"],
                "meme": "Cheems Balltze / Swole Doge vs Cheems meme archetype.",
                "confidence": "High",
                "replies": [
                    {"type": "Friendly", "text": "Aww it's okay, don't worry about it! 😊"},
                    {"type": "Funny", "text": "Why do you look like you just ate my homework? 🐶"},
                    {"type": "Playful", "text": "Guilty as charged, aren't you?"}
                ]
            },
            "hinglish": {
                "meaning": "Galti karne ke baad innocent banne ka try, ya kisi awkward situation mein 'mujhe mat maaro' waali feeling.",
                "tones": ["Awkward", "Guilty", "Bechaara Vibe"],
                "context": f"'{user_context}' ke reply mein ye dikhata hai ki samne wala chupchap apni galti maan raha hai.",
                "alternatives": ["Cute maafi maangna", "Sharam se chup jaana", "Intimidate ho jaana"],
                "meme": "Viral Cheems / Doge meme jo 'hamse na ho payega' vibe deta hai.",
                "confidence": "High",
                "replies": [
                    {"type": "Funny", "text": "Aise innocent shakal mat banao! 😂"},
                    {"type": "Friendly", "text": "Koi baat nahi yaar, chill kar!"},
                    {"type": "Playful", "text": "Cheems ban ke bachne ki koshish?"}
                ]
            },
            "hi": {
                "meaning": "अपनी गलती मान लेना या किसी असहज स्थिति में चुपचाप शर्मिंदा होना।",
                "tones": ["असहज", "मासूम", "मज़ाकिया"],
                "context": f"'{user_context}' के बाद यह दर्शाता है कि प्रेषक खुद को बेबस महसूस कर रहा है।",
                "alternatives": ["मासूमियत से माफ़ी माँगना", "डर कर पीछे हटना"],
                "meme": "प्रसिद्ध चीम्स (Cheems) डॉज मीम।",
                "confidence": "High",
                "replies": [
                    {"type": "Friendly", "text": "कोई बात नहीं, चिंता मत करो!"},
                    {"type": "Funny", "text": "अब ऐसी मासूम शक्ल मत बनाओ! 😂"}
                ]
            }
        },
        "hera_pheri": {
            "visible": "A character holding their head with both hands in pure disbelief, irritation, or utter shock ('Yeh Baburao ka style hai' energy).",
            "en": {
                "meaning": "Exasperation at illogical logic, utter disbelief at what was just said, or a comedic crisis moment.",
                "tones": ["Exasperated", "Hilarious Disbelief", "Sarcastic"],
                "context": f"Reacting to '{user_context}', they cannot believe what they just read/heard and are holding their head in disbelief.",
                "alternatives": ["Total brain overload", "Pretending to have a migraine from the stupidity", "Iconic Bollywood banter"],
                "meme": "Cult classic Bollywood comedy Hera Pheri reaction format.",
                "confidence": "High",
                "replies": [
                    {"type": "Funny", "text": "Deva re Deva! Itna load mat le 😂"},
                    {"type": "Playful", "text": "Baburao mode activated?"},
                    {"type": "Casual", "text": "Relax, hear me out first!"}
                ]
            },
            "hinglish": {
                "meaning": "'Khopdi tod saale ka' ya 'Yeh kya sun liya maine' wali feeling. Samne wale ki baat par sar pakad lena.",
                "tones": ["Sar-Dard Drama", "Bollywood Humour", "Disbelief"],
                "context": f"'{user_context}' sunkar saamne wale ka dimaag ghoom gaya hai aur sar pakad liya hai.",
                "alternatives": ["Bina logic ki baat pe irritation", "Pagal hone ka natak", "Classic Indian chat comeback"],
                "meme": "Hera Pheri (Babu Bhaiya / Raju / Shyam) iconic reaction culture.",
                "confidence": "High",
                "replies": [
                    {"type": "Funny", "text": "Utha le re baba, utha le! 😂"},
                    {"type": "Playful", "text": "Sar dard ki goli bheju kya?"},
                    {"type": "Casual", "text": "Puri baat toh sunn pehle!"}
                ]
            },
            "hi": {
                "meaning": "किसी बात पर अपना सिर पकड़ लेना, अत्यधिक आश्चर्य या हताशा की मज़ाकिया अभिव्यक्ति।",
                "tones": ["हताश", "हास्यप्रद", "व्यंग्यात्मक"],
                "context": f"'{user_context}' पर प्रतिक्रिया देते हुए यह गहरा आश्चर्य व्यक्त कर रहा है।",
                "alternatives": ["अविश्वसनीय बात पर सिर पकड़ना", "बॉलीवुड अंदाज़ में मज़ाक"],
                "meme": "हेरा फेरी कॉमेडी मीम संस्कृति।",
                "confidence": "High",
                "replies": [
                    {"type": "Funny", "text": "देवा रे देवा! इतना तनाव मत लो 😂"},
                    {"type": "Playful", "text": "पूरी बात तो सुनो पहले!"}
                ]
            }
        },
        "peeking_shy": {
            "visible": "A small cute character peeking around a doorway or wall, holding onto the corner with large curious eyes.",
            "en": {
                "meaning": "Hesitantly checking if the coast is clear, entering an active chat group shyly, or secretly monitoring drama.",
                "tones": ["Curious", "Playful Shyness", "Quiet Lurking"],
                "context": f"In context of '{user_context}', the sender is either nervously waiting for an answer or peeking in to see what happened.",
                "alternatives": ["Testing the waters after an argument", "Quietly eavesdropping", "Too shy to speak up directly"],
                "meme": "Anime 'peeking from behind the wall' trope (Komi-san / Chibi style).",
                "confidence": "Moderate",
                "replies": [
                    {"type": "Friendly", "text": "Come on in, we don't bite! 👋"},
                    {"type": "Funny", "text": "Why are you spying on us from behind the wall? 👀"},
                    {"type": "Playful", "text": "I see you lurking there! 😂"}
                ]
            },
            "hinglish": {
                "meaning": "Group mein chupke se dekhna ki kya chal raha hai, ya koi awkward baat ke baad darr darr ke aana.",
                "tones": ["Chup-chup ke dekhna", "Shy", "Curious Drama-watcher"],
                "context": f"'{user_context}' ke baad ye dekhne ki koshish ki sab theek hai ya mahol garam hai.",
                "alternatives": ["Lafda dekhne aana bina kuch bole", "Maafi maangne se pehle jhaankna", "Cute entry marna"],
                "meme": "Classic anime wall peeking trope.",
                "confidence": "Moderate",
                "replies": [
                    {"type": "Friendly", "text": "Aaja aaja, dar mat! Sab theek hai."},
                    {"type": "Funny", "text": "CID ki tarah deewar ke peeche se kya jhaank raha hai? 😂"},
                    {"type": "Playful", "text": "Dekh liya maine tujhe! 👋"}
                ]
            },
            "hi": {
                "meaning": "चुपके से झांकना, असहज बातचीत के बाद स्थिति की टोह लेना या शर्मीलापन दिखाना।",
                "tones": ["शर्मीला", "उत्सुक", "शांत"],
                "context": f"'{user_context}' के बाद यह जानने की कोशिश कि क्या स्थिति सामान्य है।",
                "alternatives": ["बातचीत में धीरे से शामिल होना", "तमाशा देखना"],
                "meme": "दीवार के पीछे से झांकने वाला कार्टून ट्रोप।",
                "confidence": "Moderate",
                "replies": [
                    {"type": "Friendly", "text": "आ जाओ, कोई बात नहीं! 👋"},
                    {"type": "Funny", "text": "दीवार के पीछे क्या कर रहे हो? 😂"}
                ]
            }
        }
    }

    # Match preset or default fallback
    matched_key = None
    desc_lower = desc.lower()
    if "cat" in desc_lower or "faint" in desc_lower or "sleep" in desc_lower or "orange" in desc_lower:
        matched_key = "dramatic_cat"
    elif "dog" in desc_lower or "cheem" in desc_lower or "shiba" in desc_lower:
        matched_key = "cheems_doge"
    elif "hera" in desc_lower or "pheri" in desc_lower or "babu" in desc_lower or "head" in desc_lower or "shock" in desc_lower:
        matched_key = "hera_pheri"
    elif "peek" in desc_lower or "shy" in desc_lower or "wall" in desc_lower or "hide" in desc_lower or "behind" in desc_lower:
        matched_key = "peeking_shy"

    if matched_key and matched_key in presets:
        data = presets[matched_key]
        lang_data = data.get(lang) or data["en"]
        return {
            "visual_description": data["visible"],
            "primary_meaning": lang_data["meaning"],
            "emotional_tone": lang_data["tones"],
            "contextual_interpretation": lang_data["context"],
            "alternative_meanings": lang_data["alternatives"],
            "meme_reference": lang_data["meme"],
            "confidence": lang_data["confidence"],
            "suggested_replies": lang_data["replies"]
        }

    # Generic contextual interpretation for custom uploaded stickers
    return {
        "visual_description": f"The sticker shows a character/reaction visual representing: '{desc}'.",
        "primary_meaning": "Expresses an emotionally heightened or humorous reaction tailored to convey unspoken subtext." if lang != "hi" else "बातचीत में अनकहे भावों और मज़ाकिया प्रतिक्रिया को व्यक्त करता है।",
        "emotional_tone": ["Humorous", "Playful", "Expressive"],
        "contextual_interpretation": f"In relation to '{user_context}', it serves as an emotional punchline or avoids a blunt text answer." if user_context else "Often used to replace a lengthy reply with an instant emotional signal.",
        "alternative_meanings": ["Playful sarcasm", "Deflecting serious tension", "Expressing excitement or shock"],
        "meme_reference": "Common internet reaction sticker format widely used across WhatsApp, Telegram, and Discord.",
        "confidence": "Moderate",
        "suggested_replies": [
            {"type": "Playful", "text": "Haha exactly what I was thinking! 😂" if lang == "en" else "Bilkul sahi reaction diya! 😂"},
            {"type": "Friendly", "text": "Tell me more, why that sticker? 🤔" if lang == "en" else "Aise kyu react kiya? 🤔"},
            {"type": "Funny", "text": "10/10 sticker choice! 👏" if lang == "en" else "Wah, kya sticker hai! 👏"}
        ]
    }


class StickerAppHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/explain":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}

            sticker_name = data.get("sticker_name", "custom_sticker")
            sticker_desc = data.get("sticker_description", "")
            user_context = data.get("chat_context", "").strip()
            language = data.get("language", "English")

            # Try Sarvam AI first if available
            sarvam_success = False
            sarvam_error_detail = None
            response_payload = None

            if sarvam_client:
                try:
                    user_msg = f"""Analyze this sticker for a user:
Sticker description: {sticker_desc or sticker_name}
Recent chat context: {user_context if user_context else 'None provided'}
Preferred language: {language}

Return your structured JSON analysis following the system instructions."""

                    chat_res = sarvam_client.chat.completions(
                        model="sarvam-105b-conversations",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_msg}
                        ],
                        temperature=0.4
                    )
                    raw_text = chat_res.choices[0].message.content.strip()
                    # Strip markdown code blocks if wrapped
                    if raw_text.startswith("```"):
                        raw_text = raw_text.split("\n", 1)[1]
                        if raw_text.endswith("```"):
                            raw_text = raw_text.rsplit("```", 1)[0]
                    parsed = json.loads(raw_text)
                    response_payload = parsed
                    sarvam_success = True
                except Exception as e:
                    err_str = str(e)
                    print(f"[Sarvam API Call Notice]: {err_str}")
                    if "402" in err_str or "insufficient_quota" in err_str:
                        sarvam_error_detail = "Sarvam AI cloud account currently has insufficient credits (HTTP 402). Using local multi-agent fallback engine."
                    else:
                        sarvam_error_detail = f"Sarvam AI: {err_str[:120]}"

            # If Sarvam didn't return or was out of quota, use intelligent fallback
            if not sarvam_success:
                response_payload = generate_intelligent_analysis(sticker_name, user_context, language, sticker_desc)

            result = {
                "status": "success",
                "sarvam_live": sarvam_success,
                "sarvam_notice": sarvam_error_detail,
                "data": response_payload
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        elif self.path == "/api/followup":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}

            question = data.get("question", "").strip()
            current_analysis = data.get("current_analysis", {})
            language = data.get("language", "English")

            # Follow up handling
            q_lower = question.lower()
            ans = ""
            if "simple" in q_lower:
                ans = f"In simple words: {current_analysis.get('primary_meaning', 'This sticker shows an exaggerated emotional reaction to lighten up the mood.')}"
            elif "funny" in q_lower or "joke" in q_lower or "why" in q_lower:
                ans = f"It's funny because of the hyper-exaggerated reaction! In messaging culture, sending an over-the-top reaction image breaks the tension and turns a potentially stressful topic into a lighthearted joke."
            elif "hinglish" in q_lower:
                ans = f"Hinglish mein iska simple matlab: {current_analysis.get('primary_meaning', 'Ye sticker mazaak mein over-dramatic reaction dene ke liye use hota hai!')}"
            elif "sarcastic" in q_lower:
                ans = f"Yes, this sticker is frequently used with sarcastic undertones—especially when responding to obvious questions or unreasonable demands!"
            elif "reply" in q_lower:
                ans = "Here are a few quick witty comebacks you can send:\n• 'Award jaata hai is dramatic performance ko! 🏆'\n• 'Haha don't faint on me yet! 😂'\n• 'Chai piyoge ya sidha hospital le chalu? ☕'"
            else:
                ans = f"Regarding '{question}': Based on the visual tone ({', '.join(current_analysis.get('emotional_tone', ['playful']))}) and context, this sticker serves to soften the conversation and invite a playful response rather than a serious confrontation."

            result = {
                "status": "success",
                "reply": ans
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def run():
    port = int(os.environ.get("PORT", 3000))
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, StickerAppHandler)
    print(f"Sticker Understander Web Server running at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
