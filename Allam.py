from ibm_watsonx_ai.foundation_models import Model

class Model_Allam:
    def get_credentials(self):
        # بيانات اعتماد لاستخدام نموذج IBM Watson
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }

    def generate_info(self, user_input):
        # إعدادات نموذج IBM Watson لتوليد ردود مخصصة بناءً على المدخلات
        model_id = "sdaia/allam-1-13b-instruct"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"

        # إنشاء الكائن الخاص بالنموذج باستخدام بيانات الاعتماد والمعلمات
        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=self.get_credentials(),
            project_id=project_id
        )

        # البرومبت المعدل لتقديم المعلومات وكأن المعلم يشرح للأطفال
        prompt_input = f"""[INST] أنت شات بوت مساعد للأطفال في تعلم اللغة العربية. مهمتك هي تقديم معلومات واضحة وسهلة للأطفال حول {user_input}. حاول أن تكون المعلومات بسيطة ومختصرة وسهلة الفهم. [INST]"""

        # تنسيق المدخلات لاستخدامها في النموذج
        formattedQuestion = f"""<s> [INST] {prompt_input} [/INST]"""
        generated_response = model.generate_text(prompt=formattedQuestion, guardrails=False)
        return generated_response
