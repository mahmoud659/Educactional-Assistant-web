import re
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from PIL import ImageFont, ImageDraw, Image
import arabic_reshaper
from bidi.algorithm import get_display
import random
import time
from ibm_watsonx_ai.foundation_models import Model
from gtts import gTTS
import io
import pygame
import base64
import pandas as pd


# اللعبة الاولى 
class WordGame:
    def __init__(self):
        # إعدادات الخط وحجم الشاشة
        self.fontpath = "arial.ttf"  # تأكد من أن مسار الخط صحيح
        self.font_size = 100  # تكبير حجم الخط
        self.width, self.height = 1280, 720  # حجم الشاشة
        self.spacing = 150  # المسافة بين الحروف
        self.box_y1 = self.height * 2 // 3  # تحديد موقع صندوق الإدخال في الثلث الأخير من الشاشة
        self.box_y2 = self.height * 2 // 3 + 80  # طول صندوق الإدخال
        self.box_x1 = 50  # الإحداثيات السفلية لصندوق الإدخال
        self.box_x2 = self.width - 50
        self.help_box_x1, self.help_box_y1, self.help_box_x2, self.help_box_y2 = 50, 50, 250, 150  # إعدادات صندوق المساعدة

    def get_credentials(self):
        # دالة لاسترجاع بيانات الاعتماد لاستخدام نموذج IBM Watson
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }

    def generate_words(self):
        # إعدادات نموذج IBM Watson وتوليد الكلمات
        model_id = "sdaia/allam-1-13b-instruct"  # معرف النموذج المستخدم
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,  # عدد الكلمات الجديدة المسموح بها
            "repetition_penalty": 1
        }
        project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"  # معرف المشروع

        # إنشاء الكائن الخاص بالنموذج باستخدام بيانات الاعتماد والمعلمات
        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=self.get_credentials(),
            project_id=project_id
        )

        # استخدام البرومبت كما تم تقديمه لتوليد الكلمات
        prompt_input = """[INST] أنت شات بوت مساعد للأطفال في تعلم اللغة العربية. مهمتك هي تقديم كلمات بسيطة جدًا للأطفال تتكون من 3 إلى 4 حروف. عليك أن تقدم كل مرة 10 كلمات متنوعة وغير مكررة. الكلمات يجب أن تكون بين قوسين ومرتبة بهذا الشكل:
        [ كلمة - كلمة - كلمة - ... ]
        يجب أن تكون الكلمات مألوفة وسهلة للأطفال."
        
        مثال للإخراج المطلوب: [ قلم - شمس - قمر - ليل - موز - نهار - أهلا - كتاب - نور - نخل ] </s><s> [INST]"""
        
        # تنسيق المدخلات لاستخدامها في النموذج
        formattedQuestion = f"""<s> [INST] {prompt_input} [/INST]"""
        generated_response = model.generate_text(prompt=formattedQuestion, guardrails=False)

        # استخدام التعبيرات النمطية لاستخراج الكلمات بين الأقواس
        match = re.search(r'\[(.*?)\]', generated_response)
        if match:
            words = match.group(1).split(' - ')  # استخراج الكلمات وفصلها
        else:
            words = ["باب", "كلب", "سيارة"]  # قائمة افتراضية في حالة عدم وجود نتيجة

        return words

    def play_game(self, words):
        # إعداد الكاميرا
        cap = cv2.VideoCapture(0)
        cap.set(3, self.width)  # ضبط عرض الفيديو
        cap.set(4, self.height)  # ضبط ارتفاع الفيديو

        # كاشف اليد
        detector = HandDetector(detectionCon=0.8)

        # تحميل الخط العربي مع تكبير الحجم
        font = ImageFont.truetype(self.fontpath, self.font_size)

        # توليد كلمة عشوائية
        current_word_index = 0
        target_word = words[current_word_index]
        letters = list(target_word)
        random.shuffle(letters)  # خلط الحروف بشكل عشوائي

        # تحديد موقع الحروف في الثلث الأول من الشاشة
        start_x = (self.width - (len(letters) - 1) * self.spacing) // 2
        letter_positions = [(start_x + i * self.spacing, self.height // 6) for i in range(len(letters))]

        # إعداد متغيرات اللعبة
        word_formed = []  # قائمة الحروف التي تم تشكيلها
        show_help_word = False  # متغير لتحديد ما إذا كان سيتم عرض كلمة المساعدة
        help_word_displayed = False  # متغير لتتبع عرض كلمة المساعدة
        result_display_time = None  # وقت إظهار النتيجة

        # بدء اللعبة
        while True:
            # التقاط الصورة من الكاميرا
            success, img = cap.read()
            if not success:
                break
            
            img = cv2.flip(img, 1)  # عكس الصورة لتحسين الحركة

            # العثور على اليدين
            hands, img = detector.findHands(img, flipType=False)

            # التحقق من وقت عرض النتيجة
            if result_display_time is not None:
                elapsed_time = time.time() - result_display_time
                if elapsed_time > 5:  # مدة 5 ثوانٍ
                    result_display_time = None
                    if "".join(word_formed) == target_word:
                        current_word_index += 1
                        if current_word_index < len(words):
                            # إذا كانت الكلمة صحيحة، الانتقال إلى الكلمة التالية
                            target_word = words[current_word_index]
                            letters = list(target_word)
                            random.shuffle(letters)
                            letter_positions = [(start_x + i * self.spacing, self.height // 6) for i in range(len(letters))]
                            word_formed = []
                            help_word_displayed = False
                        else:
                            break  # إنهاء اللعبة عند الانتهاء من جميع الكلمات
                    else:
                        # إعادة تعيين الحالة إذا كانت الكلمة غير صحيحة
                        word_formed = []
                        letters = list(target_word)
                        random.shuffle(letters)
                        letter_positions = [(start_x + i * self.spacing, self.height // 6) for i in range(len(letters))]
                        help_word_displayed = False
                else:
                    # عرض الصورة بدون أي تفاعل إذا كانت النتيجة معروضة
                    cv2.imshow("Game", img)
                    continue

            if hands:
                hand = hands[0]
                lmList = hand['lmList']
                cursor = lmList[8][:2]  # إحداثيات إصبع السبابة

                # التحقق من وجود اليد في صندوق المساعدة
                if self.help_box_x1 < cursor[0] < self.help_box_x2 and self.help_box_y1 < cursor[1] < self.help_box_y2:
                    if not help_word_displayed:
                        show_help_word = True  # إظهار الكلمة مرة واحدة فقط
                        help_word_displayed = True  # تعيين الكلمة كمعروضة بعد العرض الأول
                else:
                    show_help_word = False  # إخفاء الكلمة عند إخراج اليد من الصندوق
                
                # التحقق من اليد اليمنى
                p1 = lmList[8][:2]  # إحداثيات إصبع السبابة
                p2 = lmList[12][:2]  # إحداثيات إصبع الوسطى
                length, info, img = detector.findDistance(p1, p2, img)

                # سحب الحرف فقط عند قفل الأصابع
                if length < 60:
                    cursor = lmList[8][:2]  # إحداثيات الإصبع لتحديث موقع الحرف
                    for i, pos in enumerate(letter_positions):
                        x, y = pos
                        letter_rect = (x, y, x + self.spacing, y + self.font_size)

                        # إذا كانت الإحداثيات داخل موقع الحرف
                        if letter_rect[0] < cursor[0] < letter_rect[2] and letter_rect[1] < cursor[1] < letter_rect[3]:
                            letter_positions[i] = (cursor[0] - self.font_size // 2, cursor[1] - self.font_size // 2)

                            # التحقق من وضع الحرف في صندوق الإدخال
                            if self.box_x1 < cursor[0] < self.box_x2 and self.box_y1 < cursor[1] < self.box_y2:
                                if letters.count(letters[i]) > word_formed.count(letters[i]):  # التحقق من عدد التكرارات
                                    word_formed.append(letters[i])
                                    letter_positions[i] = (-100, -100)  # إخفاء الحرف بعد وضعه

            # رسم الحروف العشوائية
            img = self.draw_letters(img, letters, letter_positions, (255, 255, 255), font)  # لون الحروف الأبيض

            # رسم صندوق الإدخال
            img = self.draw_word_box(img, word_formed, (0, 255, 0), font)  # لون النص الأخضر

            # رسم صندوق المساعدة
            img = self.draw_help_box(img, show_help_word, target_word, font)

            # عرض النتيجة إذا كانت الكلمة مكتملة
            if len(word_formed) == len(target_word):
                if "".join(word_formed) == target_word:
                    img = self.display_result(img, "صحيح!", font)
                else:
                    img = self.display_result(img, "خطأ!", font)
                result_display_time = time.time()  # تعيين وقت عرض النتيجة

            # عرض الصورة
            cv2.imshow("Game", img)

            # إنهاء البرنامج عند الضغط على مفتاح "q"
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # إغلاق الكاميرا والنوافذ
        cap.release()
        cv2.destroyAllWindows()

    def draw_letters(self, img, letters, positions, color, font):
        # دالة لرسم الحروف العشوائية باستخدام Pillow
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)

        for i, letter in enumerate(letters):
            x, y = positions[i]
            reshaped_text = arabic_reshaper.reshape(letter)
            bidi_text = get_display(reshaped_text)
            draw.text((x, y), bidi_text, font=font, fill=color)

        return np.array(img_pil)

    def draw_word_box(self, img, word_formed, color, font):
        # دالة لرسم صندوق الإدخال
        cv2.rectangle(img, (self.box_x1, self.box_y1), (self.box_x2, self.box_y2), (0, 0, 255), 3)
        reshaped_word = arabic_reshaper.reshape("".join(word_formed))
        bidi_word = get_display(reshaped_word)

        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((self.box_x1 + 10, self.box_y1 + 10), bidi_word, font=font, fill=color)

        return np.array(img_pil)

    def display_result(self, img, result_message, font):
        # دالة لعرض النتيجة على الشاشة
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        reshaped_text = arabic_reshaper.reshape(result_message)
        bidi_text = get_display(reshaped_text)
        
        # حساب حجم النص باستخدام textbbox
        bbox = draw.textbbox((0, 0), bidi_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text((self.width // 2 - text_width // 2, self.height // 2 - text_height // 2), bidi_text, font=font, fill=(0, 255, 0, 255))
        return np.array(img_pil)

    def draw_help_box(self, img, show_word, target_word, font):
        # دالة لرسم صندوق المساعدة
        cv2.rectangle(img, (self.help_box_x1, self.help_box_y1), (self.help_box_x2, self.help_box_y2), (255, 0, 0), 3)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        if show_word:
            reshaped_help_word = arabic_reshaper.reshape(target_word)
            bidi_help_word = get_display(reshaped_help_word)
            draw.text((self.help_box_x1 + 10, self.help_box_y1 + 10), bidi_help_word, font=font, fill=(0, 255, 0))
        else:
            reshaped_help_word = arabic_reshaper.reshape("مساعدة")
            bidi_help_word = get_display(reshaped_help_word)
            draw.text((self.help_box_x1 + 10, self.help_box_y1 + 10), bidi_help_word, font=font, fill=(255, 255, 255))

        return np.array(img_pil)
    
    def run_full_process(self):
        words = self.generate_words()
        self.play_game(words)


# اللعبه الثانية حذف حرف من الكلمة 
class WordGuessingGame:
    def __init__(self):
        # إعداد الكاميرا والحجم والـ font
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.detector = HandDetector(detectionCon=0.8)
        self.fontpath = "arial.ttf"  # تأكد من أن مسار ملف الخط صحيح
        self.font_size = 100
        self.font = ImageFont.truetype(self.fontpath, self.font_size)
        self.words = self.get_words_from_model()  # جلب الكلمات من الموديل
        self.current_word_index = 0
        self.result_message = ""

    def get_credentials(self):
        # دالة لاسترجاع بيانات اعتماد IBM Watson
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }

    def get_words_from_model(self):
        # دالة لجلب الكلمات من الموديل بناءً على البرومبت المعطى
        model_id = "sdaia/allam-1-13b-instruct"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"

        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=self.get_credentials(),
            project_id=project_id
        )

        prompt_input = """[INST] أنت شات بوت مساعد للأطفال في تعلم اللغة العربية. مهمتك هي تقديم كلمات بسيطة جدًا للأطفال تتكون من 3 إلى 4 حروف. عليك أن تقدم كل مرة 10 كلمات متنوعة وغير مكررة. الكلمات يجب أن تكون بين قوسين ومرتبة بهذا الشكل:
        [ كلمة - كلمة - كلمة - ... ]
        يجب أن تكون الكلمات مألوفة وسهلة للأطفال."
        
        مثال للإخراج المطلوب: [ قلم - شمس - قمر - ليل - موز - نهار - أهلا - كتاب - نور - نخل ] </s><s> [INST]"""

        formatted_question = f"""<s> [INST] {prompt_input} [/INST]"""
        generated_response = model.generate_text(prompt=formatted_question, guardrails=False)

        # استخدام الـ regex لاستخراج الكلمات بين الأقواس
        match = re.search(r'\[(.*?)\]', generated_response)
        if match:
            words = match.group(1).split(' - ')
        else:
            words = ["باب", "كلب", "سيارة"]  # قائمة افتراضية في حالة الخطأ

        return words

    def get_new_word(self, index):
        # دالة لجلب كلمة جديدة بناءً على الفهرس
        if index < len(self.words):
            target_word = self.words[index]
            missing_letter_index = random.randint(0, len(target_word) - 1)
            missing_letter = target_word[missing_letter_index]
            display_word = list(target_word)
            display_word[missing_letter_index] = "_"

            # توليد خيارات الحروف
            letters_options = [missing_letter]
            while len(letters_options) < 4:
                random_letter = random.choice("ابجدهوز")
                if random_letter not in letters_options:
                    letters_options.append(random_letter)
            random.shuffle(letters_options)

            # تحديد مواقع الخيارات في الثلث الأول من الشاشة
            width, height = 1280, 720
            spacing = 150
            start_x = (width - (len(letters_options) - 1) * spacing) // 2
            option_positions = [(start_x + i * spacing, height // 6) for i in range(len(letters_options))]

            # تحديد صندوق الإدخال في الثلث الأخير من الشاشة
            box_x1 = 50
            box_y1 = height * 2 // 3
            return target_word, missing_letter, display_word, letters_options, option_positions, box_x1, box_y1, width, height
        else:
            return None

    def draw_letters(self, img, letters, positions, color):
        # دالة لرسم الحروف العشوائية
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        for i, letter in enumerate(letters):
            x, y = positions[i]
            reshaped_text = arabic_reshaper.reshape(letter)
            bidi_text = get_display(reshaped_text)
            draw.text((x, y), bidi_text, font=self.font, fill=color)
        return np.array(img_pil)

    def draw_word_with_missing_letter(self, img, word, color, box_x1, box_y1):
        # دالة لرسم الكلمة مع الحرف المفقود
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        reshaped_word = arabic_reshaper.reshape("".join(word))
        bidi_word = get_display(reshaped_word)
        draw.text((box_x1 + 10, box_y1 + 10), bidi_word, font=self.font, fill=color)
        return np.array(img_pil)

    def display_result(self, img, result_message, width, height):
        # دالة لعرض النتيجة على الشاشة
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        reshaped_text = arabic_reshaper.reshape(result_message)
        bidi_text = get_display(reshaped_text)
        draw.text((width // 2 - 200, height // 2 - 50), bidi_text, font=self.font, fill=(0, 255, 0, 255))
        return np.array(img_pil)

    def play_game(self):
        # بدء اللعبة
        new_word_data = self.get_new_word(self.current_word_index)
        if not new_word_data:
            self.cap.release()
            cv2.destroyAllWindows()
            return

        target_word, missing_letter, display_word, letters_options, option_positions, box_x1, box_y1, width, height = new_word_data

        while True:
            # التقاط الصورة من الكاميرا
            success, img = self.cap.read()
            if not success:
                break

            img = cv2.flip(img, 1)

            # العثور على اليدين
            hands, img = self.detector.findHands(img, flipType=False)

            if hands:
                hand = hands[0]
                if hand['type'] == 'Right':
                    lmList = hand['lmList']
                    p1 = lmList[8][:2]
                    p2 = lmList[12][:2]
                    length, info, img = self.detector.findDistance(p1, p2, img)

                    # سحب الحرف عند قفل الأصابع
                    if length < 60:
                        cursor = lmList[8][:2]
                        for i, pos in enumerate(option_positions):
                            x, y = pos
                            letter_rect = (x, y, x + self.font_size, y + self.font_size)
                            if letter_rect[0] < cursor[0] < letter_rect[2] and letter_rect[1] < cursor[1] < letter_rect[3]:
                                selected_letter = letters_options[i]
                                if selected_letter == missing_letter:
                                    self.result_message = "مبروك! الحرف صحيح."
                                    img = self.display_result(img, self.result_message, width, height)
                                    cv2.imshow("Game", img)
                                    cv2.waitKey(2000)
                                    self.current_word_index += 1
                                    if self.current_word_index >= len(self.words):
                                        break
                                    new_word_data = self.get_new_word(self.current_word_index)
                                    if new_word_data:
                                        target_word, missing_letter, display_word, letters_options, option_positions, box_x1, box_y1, width, height = new_word_data
                                else:
                                    self.result_message = "خطأ! حاول مرة أخرى."
                                    img = self.display_result(img, self.result_message, width, height)
                                    cv2.imshow("Game", img)
                                    cv2.waitKey(2000)

            if self.current_word_index >= len(self.words):
                break

            # رسم الحروف الخيارات
            img = self.draw_letters(img, letters_options, option_positions, (255, 0, 0))

            # رسم الكلمة مع الحرف المفقود
            img = self.draw_word_with_missing_letter(img, display_word, (0, 255, 0), box_x1, box_y1)

            # عرض الصورة
            cv2.imshow("Game", img)

            # إنهاء البرنامج عند الضغط على 'q'
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        # تحرير الكاميرا وإغلاق النوافذ
        self.cap.release()
        cv2.destroyAllWindows()

# اللعبة الثالثة اختيار الكلمة المسموعة 
class WordShootingGame:
    def __init__(self):
        # إعداد الكاميرا
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        # إعداد كاشف اليد
        self.detector = HandDetector(detectionCon=0.8, maxHands=1)

        # إعداد Pygame لتشغيل الصوت
        pygame.mixer.init()

        # تحميل الخط العربي
        self.fontpath = "arial.ttf"  # تأكد من استخدام مسار صحيح لملف الخط
        self.font = ImageFont.truetype(self.fontpath, 80)

        # سرعة تحرك الكلمات
        self.word_speed = 2

        # الحصول على الجمل من الموديل
        self.sentences = self.get_sentences_from_model()

    def get_credentials(self):
        # دالة لاسترجاع بيانات اعتماد IBM Watson
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }

    def get_sentences_from_model(self):
        # دالة لجلب الجمل من الموديل بناءً على البرومبت المعطى
        model_id = "sdaia/allam-1-13b-instruct"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"

        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=self.get_credentials(),
            project_id=project_id
        )

        # إعداد البرومبت الخاص بتوليد الجمل
        prompt_input = """[INST] أنت شات بوت مساعد للأطفال في تعلم اللغة العربية. مهمتك هي تقديم جمل بسيطة للأطفال. عليك أن تقدم كل مرة 5 جمل متنوعة وغير مكررة. الجمل يجب أن تكون بين قوسين ومرتبة بهذا الشكل:
        [ جملة 1 - جملة 2 - جملة 3 - جملة 4 - جملة 5 ]
        يجب أن تكون الجمل مألوفة وسهلة للأطفال."
        
        مثال للإخراج المطلوب: [ أنا أرتدي القميص الأبيض - هذه هي ساعة والدتي - هناك ماء في البحيرة - أنا أسمع الموسيقى - الأصدقاء يلعبون كرة القدم ] </s><s> [INST]"""

        formatted_question = f"""<s> [INST] {prompt_input} [/INST]"""
        generated_response = model.generate_text(prompt=formatted_question, guardrails=False)

        # استخدام التعبيرات النمطية لاستخراج الجمل بين الأقواس
        match = re.search(r'\[(.*?)\]', generated_response)
        if match:
            sentences = match.group(1).split(' - ')
        else:
            sentences = ["أنت هنا", "جملة أخرى", "مثال لجملة"]  # قائمة افتراضية في حالة الخطأ

        return sentences

    def speak(self, text):
        # دالة لتحويل النص إلى صوت باستخدام gTTS
        tts = gTTS(text=text, lang='ar')
        with io.BytesIO() as audio_file:
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            pygame.mixer.music.load(audio_file, 'mp3')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

    def draw_words(self, img, words, positions):
        # دالة لرسم الكلمات المتحركة على الشاشة
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        for i, word in enumerate(words):
            reshaped_word = arabic_reshaper.reshape(word)
            bidi_word = get_display(reshaped_word)
            draw.text(positions[i], bidi_word, font=self.font, fill=(255, 0, 0))
        return np.array(img_pil)

    def display_result(self, img, message):
        # دالة لعرض نتيجة اختيار الكلمة على الشاشة
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        reshaped_message = arabic_reshaper.reshape(message)
        bidi_message = get_display(reshaped_message)
        # حساب حجم النص باستخدام textbbox
        text_bbox = draw.textbbox((0, 0), bidi_message, font=self.font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text(((1280 - text_width) / 2, (720 - text_height) / 2), bidi_message, font=self.font, fill=(0, 255, 0))
        return np.array(img_pil)

    def play_game(self):
        # بدء اللعبة
        for sentence in self.sentences:
            words = sentence.split()  # تقسيم الجملة إلى كلمات
            word_positions = [(random.randint(100, 1100), random.randint(100, 500)) for _ in words]

            target_word = random.choice(words)  # اختيار كلمة مستهدفة بشكل عشوائي

            # تحويل النص إلى صوت
            self.speak(f"اختر كلمة {target_word}")

            word_correct = False  # متغير لتحديد إذا تم اختيار الكلمة الصحيحة

            while not word_correct:  # الاستمرار حتى اختيار الكلمة الصحيحة
                # التقاط الصورة من الكاميرا
                success, img = self.cap.read()
                img = cv2.flip(img, 1)  # عكس الصورة لتحسين الحركة
                img_height, img_width, _ = img.shape

                # العثور على اليد
                hands, img = self.detector.findHands(img, flipType=False)

                # تحريك الكلمات
                for i in range(len(word_positions)):
                    word_positions[i] = (word_positions[i][0], word_positions[i][1] + self.word_speed)
                    if word_positions[i][1] > img_height:
                        word_positions[i] = (random.randint(100, 1100), -50)  # إعادة تعيين الكلمة لأعلى الشاشة

                # رسم الكلمات المتحركة
                img = self.draw_words(img, words, word_positions)

                # التحقق من التصويب بإصبع السبابة
                if hands:
                    hand = hands[0]
                    lmList = hand['lmList']  # قائمة المعالم (landmarks) لليد
                    index_finger_pos = lmList[8][:2]  # إحداثيات إصبع السبابة

                    for i, pos in enumerate(word_positions):
                        word_rect = (pos[0], pos[1], pos[0] + 200, pos[1] + 80)  # افتراض حجم الكلمة 200x80
                        if word_rect[0] < index_finger_pos[0] < word_rect[2] and word_rect[1] < index_finger_pos[1] < word_rect[3]:
                            if words[i] == target_word:
                                result_message = "مبروك! لقد اخترت الكلمة الصحيحة."
                                img = self.display_result(img, result_message)
                                self.speak(result_message)
                                cv2.imshow("Word Shooting Game", img)
                                cv2.waitKey(2000)
                                word_correct = True  # تم اختيار الكلمة الصحيحة، الانتقال إلى الجملة التالية
                                break
                            else:
                                result_message = "خطأ! حاول مرة أخرى."
                                img = self.display_result(img, result_message)
                                self.speak(result_message)
                                cv2.imshow("Word Shooting Game", img)
                                cv2.waitKey(2000)
                                break

                # عرض الصورة
                cv2.imshow("Word Shooting Game", img)

                # التحكم في الإغلاق
                key = cv2.waitKey(1)
                if key == ord('q'):
                    self.cap.release()
                    cv2.destroyAllWindows()
                    pygame.quit()
                    return

        # تحرير الكاميرا وإغلاق النوافذ
        self.cap.release()
        cv2.destroyAllWindows()
        pygame.quit()


# اللعبة الرابعة عد عدد الاحرف
class LetterCountGame:
    def __init__(self):
        # إعداد الكاميرا
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        # كاشف اليد
        self.detector = HandDetector(detectionCon=0.8, maxHands=1)

        # تحميل الخط العربي
        self.fontpath = "arial.ttf"  # تأكد من استخدام مسار صحيح لملف الخط
        self.font = ImageFont.truetype(self.fontpath, 50)

        # إعداد الموديل لتوليد الجمل
        self.sentences = self.generate_sentence_from_model()

    def get_credentials(self):
        # دالة لاسترجاع بيانات اعتماد IBM Watson
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }

    def generate_sentence_from_model(self):
        # دالة لتوليد الجمل باستخدام نموذج IBM Watson
        model_id = "sdaia/allam-1-13b-instruct"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"
        
        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=self.get_credentials(),
            project_id=project_id
        )
        
        # إعداد البرومبت الخاص بتوليد الجمل
        prompt_input = """[INST] أنت شات بوت مساعد للأطفال في تعلم اللغة العربية. مهمتك هي تقديم جمل بسيطة للأطفال. عليك أن تقدم كل مرة 5 جمل متنوعة وغير مكررة. الجمل يجب أن تكون بين قوسين ومرتبة بهذا الشكل:
        [ جملة 1 - جملة 2 - جملة 3 - جملة 4 - جملة 5 ]
        يجب أن تكون الجمل مألوفة وسهلة للأطفال." </s><s> [INST]"""
        
        formatted_question = f"""<s> [INST] {prompt_input} [/INST]"""
        generated_response = model.generate_text(prompt=formatted_question, guardrails=False)
        
        # استخدام التعبيرات النمطية لاستخراج الجمل بين الأقواس
        match = re.search(r'\[(.*?)\]', generated_response)
        if match:
            sentences = match.group(1).split(' - ')
        else:
            sentences = ["الجملة الافتراضية"]  # قائمة افتراضية في حالة الخطأ

        return sentences

    def select_random_letter(self, sentence):
        # دالة لاختيار حرف عشوائي من الجملة
        letter = random.choice(list(set(sentence.replace(" ", ""))))
        letter_count = sentence.count(letter)
        return letter, letter_count

    def generate_options(self, correct_answer):
        # توليد الخيارات بحيث لا يتكرر الرقم الصحيح
        options = random.sample(range(1, 10), 3)  # توليد 3 أرقام عشوائية
        while correct_answer in options:  # التحقق من عدم تكرار الرقم الصحيح
            options = random.sample(range(1, 10), 3)
        options.append(correct_answer)  # إضافة الرقم الصحيح
        random.shuffle(options)  # خلط الخيارات
        return options

    def draw_text(self, img, text, position, color, font_size):
        # دالة لرسم النص على الصورة
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        font = ImageFont.truetype(self.fontpath, font_size)
        draw.text(position, bidi_text, font=font, fill=color)
        return np.array(img_pil)

    def draw_game_elements(self, img, sentence, options, letter, selected_option=None):
        # دالة لرسم الجملة وخيارات الإجابة في صناديق
        img = self.draw_text(img, f"الجملة: {sentence}", (50, 50), (255, 255, 255), 50)
        img = self.draw_text(img, f"كم مرة ظهر حرف '{letter}' في الجملة؟", (50, 120), (255, 255, 255), 50)

        # رسم خيارات الإجابة في صناديق
        box_width = 200
        box_height = 60
        spacing = 20
        start_y = 200
        for i, option in enumerate(options):
            y_position = start_y + i * (box_height + spacing)
            color = (0, 255, 0) if selected_option == option else (255, 255, 255)
            img = self.draw_text(img, str(option), (60, y_position + 10), color, 50)
            cv2.rectangle(img, (50, y_position), (50 + box_width, y_position + box_height), color, 2)
            
        return img

    def start_game(self):
        # دالة اللعبة الرئيسية
        if not self.sentences:
            print("لا توجد جمل للتعلم.")
            return

        sentence_index = 0

        while sentence_index < len(self.sentences):
            sentence = self.sentences[sentence_index]
            letter, letter_count = self.select_random_letter(sentence)
            options = self.generate_options(letter_count)  # توليد خيارات الإجابة
            selected_option = None
            answered_correctly = False  # متغير لتتبع ما إذا تم الإجابة بشكل صحيح

            while not answered_correctly:  # الاستمرار حتى يتم الإجابة بشكل صحيح
                # التقاط الصورة من الكاميرا
                success, img = self.cap.read()
                
                if not success:
                    print("فشل في التقاط الصورة من الكاميرا.")
                    break

                img = cv2.flip(img, 1)  # عكس الصورة لتحسين الحركة
                img_height, img_width, _ = img.shape

                # العثور على اليد
                hands, img = self.detector.findHands(img, flipType=False)

                # رسم الجملة وخيارات الإجابة
                img = self.draw_game_elements(img, sentence, options, letter, selected_option)

                # التحقق من التصويب بإصبع السبابة
                if hands:
                    hand = hands[0]
                    lmList = hand['lmList']  # قائمة المعالم (landmarks) لليد
                    index_finger_pos = lmList[8][:2]  # إحداثيات إصبع السبابة

                    # التحقق من الاختيارات
                    box_width = 200
                    box_height = 60
                    spacing = 20
                    start_y = 200
                    for i, option in enumerate(options):
                        option_rect = (50, start_y + i * (box_height + spacing), 50 + box_width, start_y + (i + 1) * (box_height + spacing))
                        if option_rect[0] < index_finger_pos[0] < option_rect[2] and option_rect[1] < index_finger_pos[1] < option_rect[3]:
                            selected_option = option
                            if option == letter_count:
                                img = self.draw_text(img, "مبروك! لقد اخترت الإجابة الصحيحة.", (50, img_height - 100), (0, 255, 0), 50)
                                cv2.imshow("Count the Letters Game", img)
                                cv2.waitKey(2000)  # الانتظار لمدة 2 ثانية قبل الانتقال إلى الجملة التالية
                                answered_correctly = True  # تم الإجابة بشكل صحيح، الخروج من الحلقة الداخلية
                                break
                            else:
                                img = self.draw_text(img, "خطأ! حاول مرة أخرى.", (50, img_height - 100), (0, 0, 255), 50)

                # عرض الصورة
                cv2.imshow("Count the Letters Game", img)

                # التحكم في الإغلاق
                key = cv2.waitKey(1)
                if key == ord('q'):
                    return  # إنهاء اللعبة عند الضغط على 'q'

            # الانتقال إلى الجملة التالية بعد الإجابة الصحيحة
            sentence_index += 1

        # تحرير الكاميرا وإغلاق النوافذ
        self.cap.release()
        cv2.destroyAllWindows()

# اللعبة الخامسة اخذ كل كلمة ووضعها فى السلة المناسبة لها 
class WordSortingGame:
    def __init__(self):
        # إعداد الكاميرا
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        # كاشف اليد
        self.detector = HandDetector(detectionCon=0.8)

        # تحميل الخط العربي مع تكبير الحجم
        self.fontpath = "arial.ttf"  # تأكد من استخدام مسار صحيح لملف الخط
        self.font_size = 50
        self.font = ImageFont.truetype(self.fontpath, self.font_size)

        # توليد الكلمات والفئات من الموديل
        self.words_categories = self.generate_words_from_model()

        # اختيار 6 كلمات عشوائية من قائمة الكلمات
        self.all_words = [word for words in self.words_categories.values() for word in words]
        self.selected_words = random.sample(self.all_words, min(6, len(self.all_words)))

        # إعداد المواقع على الشاشة
        self.width, self.height = 1280, 720
        self.word_positions = []
        self.spacing = 200  # زيادة المسافة بين الكلمات
        self.start_x = (self.width - (len(self.selected_words) - 1) * self.spacing) // 2
        for i, word in enumerate(self.selected_words):
            x = self.start_x + i * self.spacing
            y = self.height // 6
            self.word_positions.append((x, y))

        # إعداد السلال
        self.basket_width, self.basket_height = 200, 100
        self.basket_positions = {
            category: (50 + i * (self.width // 3), self.height - self.basket_height - 50)
            for i, category in enumerate(self.words_categories.keys())
        }

        self.classified_words_set = set()  # مجموعة لتتبع الكلمات المصنفة

    def get_credentials(self):
        # دالة لاسترجاع بيانات اعتماد IBM Watson
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }

    def generate_words_from_model(self):
        # دالة لتوليد الكلمات من الموديل
        model_id = "sdaia/allam-1-13b-instruct"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"
        
        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=self.get_credentials(),
            project_id=project_id
        )
        
        # تعديل البرومبت لتوليد الكلمات حسب الفئات
        prompt_input = """[INST] أنت شات بوت مساعد للأطفال في تعلم اللغة العربية. مهمتك هي تقديم كلمات مقسمة حسب الفئات التالية: "حيوانات"، "فواكه"، و"ألوان". يجب أن تقدم كل فئة مع كلمتين فقط بشكل منسق كالتالي:
        {"حيوانات": ["قطة", "كلب"], "فواكه": ["تفاح", "موز"], "ألوان": ["أحمر", "أزرق"]}
        تأكد من أن الكلمات بسيطة ومناسبة للأطفال الصغار للتعلم. 
        أعد النتائج بهذا الشكل المنظم فقط:
        {"حيوانات": ["كلمة1", "كلمة2"], "فواكه": ["كلمة3", "كلمة4"], "ألوان": ["كلمة5", "كلمة6"]} [/INST]"""
        
        formatted_question = f"""<s> [INST] {prompt_input} [/INST]"""
        generated_response = model.generate_text(prompt=formatted_question, guardrails=False)

        # استخدام التعبيرات النمطية لاستخراج الكلمات والفئات
        try:
            words_categories = eval(generated_response)  # تحويل النص إلى صيغة قاموس
            if isinstance(words_categories, dict):
                return words_categories
        except:
            return {
                "حيوانات": ["قطة", "كلب"],
                "فواكه": ["تفاح", "موز"],
                "ألوان": ["أحمر", "أزرق"]
            }  # قائمة افتراضية في حالة الخطأ

    def draw_words(self, img, words, positions, color):
        # دالة لرسم الكلمات على الصورة
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        for i, word in enumerate(words):
            x, y = positions[i]
            reshaped_text = arabic_reshaper.reshape(word)
            bidi_text = get_display(reshaped_text)
            draw.text((x, y), bidi_text, font=self.font, fill=color)
        return np.array(img_pil)

    def draw_baskets(self, img):
        # دالة لرسم السلال
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        for category, (x, y) in self.basket_positions.items():
            draw.rectangle([x, y, x + self.basket_width, y + self.basket_height], outline="blue", width=3)
            reshaped_text = arabic_reshaper.reshape(category)
            bidi_text = get_display(reshaped_text)
            bbox = draw.textbbox((x, y), bidi_text, font=self.font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text((x + self.basket_width // 2 - text_width // 2, y + self.basket_height // 2 - text_height // 2), bidi_text, font=self.font, fill="blue")
        return np.array(img_pil)

    def run_game(self):
        # بدء اللعبة
        while True:
            # التقاط الصورة من الكاميرا
            success, img = self.cap.read()
            if not success:
                break
            
            img = cv2.flip(img, 1)  # عكس الصورة لتحسين الحركة

            # العثور على اليدين
            hands, img = self.detector.findHands(img, flipType=False)

            if hands:
                hand = hands[0]
                if hand['type'] == 'Right':  # التحقق من أن اليد اليمنى هي التي تتحرك
                    lmList = hand['lmList']
                    p1 = lmList[8][:2]
                    p2 = lmList[12][:2]
                    length, info, img = self.detector.findDistance(p1, p2, img)

                    if length < 60:
                        cursor = lmList[8][:2]
                        for i, pos in enumerate(self.word_positions):
                            x, y = pos
                            word_rect = (x, y, x + self.font_size * len(self.selected_words[i]), y + self.font_size)
                            if word_rect[0] < cursor[0] < word_rect[2] and word_rect[1] < cursor[1] < word_rect[3]:
                                self.word_positions[i] = (cursor[0] - self.font_size // 2, cursor[1] - self.font_size // 2)

                                for category, (bx, by) in self.basket_positions.items():
                                    if bx < cursor[0] < bx + self.basket_width and by < cursor[1] < by + self.basket_height:
                                        if self.selected_words[i] in self.words_categories[category]:
                                            if self.selected_words[i] not in self.classified_words_set:
                                                self.classified_words_set.add(self.selected_words[i])
                                                self.word_positions[i] = (-100, -100)  # إخفاء الكلمة
                                            break

            # عرض الكلمات المتبقية فقط
            remaining_words = [w for w in self.selected_words if w not in self.classified_words_set]
            img = self.draw_words(img, remaining_words, [self.word_positions[self.selected_words.index(w)] for w in remaining_words], (255, 0, 0))

            # رسم السلال
            img = self.draw_baskets(img)

            # التحقق من إنهاء اللعبة
            if len(self.classified_words_set) == len(self.selected_words):
                img_pil = Image.fromarray(img)
                draw = ImageDraw.Draw(img_pil)
                congrats_message = "ممتاز! لقد قمت بعمل رائع."
                reshaped_text = arabic_reshaper.reshape(congrats_message)
                bidi_text = get_display(reshaped_text)
                draw.text((self.width // 2, self.height // 2), bidi_text, font=self.font, fill=(0, 255, 0))
                img = np.array(img_pil)
                cv2.imshow("Game", img)
                cv2.waitKey(5000)
                break

            cv2.imshow("Game", img)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

# اللعبة السادسة الذاكرة بالكلمات 
class WordBoxGame:
    def __init__(self):
        # إعداد الكاميرا
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        # كاشف اليد
        self.detector = HandDetector(detectionCon=0.8)

        # تحميل الخط العربي
        self.fontpath = "arial.ttf"
        self.font_size = 30
        self.font = ImageFont.truetype(self.fontpath, self.font_size)

        # إعداد الصناديق والكلمات
        self.words = self.generate_words_from_model()
        self.num_boxes = 3  # عدد الصناديق المطلوب
        self.box_size = 100
        self.spacing = 120
        self.width, self.height = 1280, 720

        # تحديد مواقع الصناديق
        self.box_positions = [(self.width // 2 - self.box_size // 2, i * self.spacing + 50) for i in range(self.num_boxes)]

    def get_credentials(self):
        # دالة لجلب بيانات اعتماد IBM Watson
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }

    def generate_words_from_model(self):
        # دالة لجلب الكلمات من الموديل باستخدام مكتبة re
        model_id = "sdaia/allam-1-13b-instruct"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"

        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=self.get_credentials(),
            project_id=project_id
        )

        prompt_input = """[INST] أنت شات بوت مساعد للأطفال في تعلم اللغة العربية. مهمتك هي تقديم كلمات مقسمة حسب الفئات التالية: "حيوانات"، "فواكه"، و"ألوان". يجب أن تقدم 3 كلمات مناسبة فقط:
        {"كلمة1", "كلمة2", "كلمة3"} [/INST]"""

        formatted_question = f"""<s> [INST] {prompt_input} [/INST]"""
        generated_response = model.generate_text(prompt=formatted_question, guardrails=False)

        # استخدام التعبيرات النمطية لاستخراج الكلمات بين القوسين
        match = re.search(r'\{(.*?)\}', generated_response)
        if match:
            words_list = match.group(1).split(", ")
            if len(words_list) == 3:
                return words_list

        return ["قطة", "كلب", "تفاح"]  # قائمة افتراضية في حالة الخطأ

    def draw_boxes(self, img, words, positions, show_words):
        # دالة لرسم الصناديق والكلمات
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        for i, pos in enumerate(positions):
            x, y = pos
            if show_words:
                reshaped_text = arabic_reshaper.reshape(words[i])
                bidi_text = get_display(reshaped_text)
                draw.rectangle([x, y, x + self.box_size, y + self.box_size], fill=(0, 255, 0), outline=(0, 0, 0))
                draw.text((x + 10, y + 10), bidi_text, font=self.font, fill=(0, 0, 0))
            else:
                draw.rectangle([x, y, x + self.box_size, y + self.box_size], fill=(0, 255, 0), outline=(0, 0, 0))
        return np.array(img_pil)

    def display_text(self, img, text, pos):
        # دالة لعرض النص على الشاشة
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        draw.text(pos, bidi_text, font=self.font, fill=(0, 0, 255))
        return np.array(img_pil)

    def run_game(self):
        # بدء اللعبة
        start_time = time.time()
        show_words = True
        word_to_find = ""
        word_pos = -1

        while True:
            success, img = self.cap.read()
            if not success:
                break

            img = cv2.flip(img, 1)  # عكس الصورة لتحسين الحركة

            elapsed_time = time.time() - start_time
            remaining_time = max(10 - int(elapsed_time), 0)  # الوقت المتبقي 10 ثوانٍ

            if remaining_time > 0:
                img = self.draw_boxes(img, self.words, self.box_positions, True)
                img = self.display_text(img, f"الوقت المتبقي: {remaining_time}", (10, 10))
            else:
                img = self.draw_boxes(img, self.words, self.box_positions, False)
                if show_words:
                    word_to_find = random.choice(self.words)
                    word_pos = self.words.index(word_to_find)
                    show_words = False

                img = self.display_text(img, f"ابحث عن: {word_to_find}", (self.width - 300, 10))

                hands, img = self.detector.findHands(img, flipType=False)
                if hands:
                    hand = hands[0]
                    if hand['type'] == 'Right':
                        lmList = hand['lmList']
                        p1 = lmList[8][:2]
                        p2 = lmList[12][:2]
                        length, _, img = self.detector.findDistance(p1, p2, img)

                        if length < 60:
                            cursor = lmList[8][:2]
                            for i, pos in enumerate(self.box_positions):
                                x, y = pos
                                if x < cursor[0] < x + self.box_size and y < cursor[1] < y + self.box_size:
                                    if i == word_pos:
                                        result_message = "صحيح! لقد وجدت الكلمة."
                                    else:
                                        result_message = "خطأ! حاول مرة أخرى."

                                    img = self.display_text(img, result_message, (self.width // 2 - 150, self.height // 2))
                                    cv2.imshow("Game", img)
                                    cv2.waitKey(2000)
                                    if i == word_pos:
                                        return  # إنهاء اللعبة عند الحل الصحيح
                                    show_words = True
                                    start_time = time.time()
                                    break

            cv2.imshow("Game", img)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

# اللعبة السابعة ربط المعلومة بالصورة المناسبة
class AnimalGuessingGame:
    def __init__(self, csv_file):
        # تحميل بيانات الحيوانات من ملف CSV
        self.animal_data = self.load_animal_data(csv_file)

        # إعداد الكاميرا
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        # كاشف اليد
        self.detector = HandDetector(detectionCon=0.8)

        # تحميل الخط العربي
        self.fontpath = "arial.ttf"  # تأكد من أن المسار صحيح
        self.font_size = 40  # حجم الخط
        self.font = ImageFont.truetype(self.fontpath, self.font_size)

    def get_credentials(self):
        # دالة لجلب بيانات اعتماد IBM Watson
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"  # ضع مفتاح API هنا
        }

    def load_animal_data(self, csv_file):
        # دالة لتحميل بيانات الحيوانات من ملف CSV
        return pd.read_csv(csv_file)

    def base64_to_image(self, base64_string):
        # دالة لتحويل الصورة من Base64 إلى OpenCV
        image_data = base64.b64decode(base64_string)
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img

    def get_animal_info(self, animal_name):
        # دالة لجلب وصف الحيوان من الموديل
        model_id = "sdaia/allam-1-13b-instruct"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"

        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=self.get_credentials(),
            project_id=project_id
        )

        # برومبت الموديل لجلب وصف الحيوان
        prompt_input = f"""[INST] مهمتك هي تقديم وصف لحيوان معين. الوصف يجب أن يكون سهل الفهم للأطفال ويتكون من جملتين. لا يجب أن تذكر اسم الحيوان في الإجابة، والإجابة يجب أن تكون داخل القوسين المربعين هكذا:
        "[وصف الحيوان]"
        حتى لو وصل اسم الحيوان بالإنجليزية، يجب أن ترد بالعربية. اسم الحيوان المطلوب: {animal_name}</s><s> [INST]"""

        formatted_question = f"<s> [INST] {prompt_input} [/INST]"
        generated_response = model.generate_text(prompt=formatted_question, guardrails=False)

        # استخدام التعبيرات النمطية لاستخراج الوصف
        match = re.search(r'\[(.*?)\]', generated_response)
        if match:
            description = match.group(1)
        else:
            description = "وصف غير متاح في الوقت الحالي."

        return description

    def resize_image(self, img, size=(150, 150)):
        # دالة لتغيير حجم الصورة
        return cv2.resize(img, size)

    def play_game(self):
        # بدء تشغيل اللعبة

        while True:
            # اختيار حيوان عشوائي
            selected_animal = self.animal_data.sample(n=1).iloc[0]
            animal_name = selected_animal['اسم الحيوان']
            animal_image_base64 = selected_animal['صورة']
            animal_info = self.get_animal_info(animal_name)

            # عرض معلومات الحيوان في الكونسول
            print(f"معلومات عن {animal_name}: {animal_info}")

            # اختيار 3 صور عشوائية بالإضافة إلى الصورة الصحيحة
            images = [animal_image_base64] + random.sample(self.animal_data['صورة'].tolist(), 3)
            random.shuffle(images)

            # تحويل الصور من Base64 إلى OpenCV وتغيير حجمها
            image_objects = [self.resize_image(self.base64_to_image(img)) for img in images]

            while True:
                success, img = self.cap.read()
                img = cv2.flip(img, 1)

                # العثور على اليدين
                hands, img = self.detector.findHands(img, flipType=False)

                # عرض المعلومات
                img_pil = Image.fromarray(img)
                draw = ImageDraw.Draw(img_pil)
                reshaped_text = arabic_reshaper.reshape(animal_info)
                bidi_text = get_display(reshaped_text)
                draw.text((50, 50), bidi_text, font=self.font, fill=(255, 255, 255))
                img = np.array(img_pil)

                # عرض الصور على الشاشة
                for i, img_object in enumerate(image_objects):
                    h, w = img_object.shape[:2]
                    x = (i % 2) * 640 + 50  # 2 صور في كل صف
                    y = (i // 2) * 360 + 150
                    img[y:y + h, x:x + w] = img_object

                # التحقق من يد الطفل
                if hands:
                    lmList = hands[0]['lmList']
                    index_finger = lmList[8][:2]  # إحداثيات إصبع السبابة
                    middle_finger = lmList[12][:2]  # إحداثيات إصبع الوسط

                    # التحقق من الضغط على الصورة الصحيحة
                    for i, img_object in enumerate(image_objects):
                        h, w = img_object.shape[:2]
                        x = (i % 2) * 640 + 50
                        y = (i // 2) * 360 + 150

                        if x < index_finger[0] < x + w and y < index_finger[1] < y + h and \
                           x < middle_finger[0] < x + w and y < middle_finger[1] < y + h:
                            if images[i] == animal_image_base64:
                                img = self.display_result(img, "صحيح!")
                                cv2.imshow("Game", img)
                                time.sleep(5)
                                self.cap.release()  # إغلاق الكاميرا
                                cv2.destroyAllWindows()  # إنهاء اللعبة
                                return
                            else:
                                img = self.display_result(img, "خطأ!")
                                cv2.imshow("Game", img)
                                time.sleep(5)  # عرض النتيجة لبضع ثوانٍ
                                break

                cv2.imshow("Game", img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            self.cap.release()
            cv2.destroyAllWindows()

    def display_result(self, img, result_message):
        # دالة لعرض النتيجة على الشاشة
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        reshaped_text = arabic_reshaper.reshape(result_message)
        bidi_text = get_display(reshaped_text)

        draw.text((640, 360), bidi_text, font=ImageFont.truetype("arial.ttf", 60), fill=(0, 255, 0))
        return np.array(img_pil)

    def run_full_process(self):
        # دالة لتشغيل العملية بالكامل
        self.play_game()




