import os
from pathlib import Path
from sarvamai import SarvamAI

# Load variables from .env into environment
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

# Initialize Sarvam client (reads SARVAM_API_KEY from environment)
client = SarvamAI(api_subscription_key=os.environ.get("SARVAM_API_KEY"))

response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[
        {"role": "user", "content": "Hello! Introduce yourself briefly."}
    ],
)

print(response.choices[0].message.content)
