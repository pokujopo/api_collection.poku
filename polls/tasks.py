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
def safisha_media_files_task():
    try:
        # 1. Tunavuta rekodi zote za "Success" zilizopo Supabase
        vitu_vya_kufuta = Test.objects.filter(status="Success")
        
        hesabu_ya_files = 0
        hesabu_ya_db_updated = 0
        
        for kazi in vitu_vya_kufuta:
            # Njia halisi ya kwenda kwenye file kwenye diski ya Render (Mfano: media/downloads/video_123.mp4)
            njia_ya_faili = os.path.join('media', 'downloads', str(kazi.name))
            
            # --- HATUA YA A: SAFISHA DISKI YA RENDER ---
            if os.path.exists(njia_ya_faili):
                try:
                    os.remove(njia_ya_faili)
                    hesabu_ya_files += 1
                except Exception as file_error:
                    print(f"Nimeshindwa kufuta file la {kazi.name}: {str(file_error)}")
                    # Kama file limegoma kufutika, usiguse DB ili ijaribu tena raundi ijayo
                    continue 
            
            # --- HATUA YA B: UPDATE SUPABASE DATABASE (Soft Delete) ---
            # Badala ya kazi.delete(), tunabadilisha status na kufuta jina la file.
            # Hii inalinda Download History ya mtumiaji kule Frontend!
            kazi.status = "Cleaned"
            kazi.name = None  # Faili halipo tena kwenye diski
            kazi.save()       # Hii inasafiri mpaka Supabase papo hapo!
            hesabu_ya_db_updated += 1
            
        print(f"=====================================================")
        print(f"USHAHIDI: Nimefuta Ma-file {hesabu_ya_files} kwenye Storage ya Render")
        print(f"USHAHIDI: Nimesafisha Rekodi {hesabu_ya_db_updated} kule Supabase DB")
        print(f"=====================================================")
        
        return f"Files Removed: {hesabu_ya_files}, Supabase Rows Updated: {hesabu_ya_db_updated}"
        
    except Exception as e:
        print(f"Kosa kuu la usafi: {str(e)}")
        return str(e)
                

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

        
