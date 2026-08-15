# Asrar-e-Dunia AI Agent — Complete Setup Guide

Ye guide tumhe **step-by-step** batayegi ke is poore system ko apne computer par kaise
chalana hai, kaunse accounts banane hain, aur kaise test karna hai. Har step ko
order mein follow karo — kisi step ko skip mat karo.

---

## System Kya Karta Hai (Recap)

- Har **3 din** mein 1 Long Video (20-30 min, Urdu world-history)
- Har **2 din** mein 3 Shorts (long video se auto-nikalte hain)
- Research → Script → Voiceover → Visuals (no-repeat) → Assembly → Thumbnail → Upload — **sab automatic**
- Har module mein Tier 1 (best tool) → Tier 2 → Tier 3 (free fallback) — koi bhi tool fail ho, system rukta nahi

---

## STEP 1: Zaroori Software Install Karo

Apne computer (Windows/Mac/Linux) par ye cheezein install karo:

### 1.1 Python (agar pehle se nahi hai)
- [python.org/downloads](https://python.org/downloads) se Python 3.10+ install karo
- Install karte waqt **"Add Python to PATH"** checkbox zaroor tick karo

### 1.2 FFmpeg (video processing ke liye zaroori)
- **Windows:** [ffmpeg.org/download.html](https://ffmpeg.org/download.html) se download karo, PATH mein add karo
- **Mac:** Terminal mein: `brew install ffmpeg`
- **Linux:** Terminal mein: `sudo apt install ffmpeg`

Verify karne ke liye terminal/cmd mein likho:
```
ffmpeg -version
python3 --version
```
Dono ka version number dikhna chahiye.

---

## STEP 2: Project Files Setup Karo

1. Ye poora `asrar_e_dunia_agent` folder apne computer par kisi jagah rakho (jaise Desktop par)
2. Terminal/Command Prompt kholo aur us folder mein jao:
   ```
   cd path/to/asrar_e_dunia_agent
   ```
3. Sab Python libraries install karo:
   ```
   pip install -r requirements.txt --break-system-packages
   ```
   (Agar error aaye to `--break-system-packages` hata kar try karo)

4. Database test karo:
   ```
   python3 database.py
   ```
   Output: `Database ready: .../data/agent_memory.db` — agar ye dikhe, sab theek hai.

---

## STEP 3: Free Accounts Banao (Tier-wise)

Yahan har tool ke liye signup link hai. **Sabse pehle Tier 3 (guaranteed free) wale
tools setup karo** — inke bina system chal hi nahi sakta. Tier 1/2 baad mein add
kar sakte ho jab time mile.

### ZAROORI (System Chalane Ke Liye Minimum):

| Tool | Kis Liye | Link | Free? |
|---|---|---|---|
| YouTube Data API | Research + Upload | [console.cloud.google.com](https://console.cloud.google.com) | ✅ Haan |
| Edge TTS | Voiceover (Tier 3) | Koi signup nahi chahiye | ✅ Unlimited |
| Pexels API | Video clips | [pexels.com/api](https://www.pexels.com/api/) | ✅ Haan |
| Pixabay API | Video clips backup | [pixabay.com/api/docs](https://pixabay.com/api/docs/) | ✅ Haan |

### OPTIONAL (Behtar Quality Ke Liye, Baad Mein Add Karo):

| Tool | Kis Liye | Link | Free Tier |
|---|---|---|---|
| Claude API | Script writing (Tier 1) | [console.anthropic.com](https://console.anthropic.com) | Limited credits |
| Google Gemini | Script writing (Tier 2) | [ai.google.dev](https://ai.google.dev) | Generous free tier |
| ElevenLabs | Voiceover (Tier 1) | [elevenlabs.io](https://elevenlabs.io) | ~10K chars/month |
| Runway ML | AI video clips | [runwayml.com](https://runwayml.com) | Limited credits |

---

## STEP 4: YouTube API Setup (Sabse Zaroori Step)

1. [console.cloud.google.com](https://console.cloud.google.com) par jao, Google account se login karo
2. Naya project banao (upar left "Select Project" → "New Project")
3. Left menu se **"APIs & Services" → "Library"** mein jao
4. Search karo **"YouTube Data API v3"** aur **Enable** karo
5. **"Credentials"** tab par jao → **"Create Credentials" → "OAuth Client ID"**
6. Application type: **"Desktop App"** select karo
7. Naam do (jaise "Asrar-e-Dunia Agent") aur Create karo
8. JSON file download hogi — is file ko rename karo `youtube_client_secret.json`
   aur project ke main folder mein rakho (jahan `main.py` hai)

---

## STEP 5: API Keys Ko System Mein Daalo

`config.py` file kholo aur jo keys tumne banayi hain wo daalo. Ya phir terminal mein
environment variables set karo (zyada safe tareeqa):

**Windows (cmd):**
```
set CLAUDE_API_KEY=your_key_here
set PEXELS_API_KEY=your_key_here
```

**Mac/Linux (terminal):**
```
export CLAUDE_API_KEY=your_key_here
export PEXELS_API_KEY=your_key_here
```

Jo keys nahi hain unhe khali chhod do — system automatically agle tier par chala jayega.

---

## STEP 6: Background Music Aur Font Daalo

1. `assets/music/` folder mein ek royalty-free music file rakho, naam do:
   `default_background.mp3`
   (YouTube Audio Library ya Pixabay Music se free le sakte ho)

2. `assets/fonts/` folder mein ek Urdu font (.ttf) rakho, naam do: `urdu_font.ttf`
   (Google Fonts par "Noto Nastaliq Urdu" free available hai)

---

## STEP 7: Pehla Test Run Karo

Poora pipeline chalane se pehle, har module ko individually test karo:

```
python3 modules/scheduler.py
```
Ye dikhayega aaj kya karna hai.

```
python3 modules/thumbnail.py
```
Ye confirm karega thumbnail-generation kaam kar raha hai.

Agar sab theek chale, to poora system chalao:
```
python3 main.py
```

**Pehli dafa YouTube upload ke waqt** ek browser window khulega — apne YouTube
channel se login karke permission do. Uske baad ye automatic ho jayega.

---

## STEP 8: Daily Automatic Chalane Ke Liye (Scheduling)

Taake tumhe roz khud se `python3 main.py` na chalana pade:

### Mac/Linux (cron job):
Terminal mein likho: `crontab -e`
Ye line add karo (roz subah 9 baje chalega):
```
0 9 * * * cd /full/path/to/asrar_e_dunia_agent && python3 main.py >> logs.txt 2>&1
```

### Windows (Task Scheduler):
1. Start menu mein "Task Scheduler" search karo
2. "Create Basic Task" → naam do → Daily trigger set karo
3. Action: "Start a Program" → `python.exe` ka path do, arguments mein `main.py` ka full path do

---

## STEP 9: Channel Ki Pehli Setup (Manual, Ek Dafa)

1. YouTube par naya channel banao, naam: **Asrar-e-Dunia**
2. Pehle di gayi DP aur Banner images upload karo (channel customization se)
3. Channel description mein pehle di gayi description paste karo
4. Channel keywords (Settings → Advanced) mein SEO keywords daalo (uploader.py
   ke `CORE_KEYWORDS` wali list)

---

## Troubleshooting (Aam Masail)

| Masla | Wajah | Hal |
|---|---|---|
| `ModuleNotFoundError` | Library install nahi hui | `pip install -r requirements.txt` dobara chalao |
| `ffmpeg: command not found` | FFmpeg install nahi hui ya PATH mein nahi | Step 1.2 dobara karo |
| Voiceover generate nahi ho raha | Internet issue ya Edge TTS down | Thodi der baad try karo |
| YouTube upload fail | OAuth token expire | `data/youtube_token.pickle` delete karo, dobara login karo |
| Script JSON parse error | LLM ne invalid JSON diya | Tier khud-b-khud agle par chala jayega, warna prompt adjust karo |

---

## Zaroori Yaad Dahani

- **Kabhi bhi** kisi Sahabi/Nabi/religious figure ki tasveer generate mat karna
  (`config.py` mein `CONTENT_RULES` already ye restrict karta hai, lekin manually
  bhi dhyan rakhna jab topics review karo)
- Shuru ke 10-15 videos manually review kar lena (clip-matching, script quality)
  taake system ka pattern samajh aaye
- API keys kabhi kisi ke sath share mat karna ya GitHub par public mat karna

---

Is guide ko follow karke system chalu ho jana chahiye. Agar kisi step par error aaye,
wo exact error message copy karke wapas puchna — us hisab se fix karenge.
