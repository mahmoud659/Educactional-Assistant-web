import pygame
from gtts import gTTS
from ibm_watsonx_ai.foundation_models import Model
from PIL import Image
import numpy as np
import moviepy.editor as mp
import os
import random

# إعداد مكتبة Pygame للصوت
pygame.mixer.init()

class LearningSession:
    def __init__(self):
        # إعداد نموذج WatsonX لتوليد النصوص
        self.model = self.setup_model()

    def setup_model(self):
        def get_credentials():
            return {
                "url": "https://eu-de.ml.cloud.ibm.com",
                "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
            }

        model_id = "sdaia/allam-1-13b-instruct"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }

        project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"

        return Model(
            model_id=model_id,
            params=parameters,
            credentials=get_credentials(),
            project_id=project_id
        )

    # توليد النص بناءً على سؤال الطفل
    def generate_text_from_ai(self, question):
        prompt_input = """[INST] أنت شات بوت مساعد للأطفال. مهمتك هي شرح موضوع علمي بطريقة مبسطة وسهلة للأطفال.
        سأعطيك موضوعًا لشرحه، عليك أن تكتب الشرح بطريقة تناسب الأطفال وتكون المعلومات واضحة.

        الموضوع: "المجموعة الشمسية". 
        [INST]"""
        
        formatted_question = f"""<s> [INST] {question} [/INST]"""
        prompt = f"""{prompt_input}{formatted_question}"""
        generated_response = self.model.generate_text(prompt=prompt, guardrails=False)
        
        return generated_response

    # تحويل النص إلى صوت
    def speak(self, text, output_file):
        tts = gTTS(text=text, lang='ar')
        tts.save(output_file)

    # تحميل صورة خلفية عشوائية من مجلد
    def load_random_background_image(self, folder_path):
        images = [f for f in os.listdir(folder_path) if f.endswith('.jpeg')]
        if images:
            selected_image = random.choice(images)
            return os.path.join(folder_path, selected_image)
        return None

    # إنشاء فيديو مع الخلفية دون كتابة النص داخله
    def create_video_with_background(self, audio_file, output_video, background_image_path):
        width, height = 1280, 720
        audio = mp.AudioFileClip(audio_file)

        background = Image.open(background_image_path).resize((width, height))
        frame = np.array(background)

        background_clip = mp.ImageClip(frame).set_duration(audio.duration)
        final_clip = background_clip.set_audio(audio)
        final_clip.write_videofile(output_video, fps=24)

    # تشغيل الجلسة التعليمية
    def start_learning_session(self, question):
        # توليد النص
        ai_response = self.generate_text_from_ai(question)
        print(f"النص المولد: {ai_response}")

        # تحويل النص إلى صوت
        audio_file = "output_audio.mp3"
        self.speak(ai_response, audio_file)

        # تحميل صورة خلفية عشوائية
        background_folder = "Photo Learning"  # المسار للمجلد الذي يحتوي على الصور
        background_image = self.load_random_background_image(background_folder)
        
        video_path = None  # تعريف متغير الفيديو
        if background_image:
            video_path = "final_video.mp4"
            self.create_video_with_background(audio_file, video_path, background_image)
            print(f"تم إنشاء الفيديو: {video_path}")
        else:
            print("لم يتم العثور على أي صور في المجلد المحدد.")

        return video_path, ai_response  # إرجاع مسار الفيديو والنص المولد
