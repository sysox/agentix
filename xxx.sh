python - << 'EOF'
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
r = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": "Say hello"}],
)
print(r.choices[0].message.content)
EOF
