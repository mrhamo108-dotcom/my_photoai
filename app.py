import telebot
import requests
import cv2
import numpy as np
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. إعداد خادم ويب وهمي لإرضاء منصة Koyeb
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    server.serve_forever()

# 2. إعدادات بوت تليجرام
API_TOKEN = '1436657438:AAFFChQdjDNvlvhOwPHo7Rrm83U7NiTJHaA' # ضع التوكن هنا
bot = telebot.TeleBot(API_TOKEN)

def get_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&nologo=true"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            nparr = np.frombuffer(response.content, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except: return None
    return None

@bot.message_handler(func=lambda m: True)
def handle(m):
    words = m.text.split()
    if len(words) < 2: return
    
    chat_id = m.chat.id
    status = bot.reply_to(m, "🧬 جاري معالجة الكائنات...")
    
    i1, i2 = get_image(words[0]), get_image(words[1])
    i3 = get_image(f"hybrid of {words[0]} and {words[1]}, detailed")

    if i1 is not None and i3 is not None:
        video = f"v_{chat_id}.mp4"
        out = cv2.VideoWriter(video, cv2.VideoWriter_fourcc(*'mp4v'), 20, (512, 512))
        for img in [i1, i2 if i2 is not None else i1, i3]:
            for _ in range(40): out.write(cv2.resize(img, (512, 512)))
        out.release()
        
        with open(video, 'rb') as v:
            bot.send_video(chat_id, v, caption="✅ تم التحول!")
        os.remove(video)
    else:
        bot.reply_to(m, "❌ فشل التوليد، جرب كلمات أخرى.")

# 3. تشغيل الخادم والبوت معاً
if __name__ == "__main__":
    # تشغيل خادم الصحة في Thread منفصل
    threading.Thread(target=run_health_server, daemon=True).start()
    print("Bot started...")
    bot.infinity_polling()

    # توليد الصور الثلاث
    img1 = get_image(obj1)
    img2 = get_image(obj2)
    img_final = get_image(f"mystical hybrid fusion of {obj1} and {obj2}")

    if img1 is not None and img2 is not None and img_final is not None:
        video_path = f"fusion_{chat_id}.mp4"
        
        # إعداد الفيديو
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, 20.0, (512, 512))
        
        # دمج الصور في الفيديو مع تأثير بسيط
        frames = [img1, img2, img_final]
        for f in frames:
            for _ in range(40): out.write(cv2.resize(f, (512, 512)))
            
        out.release()
        
        with open(video_path, 'rb') as v:
            bot.send_video(chat_id, v, caption="✅ اكتمل التحول!")
        
        os.remove(video_path)
    else:
        bot.reply_to(message, "❌ فشل التوليد، جرب كلمات أبسط.")

bot.infinity_polling()
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
