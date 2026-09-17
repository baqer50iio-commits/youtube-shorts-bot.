import os
import sys
import requests
import yt_dlp
import ffmpeg

# استقبال الرابط ومعلومات البوت من متغيرات النظام
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID", "1565041775")
VIDEO_URL = os.environ.get("VIDEO_URL")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def send_telegram_video(video_path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    with open(video_path, 'rb') as f:
        requests.post(url, data={"chat_id": CHAT_ID}, files={"video": f})

if __name__ == "__main__":
    if not VIDEO_URL:
        print("No video URL provided!")
        sys.exit(1)

    send_telegram_message("🎬 جاري بدء تحميل ومعالجة الفيديو على السيرفر السحابي...")

    # 1. تحميل الفيديو بأعلى جودة متوفرة بصيغة MP4
    output_template = "source.mp4"
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'merge_output_format': 'mp4',
        'outtmpl': output_template,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([VIDEO_URL])
    except Exception as e:
        send_telegram_message(f"❌ فشل التحميل: {str(e)}")
        sys.exit(1)

    send_telegram_message("✂️ جاري قص الفيديو وتحويله إلى مقطع عمودي (Shorts)...")

    # 2. قص أول 30 ثانية وتحويله إلى مقطع عمودي 9:16 باستخدام FFmpeg
    output_clip = "short_clip.mp4"
    try:
        # قص من الثانية 0 إلى 30، وعمل Crop ليكون عمودياً (1080x1920)
        (
            ffmpeg
            .input(output_template, ss=0, t=30)
            .filter('scale', 1080, 1920, force_original_aspect_ratio='increase')
            .filter('crop', 1080, 1920)
            .output(output_clip, vcodec='libx264', acodec='aac')
            .run(overwrite_output=True, quiet=True)
        )
    except Exception as e:
        send_telegram_message(f"❌ فشل المعالجة بـ FFmpeg: {str(e)}")
        sys.exit(1)

    send_telegram_message("📤 جاري إرسال المقطع إلى تليجرام...")
    send_telegram_video(output_clip)
    send_telegram_message("✅ تم الانتهاء بنجاح!")
