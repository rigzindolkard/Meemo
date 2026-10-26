# 🎭 Sticker Understander
(deployment link - https://lkwhzr6juz6knbvqxwp26k.streamlit.app)

An AI-powered application that decodes the hidden meaning, emotion, humour, and cultural references behind stickers and memes used in online conversations.

## 🌐 Live Public URL
- **Cloudflare Edge Live URL**: [https://weights-wallace-commonwealth-interference.trycloudflare.com](https://weights-wallace-commonwealth-interference.trycloudflare.com)
- **Local Development URL**: [http://localhost:3000](http://localhost:3000)

## 🤖 Multi-Stage AI Agent Architecture
1. **Agent 1: Sticker Vision Analyst** — Detects characters, expressions, actions, and observable objects.
2. **Agent 2: Emotion & Tone Analyst** — Detects sarcasm, playfulness, guilt, exaggeration, and awkwardness.
3. **Agent 3: Context Interpreter** — Analyzes conversation history to understand how recent chat context shapes the punchline.
4. **Agent 4: Meme & Cultural Reference Analyst** — Recognizes viral meme archetypes and cultural tropes.
5. **Agent 5: Explanation Generator** — Synthesizes structured interpretations with copyable witty responses.

## 🚀 Quick Start Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Sarvam API Key to .env
echo "SARVAM_API_KEY=your_key_here" > .env

# 3. Run the server
python server.py
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

## ☁️ Permanent Free Cloud Deployment (Render)
1. Fork or push this repository to GitHub: `https://github.com/rigzindolkard/Meemo`
2. Go to [Render.com](https://render.com) and click **New + → Web Service**.
3. Connect your GitHub repository.
4. Set:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
5. In **Environment Variables**, add:
   - `SARVAM_API_KEY`: *(Your key)*
6. Click **Deploy Web Service**!
