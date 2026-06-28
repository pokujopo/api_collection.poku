#tasks.py
# vipimo/tasks.py
"""
from celery import shared_task
import os
import yt_dlp
from django.conf import settings
from .models import Test

@shared_task  # <── Hii inamwambia Celery: "Hii ni kazi yako ya nyuma ya pazia!"
def download_youtube_video_task(instance_id):
    media_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
    if not os.path.exists(media_path):
        os.makedirs(media_path)

    ydl_opts = {
        'outtmpl': os.path.join(media_path, '%(title)s.%(ext)s'),
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            just_filename = os.path.basename(filename)
            
            # Tunatafuta ile rekodi kwenye DB na kuisasisha kimya kimya kule nyuma
            instance = Test.objects.get(id=instance_id)
            instance.video_file = os.path.join('downloads', just_filename)
            instance.save()
            print("Celery amemaliza kudownload video kwa mafanikio!")
    except Exception as e:
        print(f"Kosa kwenye Celery: {e}")
"""
"""
from celery import shared_task
import yt_dlp
# Weka model yako halisi hapa (badilisha TestModel iwe jina la model yako)
from .models import Test

@shared_task
def download_youtube_video_task(instance_id):
    try:
        # 1. Celery inaenda kwenye DB kuvuta rekodi halisi kwa kutumia ID (Namba)
        instance = Test.objects.get(id=instance_id)
        
        # 2. Hapa tunajua kwa 100% zipi ni link na yapi ni majina kutoka kwenye DB direct
        url_ya_video = instance.link
        jina_la_video = instance.name
        
        ydl_opts = {
            'outtmpl': f'media/downloads/{jina_la_video}.%(ext)s',
        }
        
        # 3. Mtambo wa yt-dlp unawaka kwa kutumia data safi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_ya_video])
            
        # 4. Baada ya download kuisha, unaweza ku-update DB salama
        instance.status = "Success" # au field yoyote uliyonayo
        instance.save()
        
        return "Download Imekamilika na DB Imebadiika!"
        
    except Exception as e:
        return f"Kosa kwenye Celery: {str(e)}"

import os
from celery import shared_task
import yt_dlp
from .models import Test

@shared_task
def download_youtube_video_task(instance_id):
    try:
        # 1. Celery inaenda kwenye DB kuvuta rekodi halisi kwa kutumia ID (Namba)
        instance = Test.objects.get(id=instance_id)
        
        url_ya_video = instance.link
        
        # SULUHISHO: Tunalazimisha faili liitwe kwa ID ya database (Mfano: 34.mp4)
        # Hii inaondoa kabisa shida ya nafasi (spaces) au herufi mbaya kwenye majina ya faili!
        ydl_opts = {
            'outtmpl': f'media/downloads/{instance.id}.%(ext)s',
            'quiet': True, # Inazima kelele zisizo na msingi kwenye log
        }
        
        # 2. Mtambo wa yt-dlp unawaka kwa kutumia data safi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Tunavuta taarifa za video ili tujue imesave kama mp4 au format gani
            info = ydl.extract_info(url_ya_video, download=True)
            ext = info.get('ext', 'mp4') # Kama isipopatikana, chukua mp4
            
        # 3. KAZI IMEISHA SALAMA: Sasa tunaiambia database mambo matatu:
        instance.status = "Success"
        # Tunasave jina halisi lililopo kwenye simu (Mfano: "34.mp4") ili View isihangaike
        instance.name = f"{instance.id}.{ext}"
        instance.save() # <── HAPA SASA PUSH ITAENDA KWA 100% BILA KUTELEZA!
        
        return "Download Imekamilika na DB Imebadilika Kuwa Success!"
        
    except Exception as e:
        # Kama ikifeli katikati ya safari, ibadilishe iwe Failed ili user asisubiri milele
        try:
            instance = Test.objects.get(id=instance_id)
            instance.status = "Failed"
            instance.save()
        except:
            pass
        return f"Kosa kwenye Celery: {str(e)}"
"""      
import os
from celery import shared_task
from .models import Test

@shared_task
def safisha_media_files_task():
    try:
        # 1. Tunavuta rekodi zote za Success zilizopo DB
        vitu_vya_kufuta = Test.objects.filter(status="Success")
        
        hesabu_ya_files = 0
        hesabu_ya_db = 0
        
        for kazi in vitu_vya_kufuta:
            # Njia halisi ya kwenda kwenye file (Mfano: media/downloads/48.mp4)
            njia_ya_faili = os.path.join('media', 'downloads', str(kazi.name))
            
            # --- HATUA YA A: PAPASA STORAGE KWANZA ---
            # Kama file lipo, liangamize kabisa bila huruma
            if os.path.exists(njia_ya_faili):
                try:
                    os.remove(njia_ya_faili)
                    hesabu_ya_files += 1
                except Exception as file_error:
                    print(f"Nimeshindwa kufuta file la {kazi.name}: {str(file_error)}")
                    # Kama file limegoma kufutika kwa sababu ya mfumo, usifute DB kwanza!
                    continue 
            
            # --- HATUA YA B: SAFISHA DATABASE ---
            # Tunafuta DB TU BAADA ya kujiridhisha kuwa file halipo tena storage
            kazi.delete()
            hesabu_ya_db += 1
            
        print(f"=====================================================")
        print(f"USHAHIDI: Nimefuta Ma-file {hesabu_ya_files} kwenye Storage")
        print(f"USHAHIDI: Nimefuta Rekodi {hesabu_ya_db} kwenye Database")
        print(f"=====================================================")
        
        return f"Files: {hesabu_ya_files}, DB: {hesabu_ya_db}"
        
    except Exception as e:
        print(f"Kosa kuu la usafi: {str(e)}")
        return str(e)
"""
import os
from celery import shared_task
import yt_dlp
from .models import Test

@shared_task
def download_youtube_video_task(instance_id):
    try:
        # 1. Vuta data halisi kutoka DB
        instance = Test.objects.get(id=instance_id)
        url_ya_video = instance.link
        
        # 2. Tengeneza muundo wa kimsingi wa ydl_opts
        ydl_opts = {
            'outtmpl': 'media/downloads/%(title)s_%(id)s.%(ext)s',
            'quiet': True,
            'restrictfilenames': True,
        }
        
        # --- MAPINDUZI YA FFMPEG & QUALITY CONFIGURATION ---
        
        if instance.format_type == 'audio':
            # A: Mtumiaji anataka Audio (MP3) pekee kupitia FFmpeg
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', # Ubora wa sauti (192kbps)
            }]
        else:
            # B: Mtumiaji anataka Video (Chagua Quality)
            if instance.quality == '1080p':
                # Unganisha picha bora ya 1080p na sauti bora kupitia FFmpeg
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
            elif instance.quality == '720p':
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
            elif instance.quality == '360p':
                ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best'
            else:
                # 'best' au dharura yoyote
                ydl_opts['format'] = 'bestvideo+bestaudio/best'

        # 3. Mtambo wa yt-dlp unawaka sasa hivi ukiwa na options zote safi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_ya_video, download=True)
            # Kama ni audio, extension ya mwisho baada ya FFmpeg kugeuza itakuwa mp3
            ext = 'mp3' if instance.format_type == 'audio' else info.get('ext', 'mp4')
            
        # 4. Kazi imeisha: Update DB na uweke jina halisi lililookoka storage
        instance.status = "Success"
        #jina_kamili = f"{info.get('title')}_{info.get('id')}.{ext}"
        filename_kamili = ydl.prepare_filename(info)
        jina_la_file_tu = os.path.basename(filename_kamili)  # Hii inakata na kubakiza jina tu (mfano: video_123.mp3)
        if instance.format_type == 'audio':
    # Hapa tunakata extension ya zamani (.m4a/.webm) na kuweka .mp3 safi kabisa
            jina_la_msingi, _ = os.path.splitext(jina_la_file_tu)
            jina_la_file_tu = f"{jina_la_msingi}.mp3"
        else:
    # Kama ni video, tunatumia ile ile ext iliyotoka kwenye info, au tunahakikisha mp4
            ext = info.get('ext', 'mp4')
            jina_la_msingi, _ = os.path.splitext(jina_la_file_tu)
            jina_la_file_tu = f"{jina_la_msingi}.{ext}" 
        instance.name = jina_la_file_tu
        instance.save()
        
        return f"Download Imekamilika! Aina: {instance.format_type}, File: {instance.name}"
        
    except Exception as e:
        # Usalama kuzuia kifo cha foleni
        try:
            instance = Test.objects.get(id=instance_id)
            instance.status = "Failed"
            instance.error_message = str(e)
            instance.save()
        except:
            pass
        return f"Kosa: {str(e)}"
"""
import os
import subprocess
import cloudinary
import cloudinary.uploader
from celery import shared_task
from .models import Test  # Inasoma model yako ya Test inayokwenda Supabase

# Config ya Cloudinary inayosoma kutoka kwenye zile Environment Variables za Render
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

@shared_task
def download_youtube_video_task(instance_id):
    try:
        # 1. Vuta data halisi kutoka Supabase DB
        instance = Test.objects.get(id=instance_id)
        url_ya_video = instance.link
        
        # 2. Maandalizi ya Amri ya yt-dlp (Misingi ya Juu kwa Juu)
        # Tutaandika amri ya Linux itakayorusha data kwenye RAM badala ya kutengeneza faili (-o -)
        command = ['yt-dlp', '-o', '-', 'quiet']
        
        # --- MAPINDUZI YA FORMAT & QUALITY CONFIGURATION JUU KWA JUU ---
        if instance.format_type == 'audio':
            # Mtumiaji anataka sauti pekee (Tunapiga mkwaju wa extract-audio kama stream)
            command.extend([
                '-f', 'ba/best',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '192K'
            ])
            resource_type = "raw"  # Sauti safi ya mp3 inayokwenda kama file
            ext = "mp3"
        else:
            # Mtumiaji anataka Video (Chagua Quality)
            # Kumbuka: Kwenye mfumo wa ku-stream moja kwa moja (-o -), tunachagua format moja bora kabisa
            # inayojitosheleza (yenye video na audio pamoja) ili isihitaji kuunganishwa (merge) kwenye diski.
            if instance.quality == '1080p':
                command.extend(['-f', 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/best[height<=1080]/best'])
            elif instance.quality == '720p':
                command.extend(['-f', 'bv*[height<=720][ext=mp4]+ba[ext=m4a]/best[height<=720]/best'])
            elif instance.quality == '360p':
                command.extend(['-f', 'bv*[height<=360][ext=mp4]+ba[ext=m4a]/best[height<=360]/best'])
            else:
                command.extend(['-f', 'bv*[ext=mp4]+ba[ext=m4a]/best'])
                
            resource_type = "video"
            ext = "mp4"

        # Ongeza URL ya video mwishoni mwa amri wetu
        command.append(url_ya_video)
        
        # 3. Washa Bomba la Kutiririsha Data (Subprocess Pipe) kwenye RAM ya Render
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 4. Rusha hiyo Stream moja kwa moja Cloudinary bila kugusa Hard Disk!
        # Tunatumia upload_stream ambayo inapokea maji yanayotiririka kutoka kwenye process.stdout
        upload_result = cloudinary.uploader.upload_stream(
            process.stdout,
            resource_type=resource_type,
            public_id=f"poku_file_{instance_id}",
            folder="poku_downloads"
        )
        
        # Subiri mchakato wa yt-dlp umalizike salama
        process.wait()
        
        # 5. Kazi imekamilika kwa Ushindi: Update Supabase DB
        instance.status = "Success"
        
        # Tunachukua ile URL salama (Secure URL) kutoka Cloudinary
        link_ya_cloudinary = upload_result.get('secure_url')
        instance.download_url = link_ya_cloudinary  # Au field uliyoweka kuhifadhi link ya download
        
        # Kutengeneza jina la faili la kuonesha kule Frontend
        instance.name = f"download_{instance_id}.{ext}"
        instance.save()
        
        return f"Download Imekamilika! Aina: {instance.format_type}, Link ya Cloudinary: {link_ya_cloudinary}"
        
    except Exception as e:
        # Usalama kuzuia kifo cha foleni na kusave makosa Supabase
        try:
            instance = Test.objects.get(id=instance_id)
            instance.status = "Failed"
            instance.error_message = str(e)
            instance.save()
        except:
            pass
        return f"Kosa: {str(e)}"
@shared_task
def safisha_media_files_task(public_id):
    # Amri ya kwenda kufuta kule Cloudinary mawinguni kimyakimya
    cloudinary.uploader.destroy(public_id, resource_type="video")
    return f"Video {public_id} imefutwa salama Cloudinary ili kulinda nafasi!"
    
"""
import os
from celery import shared_task
from .models import Test

@shared_task
def safisha_media_files_task():
    try:
        # 1. Tunatafuta rekodi zote zilizofanikiwa (Success) kwenye DB bila kujali muda!
        vitu_vya_kufuta = Test.objects.filter(status="Success")
        
        hesabu = 0
        for kazi in vitu_vya_kufuta:
            # Njia ya kwenda kwenye file (Mfano: media/downloads/39.mp4)
            njia_ya_faili = os.path.join('media', 'downloads', f"{kazi.name}")
            
            # A: Futa faili halisi kwenye simu
            if os.path.exists(njia_ya_faili):
                os.remove(njia_ya_faili)
                
            # B: Futa rekodi kwenye Database
            kazi.delete()
            hesabu += 1
            
        # Hili neno litaonekana kwenye TERMINAL YA WORKER (Sio ya Beat!)
        print(f"=====================================================")
        print(f"BOOM! USAFI WA KIKOMANDOO UMEFANYIKA: Nimefuta video {hesabu}!")
        print(f"=====================================================")
        
        return f"Nimefuta video {hesabu}"
        
    except Exception as e:
        print(f"Kosa la usafi: {str(e)}")
        return str(e)
"""

"""
import os
from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from .models import Test  # Model yako

@shared_task
def safisha_media_files_task():
    try:
        # 1. WEKA MUDA WAKO HAPA:
        # Tunatafuta ma-file yaliyokaa zaidi ya LISAA LIMOJA (hours=1)
        # Kama unataka dakika 30, badilisha iwe timedelta(minutes=30)
        muda_wa_kufa = timezone.now() - timedelta(minutes=1)
        
        # 2. Tafuta kwenye database rekodi zote za zamani ambazo zilishakuwa "Success"
        # na muda wake wa kuumbwa (created_at) ni mdogo kuliko ule muda wetu wa kufa
        vitu_vya_kufuta = Test.objects.filter(
            status="Success",
            created_at__lte=muda_wa_kufa
        )
        
        hesabu = 0
        for kazi in vitu_vya_kufuta:
            # Njia halisi ya kwenda lilipo faili kwenye simu (Mfano: media/downloads/40.mp4)
            njia_ya_faili = os.path.join('media', 'downloads', f"{kazi.name}")
            
            # A: Futa faili halisi lililopo kwenye storage ya simu yako
            if os.path.exists(njia_ya_faili):
                os.remove(njia_ya_faili)
            
            # B: Futa kabisa ile rekodi kwenye Database ili isionekane tena kwenye API
            kazi.delete()
            
            hesabu += 1
            
        return f"USAFI UMEISHA: Nimefuta video {hesabu} zilizopitisha muda wa lisaa limoja!"
        
    except Exception as e:
        return f"Kosa lilitokea wakati wa usafi: {str(e)}"
"""
