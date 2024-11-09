import streamlit as st
import speech_recognition as sr
import random
from tashaphyne.stemming import ArabicLightStemmer
from ibm_watsonx_ai.foundation_models import Model
import re

class ArabicWordGenerator:
    def __init__(self):
        """إعداد بيانات الاعتماد"""
        self.model_id = "sdaia/allam-1-13b-instruct"
        self.project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"
        self.parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        self.credentials = {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }
    
    def get_credentials(self):
        return self.credentials

    def generate_words(self):
        """توليد الكلمات من النموذج"""
        model = Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.get_credentials(),
            project_id=self.project_id
        )

        prompt_input = """[INST] أنت شات بوت مساعد للأطفال في تعلم اللغة العربية. مهمتك هي تقديم كلمات بسيطة جدًا للأطفال تتكون من 3 إلى 4 حروف. عليك أن تقدم كل مرة 10 كلمات متنوعة وغير مكررة. الكلمات يجب أن تكون بين قوسين ومرتبة بهذا الشكل:
        [ كلمة - كلمة - كلمة - كلمة - كلمة - كلمة - كلمة - كلمة - كلمة - كلمة ]
        يجب أن تكون الكلمات مألوفة وسهلة للأطفال."
        مثال للإخراج المطلوب: [ قلم - شمس - قمر - ليل - موز - نهار - أهلا - كتاب - نور - نخل ] [/INST]"""
        
        formatted_question = f"<s> [INST] {prompt_input} [/INST]"
        generated_response = model.generate_text(prompt=formatted_question, guardrails=False)

        match = re.search(r'\[(.*?)\]', generated_response)
        if match:
            words = match.group(1).split(' - ')
        else:
            words = [ "كتاب", "قمر"]

        return words

class ReadingLesson:
    def __init__(self):
        """إعداد الموديل وتوليد الكلمات"""
        self.word_generator = ArabicWordGenerator()
        self.stemmer = ArabicLightStemmer()
        self.words = self.word_generator.generate_words()

    def recognize_speech_from_mic(self):
        """التعرف على الصوت باستخدام Google Web Speech API"""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("يرجى النطق بالكلمة...")
            audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio, language='ar-SA')
                return text
            except sr.UnknownValueError:
                st.error("لم أتمكن من فهم الصوت.")
                return None
            except sr.RequestError:
                st.error("هناك مشكلة في الاتصال بخدمة التعرف على الصوت.")
                return None

    def compare_words_using_stemmer(self, spoken_word, target_word):
        """حساب التشابه بين الكلمة المنطوقة والكلمة المستهدفة باستخدام تحليل الجذر"""
        spoken_stem = self.stemmer.light_stem(spoken_word)
        target_stem = self.stemmer.light_stem(target_word)

        return spoken_stem == target_stem

    def start_lesson(self):
        """تشغيل الدرس واختبار النطق للأطفال"""
        st.title("اختبار النطق للأطفال")

        # المتغير الذي يخزن الكلمة الحالية
        if 'current_word_index' not in st.session_state:
            st.session_state.current_word_index = 0

        # عرض الكلمة الحالية فقط
        if st.session_state.current_word_index < len(self.words):
            target_word = self.words[st.session_state.current_word_index]
            st.header(f"قل هذه الكلمة: {target_word}")

            if st.button("سجل نطقك"):
                spoken_word = self.recognize_speech_from_mic()

                if spoken_word:
                    st.write(f"لقد نطقت: {spoken_word}")

                    if self.compare_words_using_stemmer(spoken_word, target_word):
                        st.success("رائع! لقد نطقت الكلمة بشكل صحيح.")
                        st.session_state.current_word_index += 1
                        if st.session_state.current_word_index >= len(self.words):
                            st.write("انتهيت من جميع الكلمات. أحسنت!")
                    else:
                        st.error(f"آسف، الكلمة الصحيحة هي: {target_word}. حاول مرة أخرى.")
        else:
            st.write("تم الانتهاء من الكلمات. اضغط على إعادة البدء لبدء الدرس من جديد.")

        # زر لإعادة تعيين الدرس
        if st.button("إعادة البدء"):
            st.session_state.current_word_index = 0
            st.write("تمت إعادة الدرس، يمكنك البدء من جديد.")

