import streamlit as st
import os
from AR import ArucoGIFAugmenter  # استيراد الكلاس الخاص بالواقع المعزز
from Allam import Model_Allam  # استيراد الكلاس الخاص بمساعد علام
from Games import WordShootingGame, WordGuessingGame, WordGame, LetterCountGame, WordSortingGame, WordBoxGame, AnimalGuessingGame  # استيراد الألعاب من الملف Games
from ReadingLesson import ReadingLesson  # استيراد الكلاس
from EducationalLesson import LearningSession
from WrittingLesson import LetterTracingGame , ArabicLetterLearning
from SignLanguage import ArabicSignLanguageRecognition
import threading
from LastFile import WikipediaSummarizer , ModelAllam2 , StoryTelling 




# متغير عالمي لحفظ النص المسترجع من الموديل
response_text = ""

# وظيفة لتشغيل كلاس التعرف على لغة الإشارة للأطفال وتحديث النص في Streamlit
def run_asl_recognition():
    global response_text
    asl_recognition = ArabicSignLanguageRecognition()
    asl_recognition.run()
    response_text = asl_recognition.response_text



# عرض اسم البرنامج في أعلى الصفحة
st.markdown("<div style='text-align: center; font-size: 40px; font-weight: bold;'>Future Arab Speakers</div>", unsafe_allow_html=True)

# إضافة الاختيارات إلى السايد بار باستخدام radio
page = st.sidebar.radio(
    "اختر الصفحة التي تريد عرضها", 
    [
        "الصفحة الرئيسية", 
        "تقديم دروس تعليمية", 
        "تعليم الكتابة", 
        "تعليم القراءة", 
        "الألعاب", 
        "الواقع المعزز", 
        "المحاكاة", 
        "البحث و التلخيص" ,
        "أطفال الصم"
    ],
    index=0,  # الصفحة الرئيسية تظهر كاختيار افتراضي
)

# عرض المحتوى بناءً على الاختيار من السايد بار
if page == "الصفحة الرئيسية":
    st.markdown('<div style="text-align: right;"><h2>الصفحة الرئيسية</h2><p>مرحبًا بكم في Future Arab Speakers. اختر من السايد بار للوصول إلى المحتوى المطلوب.</p></div>', unsafe_allow_html=True)

elif page == "تقديم دروس تعليمية":
    st.markdown('<div style="text-align: right;"><h2>تقديم دروس تعليمية</h2><p>هذا القسم مخصص لتقديم دروس تعليمية في مجالات متعددة.</p></div>', unsafe_allow_html=True)
    # إنشاء كائن من الكلاس
    lesson_session = LearningSession()

    # إدخال السؤال
    question = st.text_input("أدخل السؤال التعليمي (مثل: أريد شرح المجموعة الشمسية):")

    if st.button("تقديم الدرس"):
        if question:
            video_path, ai_response = lesson_session.start_learning_session(question)

            # عرض النص المولد
            st.write("النص المولد:")
            st.write(ai_response)

            # عرض الفيديو
            if video_path:
                st.video(video_path)
            else:
                st.write("لم يتم إنشاء الفيديو.")
        else:
            st.warning("يرجى إدخال سؤال تعليمي.")
   

elif page == "تعليم الكتابة":
    st.markdown('<div style="text-align: right;"><h2>تعليم الكتابة</h2><p>هذا القسم مخصص لتعليم الأطفال كيفية الكتابة باللغة العربية.</p></div>', unsafe_allow_html=True)

    # صف أول لتشغيل لعبة تتبع الحروف
    st.markdown('<div style="text-align: right;"><h3>لعبة تتبع الحروف</h3></div>', unsafe_allow_html=True)
    if st.button("تشغيل لعبة تتبع الحروف"):
        tracing_game = LetterTracingGame()  # استدعاء كلاس اللعبة الأولى
        tracing_game.run()  # تشغيل لعبة تتبع الحروف

    # صف ثاني لتشغيل لعبة تعلم الحروف باستخدام arabicletterlearning
    st.markdown('<div style="text-align: right;"><h3>لعبة تعلم الحروف</h3></div>', unsafe_allow_html=True)
    if st.button("تشغيل لعبة تعلم الحروف"):
        st.write("ابدأ تعلم الحروف الآن")
        api_key = "AIzaSyDZVOpiDObZGkEtFgqzw_U-A4kPDzgFTYE"
        arabic_learning = ArabicLetterLearning()
        arabic_learning.start_learning_session()
        
        
elif page == "تعليم القراءة":
    st.markdown('<div style="text-align: right;"><h2>تعليم القراءة</h2><p>هذا القسم مخصص لتعليم الأطفال كيفية القراءة باللغة العربية.</p></div>', unsafe_allow_html=True)
    lesson = ReadingLesson()
    # بدء الدرس
    lesson.start_lesson()

elif page == "الألعاب":
    st.markdown('<div style="text-align: right;"><h2>الألعاب</h2><p>هذا القسم يحتوي على ألعاب تعليمية تساعد الأطفال في التعلم من خلال المرح.</p></div>', unsafe_allow_html=True)

   
    # لعبة 1: لعبة الكلمات
    st.markdown('<div style="text-align: right;"><h3>لعبة 1: لعبة الكلمات</h3><p>هذه اللعبة تساعد الأطفال في تعلم الكلمات بطريقة تفاعلية.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<p>يتم تفاعل الأطفال مع اللعبة عن طريق تحديد الحروف الصحيحة.</p>", unsafe_allow_html=True)
    with col2:
        if st.button("تشغيل لعبة 1"):
            st.write("جاري تشغيل لعبة 1...")
            
            word_game = WordGame()  # إنشاء كائن من لعبة الكلمات
            word_game.run_full_process()  

    st.divider()

    # لعبة 2: لعبة التخمين
    st.markdown('<div style="text-align: right;"><h3>لعبة 2: التعرف على الحروف المفقودة</h3><p>هذه اللعبة تساعد الأطفال في تخمين الحروف المفقودة من الكلمات باستخدام تقنيات تفاعلية.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<p>على الأطفال اختيار الحرف المفقود في الكلمة.</p>", unsafe_allow_html=True)
    with col2:
        if st.button("تشغيل لعبة 2"):
            st.write("جاري تشغيل لعبة 2...")
            guessing_game = WordGuessingGame()  # إنشاء كائن من لعبة التخمين
            guessing_game.play_game()  # تشغيل اللعبة

    st.divider()

    # لعبة 3: لعبة التصويب
    st.markdown('<div style="text-align: right;"><h3>لعبة 3: التصويب على الكلمات</h3><p>هذه اللعبة تساعد الأطفال في التعرف على الكلمات الصحيحة من خلال التصويب على الكلمة المستهدفة.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<p>على الأطفال التصويب على الكلمة الصحيحة باستخدام الحركة.</p>", unsafe_allow_html=True)
    with col2:
        if st.button("تشغيل لعبة 3"):
            st.write("جاري تشغيل لعبة 3...")
            shooting_game = WordShootingGame()  # إنشاء كائن من لعبة التصويب
            shooting_game.play_game()  # تشغيل اللعبة

    st.divider()

    # لعبة 4: لعبة العد
    st.markdown('<div style="text-align: right;"><h3>لعبة 4: عد الحروف</h3><p>هذه اللعبة تساعد الأطفال في عد الحروف في الجمل بطريقة تفاعلية.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<p>على الأطفال عد الحروف في الجملة والإجابة عن عدد مرات تكرار الحرف.</p>", unsafe_allow_html=True)
    with col2:
        if st.button("تشغيل لعبة 4"):
            st.write("جاري تشغيل لعبة 4...")
            letter_count_game = LetterCountGame()  # إنشاء كائن من لعبة عد الحروف
            letter_count_game.start_game()  # تشغيل اللعبة

    st.divider()

    st.markdown('<div style="text-align: right;"><h3>لعبة 5: تصنيف الكلمات</h3><p>هذه اللعبة تساعد الأطفال في تصنيف الكلمات إلى فئات مختلفة مثل الحيوانات، الفواكه، والألوان.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<p>على الأطفال تصنيف الكلمات إلى الفئات الصحيحة عن طريق وضع كل كلمة في السلة المناسبة.</p>", unsafe_allow_html=True)
    with col2:
        if st.button("تشغيل لعبة 5"):
            st.write("جاري تشغيل لعبة 5...")
            sorting_game = WordSortingGame()  # إنشاء كائن من لعبة تصنيف الكلمات
            sorting_game.run_game()  # تشغيل اللعبة

    st.divider()

    # لعبة 6: لعبة الصندوق
    st.markdown('<div style="text-align: right;"><h3>لعبة 6: صندوق الكلمات</h3><p>هذه اللعبة تساعد الأطفال في العثور على الكلمة الصحيحة من خلال اختيار الصندوق الصحيح.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<p>على الأطفال العثور على الكلمة الصحيحة من بين الصناديق.</p>", unsafe_allow_html=True)
    with col2:
        if st.button("تشغيل لعبة 6"):
            st.write("جاري تشغيل لعبة 6...")
            word_box_game = WordBoxGame()  # إنشاء كائن من لعبة الصندوق
            word_box_game.run_game()  # تشغيل اللعبة

    st.divider()

   # لعبة 7: لعبة تخمين الحيوانات
    st.markdown('<div style="text-align: right;"><h3>لعبة 7: تخمين الحيوانات</h3><p>هذه اللعبة تساعد الأطفال في التعرف على الحيوانات من خلال الصور والأوصاف.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<p>على الأطفال التعرف على الحيوان من خلال الصور المتاحة.</p>", unsafe_allow_html=True)
    with col2:
        if st.button("تشغيل لعبة 7"):
            st.write("جاري تشغيل لعبة 7...")
            animal_guessing_game = AnimalGuessingGame("animals.csv")  # إنشاء كائن من لعبة تخمين الحيوانات
            animal_guessing_game.run_full_process()  # تشغيل اللعبة

    st.divider()


elif page == "الواقع المعزز":
    st.markdown('<div style="text-align: right;"><h2>الواقع المعزز</h2></div>', unsafe_allow_html=True)

    # إضافة تبويبات تحت الواقع المعزز
    sub_tab = st.selectbox(
        "اختر الخيار المطلوب:", 
        ["الواقع المعزز", "مزيد من المعلومات"]
    )
    
    if sub_tab == "الواقع المعزز":
        st.markdown("""
            <div style="text-align: right;">
            <p>الواقع المعزز هو تقنية تهدف إلى دمج العالم الافتراضي مع العالم الحقيقي لتوفير تجربة تعلم فريدة.</p>
            <p>باستخدام الواقع المعزز، يمكن للطلاب رؤية الكائنات الافتراضية والتفاعل معها بشكل مباشر.</p>
            <p>اضغط على الزر أدناه للبدء في استخدام تقنية الواقع المعزز.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # التأكد من أن 'stop_signal' موجود في حالة الجلسة
        if 'stop_signal' not in st.session_state:
            st.session_state['stop_signal'] = False

        # زر البدء في الواقع المعزز
        start_button = st.button("البدء في استعمال الواقع المعزز", key="start_ar")

        # عند الضغط على الزر، يتم تفعيل الواقع المعزز
        if start_button:
            st.write("جاري تشغيل الواقع المعزز...")
            marker_path = os.path.join(os.getcwd(), "Markers")  # تحديد مسار ملفات Markers

            if os.path.exists(marker_path):
                st.write(f"تم العثور على المجلد: {marker_path}")
                try:
                    # إنشاء كائن من الكلاس الخاص بالواقع المعزز
                    augmenter = ArucoGIFAugmenter(marker_path)
                    video_placeholder = st.empty()  # مساحة لعرض الفيديو داخل Streamlit

                    # دالة لإيقاف الكاميرا
                    def stop_camera():
                        st.session_state['stop_signal'] = True

                    # إضافة زر إيقاف الكاميرا
                    stop_button = st.button("إيقاف الكاميرا", on_click=stop_camera)

                    # تشغيل الواقع المعزز
                    augmenter.run_streamlit(video_placeholder, lambda: st.session_state['stop_signal'])

                except Exception as e:
                    st.write(f"حدث خطأ أثناء تشغيل الواقع المعزز: {e}")
            else:
                st.write(f"المسار {marker_path} غير موجود.")
    
    elif sub_tab == "مزيد من المعلومات":
        # الشات بوت يظهر هنا داخل النافذة
        st.markdown("<h3 style='text-align: center;'>شات بوت مساعد</h3>", unsafe_allow_html=True)
        
        client = Model_Allam()

        # تخزين الرسائل في الجلسة
        if "messages" not in st.session_state:
            st.session_state["messages"] = []  # إلغاء الجملة الافتراضية

        # عرض الرسائل السابقة في الشات، مع جعل الرسائل الحديثة في الأسفل
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])

        # إدخال المستخدم في الجزء السفلي من الشاشة
        if prompt := st.chat_input("اكتب سؤالك هنا..."):
            # إضافة سؤال المستخدم إلى الجلسة
            st.session_state.messages.append({"role": "user", "content": prompt})

            # عرض السؤال فورًا
            st.chat_message("user").write(prompt)

            # توليد الرد من Model_Allam
            response = client.generate_info(prompt)
            
            # إضافة رد المساعد إلى الجلسة
            st.session_state.messages.append({"role": "assistant", "content": response})

            # عرض رد المساعد
            st.chat_message("assistant").write(response)

# محتوى "المحاكاة"
elif page == "المحاكاة":
    st.markdown('<div style="text-align: right;"><h2>المحاكاة</h2><p>هذا القسم مخصص لتعلم من خلال المحاكاة.</p></div>', unsafe_allow_html=True)
        # إنشاء كائن من ModelAllam
    client = ModelAllam2()

    # قائمة السيناريوهات المتاحة
    scenarios = {
        "1": "أنت طبيب في مستشفى وتتحدث مع مريض.",
        "2": "أنت معلم في مدرسة وتتحدث مع طالب.",
        "3": "أنت موظف استقبال في فندق وتتعامل مع نزيل.",
        "4": "أنت بائع في متجر وتتحدث مع زبون."
    }

        # اختيار السيناريو
    scenario_choice = st.selectbox("اختر السيناريو:", list(scenarios.values()) + ["سيناريو مخصص"])

    # إعادة بدء الشات عند تغيير السيناريو
    if "selected_scenario" not in st.session_state or st.session_state.selected_scenario != scenario_choice:
        st.session_state["messages"] = []  # إعادة تعيين الرسائل عند اختيار سيناريو جديد
        st.session_state.selected_scenario = scenario_choice  # تحديث السيناريو المختار

    if scenario_choice == "سيناريو مخصص":
        custom_scenario = st.text_input("أدخل وصف السيناريو المخصص:")
        scenario = custom_scenario
    else:
        scenario = scenario_choice

    # عرض الرسائل السابقة في الشات، مع جعل الرسائل الحديثة في الأسفل
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # إدخال المستخدم في الجزء السفلي من الشاشة
    if prompt := st.chat_input("اكتب سؤالك هنا..."):
        # إضافة سؤال المستخدم إلى الجلسة
        st.session_state.messages.append({"role": "user", "content": prompt})

        # عرض السؤال فورًا
        st.chat_message("user").write(prompt)

        # توليد الرد من ModelAllam
        response = client.generate_response(scenario, prompt)
        
        # إضافة رد المساعد إلى الجلسة
        st.session_state.messages.append({"role": "assistant", "content": response})

        # عرض رد المساعد
        st.chat_message("assistant").write(response)
    
    
# محتوى "البحث و التلخيص"
elif page == "البحث و التلخيص":
    st.markdown('<div style="text-align: right;"><h2>البحث و التلخيص</h2><p>هذا القسم مخصص للبحث والتلخيص في المواضيع المختلفة.</p></div>', unsafe_allow_html=True)
    # إدخال الموضوع من المستخدم
    topic = st.text_input("أدخل الموضوع الذي تريد البحث عنه وتلخيصه:")

    # زر البحث و التلخيص
    if st.button("البحث و التلخيص"):
        if topic:
            # إنشاء كائن من الفئة WikipediaSummarizer
            summarizer = WikipediaSummarizer(max_words_per_part=400)

            # استدعاء دالة التلخيص والحصول على الملخص
            summary = summarizer.summarize_topic(topic)

            # عرض الملخص
            st.write("### الملخص:")
            st.write(summary)
        else:
            st.write("يرجى إدخال موضوع للبحث والتلخيص.")


# محتوى "أطفال الصم"
elif page == "أطفال الصم":
    st.markdown('<div style="text-align: right;"><h2>أطفال الصم</h2><p>هذا القسم مخصص لتعليم الأطفال الصم لغة الإشارة.</p></div>', unsafe_allow_html=True)


  # زر التشغيل
    if st.button("تشغيل التعرف على لغة الإشارة للأطفال"):
        # تشغيل كلاس التعرف على لغة الإشارة في موضوع منفصل
        st.write("جاري التشغيل... يرجى الانتظار.")
        asl_thread = threading.Thread(target=run_asl_recognition)
        asl_thread.start()
        
        # الانتظار حتى ينتهي الموضوع من التشغيل
        asl_thread.join()
        
        # عرض النص المسترجع من الموديل بعد انتهاء التشغيل
        if response_text:
            st.write("النص المسترجع من الموديل:")
            st.write(response_text)