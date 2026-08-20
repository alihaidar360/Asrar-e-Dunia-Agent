ZAROORI: Is folder mein abhi koi proper Urdu font NAHI hai.

Maine (AI) is environment mein ek generic Arabic-capable font (FreeSerif) test
ke liye use kiya tha, lekin wo asal Nastaliq Urdu jaisa professional nahi lagta.
Isliye maine wo hata diya hai taake tum galti se wahi permanent use na kar lo.

TUMHE YE KARNA HAI (2 minute ka kaam):

1. Google Fonts se free Nastaliq font download karo:
   https://fonts.google.com/noto/specimen/Noto+Nastaliq+Urdu
   (Download family -> zip khulega -> .ttf file milegi)

   Ya phir "Jameel Noori Nastaliq" (bohat popular Pakistani font) search karke
   free download karo - ye zyada authentic/traditional Urdu look deta hai.

2. Us .ttf file ka naam badal kar rakho: urdu_font.ttf

3. Isi folder (assets/fonts/) mein rakh do

Is font ko ye modules use karte hain:
- modules/thumbnail.py (thumbnail text)
- modules/shorts_generator.py (Shorts hook text)
- modules/video_assembler.py (subtitles)

Font daalne ke baad, config.py mein URDU_FONT_PATH already isi file ko point
karta hai - kuch aur change karne ki zaroorat nahi.
