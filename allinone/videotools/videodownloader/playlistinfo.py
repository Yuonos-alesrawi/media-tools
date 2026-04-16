import yt_dlp
import re
from videodownloader.chooseresolution import simplify_formats

def get_playlist_details(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # --- الجزء الأول: التعامل مع الفيديو العادي ---
        if 'entries' not in info:
            # إذا لم يكن هناك entries، نرسل الرابط مباشرة للدالة الاصلية
            return simplify_formats(url)

        # --- الجزء الثاني: التعامل مع قائمة التشغيل ---
        entries = [e for e in info.get('entries', []) if e is not None]
        total_videos = len(entries)
        
        if total_videos == 0:
            return {"formats": [], "url": url}

        playlist_formats_stats = {}

        for entry in entries:
            formats = entry.get('formats', [])
            
            # حساب أفضل صوت للفيديو الحالي
            audio_f = next((f for f in reversed(formats) if f.get('vcodec') == 'none' and f.get('acodec') != 'none'), None)
            audio_size = (audio_f.get('filesize') or audio_f.get('filesize_approx') or 0) if audio_f else 0

            for f in formats:
                if f.get('vcodec') != 'none':
                    res = str(f.get('format_note') or f.get('height'))
                    
                    # تنظيف الرزلوشن: تحويل 1080p60 إلى 1080p لجمعهم معاً
                    res_match = re.search(r'\d+', res)
                    clean_res = f"{res_match.group()}p" if res_match else res
                    
                    # في القوائم نوحد الـ FPS لجمع 1080p و 1080p60 في خانة واحدة
                    key = clean_res
                    
                    video_size = f.get('filesize') or f.get('filesize_approx') or 0
                    
                    if key not in playlist_formats_stats:
                        playlist_formats_stats[key] = {
                            'resolution': clean_res,
                            'total_filesize': 0,
                            'ext': f.get('ext'),
                            'count': 0
                        }
                    
                    playlist_formats_stats[key]['total_filesize'] += (video_size + audio_size)
                    playlist_formats_stats[key]['count'] += 1

        # --- الجزء الثالث: الفلترة والترتيب ---
        final_formats = []
        for stats in playlist_formats_stats.values():
            # شرطك: يجب أن تتوفر الجودة في كل فيديوهات القائمة
            if stats['count'] == total_videos:
                final_formats.append({
                    'format_id': 'playlist', # معرف ثابت للقوائم
                    'resolution': stats['resolution'],
                    'ext': stats['ext'],
                    'filesize': round(stats['total_filesize'] / (1024 * 1024), 2),
                    # لا نرسل fps أو video_count للحفاظ على شكل الـ Response القديم
                })

        # ترتيب الجودات من الأعلى (2160p) إلى الأقل (144p)
        final_formats.sort(key=lambda x: int(re.search(r'\d+', x['resolution']).group()) if re.search(r'\d+', x['resolution']) else 0, reverse=False)

    return {"formats": final_formats, "url": url}