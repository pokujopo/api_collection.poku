# 🚀 Advanced Asynchronous Media Downloader API (Django + Celery + Redis + FFmpeg)

Mfumo thabiti na wa kisasa wa kiwango cha juu (Enterprise-grade) unaoruhusu watumiaji kupakua video na sauti (MP3) kutoka mitandao ya kijamii (YouTube, Facebook, n.k.) kiotomatiki na kwa kasi ya juu kwa kutumia mifumo ya kijasusi ya kazi za nyuma (Asynchronous Task Queue).

---

## 🌍 SECTION 1: LIVE PRODUCTION USER EXPERIENCE (ONLINE USER)

Kama mfumo huu umeshawekwa live kwenye server (Production Environment), huu ndio mtiririko wa jinsi mtumiaji (au application ya Frontend) inavyopingana na API hii:

### 1. Mtiririko wa Mfumo (The Workflow)
1. **Request Submission:** Mtumiaji anatuma link ya video, akichagua aina ya file (`video` au `audio`) na ubora anaoutaka (`1080p`, `720p`, `best`).
2. **Instant Response:** API inamrudishia majibu ya sekunde 0 ikiwa na hali ya `Pending` na `ID` ya kazi. Mfumo haumsubirishi mtumiaji kwenye browser wakati download inaendelea kule nyuma.
3. **Background Processing:** Celery Worker anaamka chini kwa chini, anashusha mzigo kwa kutumia `yt-dlp`, na kama ni sauti, anaikabidhi kwa `FFmpeg` kuigeuza kuwa `.mp3` safi na kusafisha jina (kuondoa emojis na alama haramu).
4. **Auto-Cleanup (Ulinzi wa Storage):** Mfumo una saa ya ukutani ya kiotomatiki (`Celery Beat`). Kila baada ya sekunde 60 (dakika 1), inapiga kengele na kufuta ma-file yote yaliyopakuliwa kwenye storage na kusafisha database ili server isijae takataka.

### 2. Live API Endpoints Data Structure
Ili kuwasiliana na mfumo ukiwa live, unahitaji kutuma request yako ukiambatanisha na `X-API-Key` kwenye Header kwa ajili ya ulinzi.

---

## 💻 SECTION 2: LOCALHOST DEVELOPMENT & TESTING (LOCAL USER)

Kama unataka kuufungua, kuufanyia majaribio, au kuuendesha mfumo huu kwenye mazingira ya kompyuta yako ya ndani au Termux (Localhost), fuata maelekezo yafuatayo hatua kwa hatua:

### 🛠️ Vigezo vya Lazima (Prerequisites)
Hakikisha mifumo hii ipo kwenye mashine yako:
* Python 3.10+
* Redis Server (Kama Message Broker)
* FFmpeg (Kwa ajili ya kuunganisha na kugeuza ma-file ya audio/video)

---

### 🏃‍♂️ Hatua za Kuwasha Mfumo Kwenye Localhost

#### 1. Washa Server ya Redis
Mifumo ya Celery haiwezi kuongea na Django bila Redis kuwa wazi. Fungua Terminal ya kwanza na uwashe Redis:
```bash
redis-server


2. Weka Mazingira Sawa (Environment & Migrations)
​Fungua Terminal ya pili, ingia kwenye folder la mradi, na kimbiza amri hizi za kutengeneza database:

# Tengeneza database na meza zake
python manage.py makemigrations
python manage.py migrate

# Washa Django Local Server
python manage.py runserver

3. Washa Celery Worker (Inayofanya Kazi ya Downloads)
​Fungua Terminal ya tatu. Huyu ndiye injini ya nyuma anayesubiri kupokea kazi kutoka kwa Django na kuendesha yt-dlp na FFmpeg:
celery -A myproject worker --loglevel=info --concurrency=4


4. Washa Celery Beat (Saa ya Usafi wa Kiotomatiki)
​Fungua Terminal ya nne. Huyu ndiye askari anayepiga kengele kila sekunde 60 ili kufuta video kwenye folder la media na kusafisha database:

# Futa kumbukumbu za zamani za ratiba kama zipo
rm celerybeat-schedule

# Washa Beat ikiwa safi
celery -A myproject beat --loglevel=info -C

🧪 Amri za Kufanyia Majaribio (Local Test Commands)
​Mifumo yote minne (Redis, Runserver, Worker, Beat) ikishakuwa wazi, unaweza kutumia amri za curl zifuatazo kupima utendaji kazi:
​A: Kuomba Kupakua Video (720p)

curl -X POST [http://127.0.0.1:8000/api/v1/download/](http://127.0.0.1:8000/api/v1/download/) \
     -H "X-API-Key: WEKA_API_KEY_YAKO_HAPA" \
     -H "Content-Type: application/json" \
     -d '{
           "link": "[https://www.facebook.com/share/v/1E62QanCsZ/](https://www.facebook.com/share/v/1E62QanCsZ/)",
           "format_type": "video",
           "quality": "720p"
         }'


B: Kuomba Kupakua Audio (MP3 pekee)

curl -X POST [http://127.0.0.1:8000/api/v1/download/](http://127.0.0.1:8000/api/v1/download/) \
     -H "X-API-Key: WEKA_API_KEY_YAKO_HAPA" \
     -H "Content-Type: application/json" \
     -d '{
           "link": "[https://www.facebook.com/share/v/1E62QanCsZ/](https://www.facebook.com/share/v/1E62QanCsZ/)",
           "format_type": "audio",
           "quality": "best"
         }'

C: Angalia Log za Ushindi
​Kwenye terminal ya Worker, utaona maendeleo ya asilimia ya download ikisoma 100.0% na kukupa ujumbe wa Success.
​Baada ya dakika 1, utaona terminal hiyo hiyo ya Worker ikitema maandishi ya usafi:

=====================================================
USHAHIDI: Nimefuta Ma-file 1 kwenye Storage
USHAHIDI: Nimefuta Rekodi 1 kwenye Database
=====================================================


---

### KUHUSU SWALA LA API DOCUMENTATION (ILE UI YA KISASA)

Mzee wangu, ule muonekano wa kisasa kabisa unaouzungumzia (Ukurasa uliogawanyika mara tatu: Pembeni kushoto kuna *Menu*, katikati kuna *Maelezo ya API*, na kulia kuna *Giza lenye kodi/Code Snippets* ya lugha mbalimbali kama cURL, Python, JavaScript) unajulikana sana duniani kama **Three-Column API Documentation Layout**. 

Vyombo vinavyotumika kutengeneza huo muonekano kwa urahisi bila wewe kuandika HTML/CSS ngumu ni pamoja na:
1. **Redoc (Inayotumiwa sana na DRF kupitia OpenAPI/Swagger):** Hii inazalisha ule muonekano kiotomatiki kabisa kutokana na Serializers zako.
2. **Slate au Bump.sh:** Hizi ni platform maalum za kuandika dokezo za API zikawa na ule muonekano mkali sana wa kibiashara.

Mzee wa kazi, subiri unitumie huo mfano wa picha (UI) uliosema unataka nione, ili nikuambie ni chombo gani sahihi na jinsi tutakavyokiingiza kwenye huu mradi wetu wa Django kabla hatujagusa Frontend yenyewe! Naitubiri hiyo UI mzee wangu, nishushie tuendelee mbele!

