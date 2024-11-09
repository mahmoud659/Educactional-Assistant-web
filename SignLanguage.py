import pickle
import cv2
import mediapipe as mp
import numpy as np
import time
from PIL import ImageFont, ImageDraw, Image
import arabic_reshaper
from bidi.algorithm import get_display
from ibm_watsonx_ai.foundation_models import Model

class ArabicSignLanguageRecognition:
    def __init__(self):
        # Load model
        self.model_dict = pickle.load(open('./model.p', 'rb'))
        self.model = self.model_dict['model']

        # Configure the IBM Watsonx AI Allam model
        self.allam_model_id = "sdaia/allam-1-13b-instruct"
        self.parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        }
        self.project_id = "592f5af6-db2c-4c9f-9295-dcd1878c8d91"
        self.allam_model = Model(
            model_id=self.allam_model_id,
            params=self.parameters,
            credentials=self.get_credentials(),
            project_id=self.project_id
        )

        # Initialize video capture and Mediapipe
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

        # Arabic letters mapping with extra labels for space and delete
        self.arabic_labels = [
            "ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض",
            "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي", " ", "حذف"
        ]
        self.labels_dict = {i: self.arabic_labels[i] for i in range(len(self.arabic_labels))}

        # Initialize variables for detected letters
        self.sign_string = ""
        self.last_sign_time = time.time()
        self.inactive_threshold = 10
        self.letter_confirmation_time = 3
        self.display_time_after_send = 3  # Show sent sentence for 3 seconds

        self.current_letter = None
        self.letter_start_time = None
        self.response_text = ""
        self.response_received_time = None

        # Font for Arabic text
        font_path = "./arial.ttf"  # تأكد من مسار الخط العربي
        self.font = ImageFont.truetype(font_path, 40)  # تكبير حجم الخط

    def get_credentials(self):
        return {
            "url": "https://eu-de.ml.cloud.ibm.com",
            "apikey": "DCBw3LBA398DIxdje7pSVm2X0MmLSJJKfqUrAIZO8xOz"
        }

    def generate_text_from_ai(self, question):
        prompt_input = "[INST] أنت مساعد ذكي للأطفال. أجب فقط على السؤال الذي سيُطرح عليك بدون مقدمة. [INST]"
        formatted_question = f"<s> [INST] {question} [/INST]"
        prompt = f"{prompt_input}{formatted_question}"
        generated_response = self.allam_model.generate_text(prompt=prompt, guardrails=False)
        return generated_response

    def run(self):
        while True:
            data_aux = []
            x_ = []
            y_ = []

            ret, frame = self.cap.read()
            if not ret:
                break

            H, W, _ = frame.shape
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        x_.append(x)
                        y_.append(y)

                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        data_aux.append(x - min(x_))
                        data_aux.append(y - min(y_))

                    prediction = self.model.predict([np.asarray(data_aux)])
                    predicted_character = self.labels_dict[int(prediction[0])]

                    if predicted_character == self.current_letter:
                        if time.time() - self.letter_start_time > self.letter_confirmation_time:
                            if self.current_letter == "حذف":
                                self.sign_string = self.sign_string[:-1]
                            elif self.current_letter == " ":
                                self.sign_string += " "
                            else:
                                self.sign_string += self.current_letter
                            self.current_letter = None

                            x_min = int(min(x_) * W) - 10
                            y_min = int(min(y_) * H) - 10
                            x_max = int(max(x_) * W) + 10
                            y_max = int(max(y_) * H) + 10
                            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)

                    else:
                        self.current_letter = predicted_character
                        self.letter_start_time = time.time()

                        x_min = int(min(x_) * W) - 10
                        y_min = int(min(y_) * H) - 10
                        x_max = int(max(x_) * W) + 10
                        y_max = int(max(y_) * H) + 10
                        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 3)

                    reshaped_text = arabic_reshaper.reshape(predicted_character)
                    bidi_text = get_display(reshaped_text)
                    x1 = int(min(x_) * W) - 10
                    y1 = int(min(y_) * H) - 10

                    pil_img = Image.fromarray(frame)
                    draw = ImageDraw.Draw(pil_img)
                    draw.text((x1, y1 - 50), bidi_text, font=self.font, fill=(0, 0, 0))
                    frame = np.array(pil_img)

                self.last_sign_time = time.time()

            else:
                if time.time() - self.last_sign_time > self.inactive_threshold and self.sign_string:
                    # Display the accumulated sentence
                    reshaped_sentence = arabic_reshaper.reshape(self.sign_string)
                    bidi_sentence = get_display(reshaped_sentence)
                    pil_img = Image.fromarray(frame)
                    draw = ImageDraw.Draw(pil_img)
                    draw.text((W - 10 - len(bidi_sentence) * 20, 10), bidi_sentence, font=self.font, fill=(255, 0, 0))
                    frame = np.array(pil_img)

                    # Generate model response
                    self.response_text = self.generate_text_from_ai(self.sign_string.strip())
                    self.response_received_time = time.time()  # Store the time when response is received

                    # Print the response to the console
                    print("Response from Allam model:", self.response_text)

                    self.sign_string = ""  # Clear sign string after sending to model

            # Display the sentence for a fixed time after sending to model
            if self.response_received_time and (time.time() - self.response_received_time < self.display_time_after_send):
                reshaped_sentence = arabic_reshaper.reshape(self.sign_string)
                bidi_sentence = get_display(reshaped_sentence)
                pil_img = Image.fromarray(frame)
                draw = ImageDraw.Draw(pil_img)
                draw.text((W - 10 - len(bidi_sentence) * 20, 10), bidi_sentence, font=self.font, fill=(255, 0, 0))
                frame = np.array(pil_img)

            # Display the current accumulated letters on the screen
            if self.sign_string:
                reshaped_accumulated = arabic_reshaper.reshape(self.sign_string)
                bidi_accumulated = get_display(reshaped_accumulated)
                pil_img = Image.fromarray(frame)
                draw = ImageDraw.Draw(pil_img)
                draw.text((W - 10 - len(bidi_accumulated) * 20, 10), bidi_accumulated, font=self.font, fill=(255, 0, 0))
                frame = np.array(pil_img)

            cv2.imshow('frame', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


