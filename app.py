import telebot
import requests
import cv2
import numpy as np
import os
import time
from io import BytesIO

# ضع التوكن الخاص بك هنا
API_TOKEN = '1471297967:AAHbNyIFVc5hP9t8XrzUBUbi0UV3T5d3x_o'
bot = telebot.TeleBot(API_TOKEN)

def generate_image(prompt):
    """توليد صورة من الذكاء الاصطناعي وإعادتها كـ NumPy array لـ OpenCV"""
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&nologo=true"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # تحويل البيانات القادمة من الرابط مباشرة لمصفوفة صور يفهمها OpenCV
            nparr = np.frombuffer(response.content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
    except Exception as e:
        print(f"Error generating image: {e}")
    return None

def create_fusion_video(img1, img2, img_final, output_path):
    """صنع فيديو مع تأثير تلاشي (Fade) احترافي"""
    size = (512, 512)
    fps = 24
    fade_frames = 20  # عدد الإطارات في لحظة التحول
    hold_frames = 30  # مدة بقاء كل صورة ثابتة
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, size)

    images = [img1, img2, img_final]
    
    for i in range(len(images)):
        # 1. عرض الصورة ثابتة
        for _ in range(hold_frames):
            out.write(images[i])
        
        # 2. عمل تأثير التلاشي للصورة التالية
        if i + 1 < len(images):
            for alpha in np.linspace(0, 1, fade_frames):
                blended = cv2.addWeighted(images[i+1], alpha, images[i], 1 - alpha, 0)
                out.write(blended)
                
    out.release()

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "🔥 أهلاً بك في بوت التحول الأسطوري!\n\n"
        "أرسل لي اسمين (بالإنجليزي) لدمجهما في فيديو سينمائي.\n"
        "مثال: `Lion Robot` أو `Eagle Tank`"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    words = message.text.split()
    if len(words) < 2:
        bot.reply_to(message, "❌ من فضلك أرسل كلمتين (مثال: Cat Dragon)")
        return

    chat_id = message.chat.id
    obj1, obj2 = words[0], words[1]
    status_msg = bot.reply_to(message, "⚙️ جاري تحضير المختبر وتوليد الكائنات...")

    # 1. توليد الصور برمجياً
    bot.edit_message_text("🎨 جاري رسم الكائن الأول...", chat_id, status_msg.message_id)
    img1 = generate_image(f"portrait of a {obj1}, realistic, studio lights")
    
    bot.edit_message_text("🎨 جاري رسم الكائن الثاني...", chat_id, status_msg.message_id)
    img2 = generate_image(f"portrait of a {obj2}, realistic, studio lights")
    
    bot.edit_message_text("🧪 جاري عملية الدمج النووي...", chat_id, status_msg.message_id)
    fusion_prompt = f"a hyper-realistic mythical creature hybrid of {obj1} and {obj2}, cinematic, 8k"
    img_final = generate_image(fusion_prompt)

    if img1 is not None and img2 is not None and img_final is not None:
        bot.edit_message_text("🎬 جاري مونتاج فيديو التحول...", chat_id, status_msg.message_id)
        
        video_path = f"fusion_{chat_id}.mp4"
        create_fusion_video(img1, img2, img_final, video_path)

        # 2. إرسال الفيديو
        with open(video_path, 'rb') as v:
            bot.send_video(
                chat_id, v, 
                caption=f"✅ اكتمل التحول!\n🧬 المكونات: {obj1} + {obj2}",
                reply_to_message_id=message.message_id
            )
        
        # تنظيف الملفات
        if os.path.exists(video_path):
            os.remove(video_path)
        bot.delete_message(chat_id, status_msg.message_id)
    else:
        bot.edit_message_text("❌ فشل المختبر في دمج هذه الكائنات. حاول مرة أخرى بأسماء أوضح.", chat_id, status_msg.message_id)

# تشغيل البوت
print("Bot is alive on Koyeb!")
bot.polling(non_stop=True)
