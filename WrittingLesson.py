import pygame
import os
import cv2
import random
import google.generativeai as genai
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import streamlit as st

class LetterTracingGame:
    def __init__(self):
        # إعداد Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 600))
        pygame.display.set_caption("تتبع الحرف")

        # إعداد بعض المتغيرات الأساسية
        self.letter_folder = 'Letter'
        self.shape_folder = 'Shape'
        self.image_index = 1  # يبدأ برقم 1
        self.total_images = len([name for name in os.listdir(self.letter_folder) if name.endswith(('.png', '.jpg'))])

        # تحميل الصور الأولى
        self.letter_image, self.original_shape_image, self.gray_shape_image = self.load_images(self.image_index)

        # تحميل الإيموجي
        self.happy_emoji = pygame.image.load('Happy.jpg')  # تأكد من وضع المسار الصحيح لصورة إيموجي الفرح
        self.happy_emoji = pygame.transform.scale(self.happy_emoji, (200, 200))  # تكبير إيموجي النجاح إلى الضعف

        self.sad_emoji = pygame.image.load('Sad.jpg')  # تأكد من وضع المسار الصحيح لصورة إيموجي الحزن
        self.sad_emoji = pygame.transform.scale(self.sad_emoji, (100, 100))  # نفس حجم إيموجي الفشل

        # قائمة لحفظ النقاط التي تم تحديدها
        self.tracked_points = []
        self.success = False
        self.wait_time = 0  # متغير للانتظار بعد تتبع الحرف بنجاح
        self.show_emoji = False  # للتحكم في عرض الإيموجي
        self.emoji_timer = 0  # مدة عرض الإيموجي
        self.current_emoji = None  # الإيموجي الحالي المعروض

        # إعداد بعض الألوان
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)

    # دالة لتحميل الصور
    def load_images(self, index):
        # تحميل صورة الحرف
        letter_image_path = os.path.join(self.letter_folder, f'{index}.png')
        if not os.path.exists(letter_image_path):
            letter_image_path = os.path.join(self.letter_folder, f'{index}.jpg')
        if os.path.exists(letter_image_path):
            letter_image = pygame.image.load(letter_image_path)
            letter_image = pygame.transform.scale(letter_image, (350, 500))
        else:
            print(f"لم يتم العثور على الصورة {index} في فولدر Letter!")
            pygame.quit()
            exit()

        # تحميل صورة الشكل
        shape_image_path = os.path.join(self.shape_folder, f'{index}.png')
        if not os.path.exists(shape_image_path):
            shape_image_path = os.path.join(self.shape_folder, f'{index}.jpg')
        if os.path.exists(shape_image_path):
            original_shape_image = pygame.image.load(shape_image_path)
            original_shape_image = pygame.transform.scale(original_shape_image, (300, 400))
        else:
            print(f"لم يتم العثور على الصورة {index} في فولدر Shape!")
            pygame.quit()
            exit()

        # تحويل الصورة إلى رمادي
        gray_shape_image = self.convert_to_gray(original_shape_image)
        return letter_image, original_shape_image, gray_shape_image

    # دالة لتحويل الصورة إلى اللون الرمادي
    def convert_to_gray(self, image):
        gray_image = pygame.Surface(image.get_size())
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                r, g, b, a = image.get_at((x, y))
                gray_value = (r + g + b) // 3
                gray_image.set_at((x, y), (gray_value, gray_value, gray_value, a))
        return gray_image

    # دالة للتحقق إذا كانت النقطة على الحرف
    def is_near_letter(self, x, y, tolerance=20):
        for dx in range(-tolerance, tolerance):
            for dy in range(-tolerance, tolerance):
                try:
                    color = self.screen.get_at((x + dx, y + dy))
                    if color == self.BLACK:
                        return True
                except IndexError:
                    continue
        return False

    # دالة للتحقق من التتبع الصحيح
    def check_traced_correctly(self):
        for point in self.tracked_points:
            if not self.is_near_letter(point[0], point[1]):
                return False
        return True

    # الدالة الرئيسية لتشغيل اللعبة
    def run(self):
        running = True

        while running:
            self.screen.fill(self.WHITE)

            # عرض صورة الشكل (ملونة أو رمادية)
            self.screen.blit(self.original_shape_image if self.success else self.gray_shape_image, (50, 100))

            # عرض صورة الحرف
            self.screen.blit(self.letter_image, (600, 50))

            # رسم النقاط المتتبعة
            for point in self.tracked_points:
                pygame.draw.circle(self.screen, self.RED, point, 5)

            # عرض الإيموجي في منتصف الشاشة إذا كان يجب عرضه
            if self.show_emoji:
                self.screen.blit(self.current_emoji, (450, 10))  # إظهار الإيموجي في منتصف الشاشة

            # التحقق إذا كان الماوس مضغوطاً
            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                self.tracked_points.append((x, y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        if self.check_traced_correctly():
                            self.success = True
                            self.show_emoji = True
                            self.current_emoji = self.happy_emoji  # إظهار إيموجي الفرح
                            self.emoji_timer = pygame.time.get_ticks() + 4000  # عرض الإيموجي لمدة 4 ثوانٍ
                            print("تم تتبع الحرف بشكل صحيح!")

                            pygame.display.flip()
                            self.wait_time = pygame.time.get_ticks() + 7000  # انتظار 7 ثوانٍ
                        else:
                            self.success = False
                            self.show_emoji = True
                            self.current_emoji = self.sad_emoji  # إظهار إيموجي الحزن
                            self.emoji_timer = pygame.time.get_ticks() + 4000  # عرض إيموجي الحزن لمدة 4 ثوانٍ
                            print("التتبع غير صحيح! حاول مرة أخرى.")
                            self.tracked_points.clear()

                    if event.key == pygame.K_r:
                        self.tracked_points.clear()
                        self.success = False
                        self.show_emoji = False

            # إذا تحقق النجاح، انتظر 7 ثوانٍ ثم انتقل إلى الصورة التالية
            if self.success and pygame.time.get_ticks() > self.wait_time:
                self.image_index += 1
                if self.image_index > self.total_images:
                    print("تم الانتهاء من جميع الصور!")
                    running = False
                else:
                    self.letter_image, self.original_shape_image, self.gray_shape_image = self.load_images(self.image_index)
                    self.tracked_points.clear()
                    self.success = False
                    self.show_emoji = False

            # إخفاء الإيموجي بعد انتهاء المؤقت
            if pygame.time.get_ticks() > self.emoji_timer:
                self.show_emoji = False

            pygame.display.flip()

        pygame.quit()




class ArabicLetterLearning:
    def __init__(self):
        # إعداد مفتاح API داخل الكلاس مباشرة
        api_key = "AIzaSyDZVOpiDObZGkEtFgqzw_U-A4kPDzgFTYE"
        genai.configure(api_key=api_key)
        
        # قائمة الحروف العربية
        self.arabic_letters = [
            'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز',
            'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك',
            'ل', 'م', 'ن', 'ه', 'و', 'ي'
        ]
        self.displayed_letter = random.choice(self.arabic_letters)  # اختيار حرف عشوائي

    def extract_letter_from_image(self, image_path):
        # تحميل الصورة إلى النموذج
        file = genai.upload_file(image_path, mime_type="image/jpeg")
        
        # إعداد النص المطلوب للنموذج
        prompt = f"""
        Extract the Arabic letter present in the provided image. Output the letter only, no additional text.
        
        Image: {file.uri}
        """

        # إعداد النموذج والتوليد
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 1024,
                "response_mime_type": "text/plain",
            }
        )

        # استدعاء النموذج واستخراج الاستجابة
        response = model.generate_content([prompt])

        # إرجاع النص المستخرج (الحرف)
        return response.text.strip()

    def draw_text(self, image, text, position):
        # تحويل النص العربي ليظهر بشكل صحيح
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)

        # إنشاء صورة باستخدام PIL لرسم النص
        pil_img = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_img)
        
        # اختيار الخط (يجب التأكد من أن الخط يدعم العربية)
        font = ImageFont.truetype("arial.ttf", 32)  # تأكد من أن لديك الخط في النظام الخاص بك
        draw.text(position, bidi_text, font=font, fill=(0, 255, 0))
        
        # تحويل الصورة مرة أخرى إلى مصفوفة OpenCV
        return np.array(pil_img)

    def start_learning_session(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open the camera.")
            return

        # تحديد موقع المربع لالتقاط الصورة
        top_left = (100, 100)  # الزاوية العليا اليسرى للمربع
        bottom_right = (400, 400)  # الزاوية السفلى اليمنى للمربع

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture an image.")
                break

            # رسم المربع على الصورة
            cv2.rectangle(frame, top_left, bottom_right, (255, 0, 0), 2)

            # رسم الحرف المطلوب على الصورة
            frame_with_text = self.draw_text(frame.copy(), f"اكتب الحرف: {self.displayed_letter}", (frame.shape[1] - 250, 50))
            
            # عرض الإطار مع النص
            cv2.imshow('Arabic Letter Learning', frame_with_text)

            # التحقق من ضغط المفتاح 's' لالتقاط صورة، أو 'q' للخروج
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                # قص الصورة من المنطقة المحددة
                captured_image = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                image_path = "captured_image.jpg"
                cv2.imwrite(image_path, captured_image)  # حفظ الصورة من المربع
                
                # استخراج الحرف من الصورة الملتقطة
                extracted_letter = self.extract_letter_from_image(image_path)
                
                # مقارنة الحرفين وعرض النتيجة
                if self.displayed_letter == extracted_letter:
                    result_text = "الحرف صحيح!"
                else:
                    result_text = f"الحرف غير صحيح! الحرف المتوقع كان: {self.displayed_letter}, الحرف المستخرج: {extracted_letter}"
                
                # رسم النتيجة على الصورة مع النص
                frame_with_result = self.draw_text(frame.copy(), result_text, (frame.shape[1] - 400, 100))
                
                # عرض النتيجة للحظات ثم إنهاء البرنامج
                cv2.imshow('Arabic Letter Learning', frame_with_result)
                cv2.waitKey(3000)  # الانتظار لمدة 3 ثوانٍ قبل الإغلاق
                break

            elif key == ord('q'):
                print("تم إنهاء الجلسة.")
                break

        # تأكد من تحرير الكاميرا وإغلاق جميع النوافذ
        cap.release()
        cv2.destroyAllWindows()

