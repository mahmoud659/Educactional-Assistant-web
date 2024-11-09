from ibm_watsonx_ai.foundation_models import Model
import wikipediaapi
import nltk
from nltk.tokenize import word_tokenize

# تحميل مكتبة nltk إذا لم تكن محملة بالفعل
# nltk.download('punkt')

class WikipediaSummarizer:
    def __init__(self, max_words_per_part=500):
        # إعدادات نموذج IBM Watson
        self.model_id = "sdaia/allam-1-13b-instruct"
        self.parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        self.project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"
        self.max_words_per_part = max_words_per_part

    def get_credentials(self):
        # بيانات اعتماد لاستخدام نموذج IBM Watson
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }

    def fetch_wikipedia_content(self, topic, language='ar'):
        # إعداد ويكيبيديا باللغة المختارة
        user_agent = "MyWikipediaBot/1.0 (https://example.com; myemail@example.com)"
        wiki_wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language=language)

        # جلب المقالة
        page = wiki_wiki.page(topic)
        if page.exists():
            return page.text
        else:
            print("هذه المقالة غير موجودة.")
            return None

    def split_text_by_words(self, text):
        # تقسيم النص إلى أجزاء بناءً على عدد الكلمات المحدد
        words = word_tokenize(text)
        text_parts = []
        for i in range(0, len(words), self.max_words_per_part):
            part = ' '.join(words[i:i + self.max_words_per_part])
            text_parts.append(part)
        return text_parts

    def generate_summary_for_kids(self, text):
        # إنشاء كائن النموذج
        model = Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.get_credentials(),
            project_id=self.project_id
        )

        # تقسيم النص إلى أجزاء
        text_parts = self.split_text_by_words(text)
        summaries = []

        for idx, part in enumerate(text_parts):
            # برومبت للتلخيص للأطفال
            prompt_input = f"""[INST] أنت شات بوت مساعد للأطفال في تعلم اللغة العربية. مهمتك هي تقديم تلخيص واضح وسهل للأطفال حول الموضوع التالي: {part}. حاول أن يكون التلخيص بسيطًا وسهل الفهم. [INST]"""
            formatted_question = f"""<s> [INST] {prompt_input} [/INST]"""

            # توليد التلخيص
            generated_response = model.generate_text(prompt=formatted_question, guardrails=False)
            summaries.append(generated_response)

        # دمج الملخصات بتنسيق منظم
        full_summary = "\n\n".join(summaries)
        return full_summary

    def summarize_topic(self, topic):
        # جلب المحتوى من ويكيبيديا
        content = self.fetch_wikipedia_content(topic)
        if content:
            # تلخيص المحتوى للأطفال
            summary = self.generate_summary_for_kids(content)
            
            # عرض الملخص بالكامل
            print("\nملخص للمقال:\n", summary)
            return summary
        else:
            return "لم يتم العثور على محتوى للمقالة."



class ModelAllam2:
    def __init__(self):
        # إعداد بيانات اعتماد IBM Watson لاستخدام نموذج Allam
        self.credentials = {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }
        self.model_id = "sdaia/allam-1-13b-instruct"
        self.project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"
        self.parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        
        # إنشاء كائن النموذج
        self.model = Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.credentials,
            project_id=self.project_id
        )

    def generate_response(self, scenario, user_input):
        # إعداد البرومبت لتناسب السيناريو المطلوب
        prompt_input = f"[INST] {scenario} [INST] {user_input}"
        formatted_prompt = f"<s> [INST] {prompt_input} [/INST]"

        # توليد النص باستخدام نموذج Allam
        generated_response = self.model.generate_text(prompt=formatted_prompt, guardrails=False)
        return generated_response
 
    
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

class StoryTelling:
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

    # توليد النص بناءً على سؤال الطفل (موضوع القصه)
    def generate_story_from_ai(self, story_theme):
        prompt_input = """[INST] أنت مساعد ذكي للأطفال. مهمتك هي سرد قصة تعليمية بطريقة مبسطة وسهلة للأطفال.
        سأعطيك موضوعًا للقصة، عليك أن تكتب القصة بطريقة تناسب الأطفال وتكون المعلومات واضحة.

        الموضوع: "تعلم اللغة العربية من خلال القصص."
        [INST]"""
        
        formatted_story = f"""<s> [INST] {story_theme} [/INST]"""
        prompt = f"""{prompt_input}{formatted_story}"""
        generated_response = self.model.generate_text(prompt=prompt, guardrails=False)
        
        return generated_response

    # تحويل النص إلى صوت
    def speak(self, text, output_file):
        tts = gTTS(text=text, lang='ar')
        tts.save(output_file)

    # تحميل صورة خلفية عشوائية من مجلد خاص بالقصة
    def load_random_background_image(self, folder_path):
        images = [f for f in os.listdir(folder_path) if f.endswith('.jpeg') or f.endswith('.png')]
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

    # تشغيل الجلسة التعليمية مع القصة
    def start_story_telling_session(self, story_theme):
        # توليد النص
        story_text = self.generate_story_from_ai(story_theme)
        print(f"النص المولد للقصة: {story_text}")

        # تحويل النص إلى صوت
        audio_file = "story_output_audio.mp3"
        self.speak(story_text, audio_file)

        # تحميل صورة خلفية عشوائية من مجلد القصة
        background_folder = "Story Telling"  # المسار للمجلد الذي يحتوي على الصور الخاصة بالقصة
        background_image = self.load_random_background_image(background_folder)
        
        video_path = None  # تعريف متغير الفيديو
        if background_image:
            video_path = "story_final_video.mp4"
            self.create_video_with_background(audio_file, video_path, background_image)
            print(f"تم إنشاء الفيديو: {video_path}")
        else:
            print("لم يتم العثور على أي صور في المجلد المحدد.")

        return video_path, story_text  # إرجاع مسار الفيديو والنص المولد للقصة
