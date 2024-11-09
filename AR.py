import cv2
import cv2.aruco as aruco
import numpy as np
import os
from PIL import Image

class ArucoGIFAugmenter:
    def __init__(self, marker_path, slow_factor=4):
        # تحميل الصور من مسار المجلد
        self.augDics = self.loadAugImages(marker_path)

        # معامل البطء (يستخدم للتحكم في سرعة عرض الإطارات)
        self.slow_factor = slow_factor

        # عداد الإطارات للتحكم في الإطارات التي يتم عرضها
        self.frameCount = 0
        self.currentFrameIndex = 0

    def loadAugImages(self, path):
        """
        دالة لتحميل الصور المساعدة من مسار محدد. تقرأ ملفات GIF وتخزن كل إطار في قائمة.
        """
        myList = os.listdir(path)
        noOfMarkers = len(myList)
        print("Total Number of Markers Detected:", noOfMarkers)
        augDics = {}
        for imgPath in myList:
            # التحقق من أن الصورة بصيغة GIF
            imgPIL = Image.open(f'{path}/{imgPath}')

            if imgPIL.format != 'GIF':
                continue  # تخطي الصور التي ليست بصيغة GIF
            
            key = int(os.path.splitext(imgPath)[0])
            imgAug = []

            # قراءة الإطارات في صورة GIF
            for frame in range(0, imgPIL.n_frames):
                imgPIL.seek(frame)
                imgFrame = np.array(imgPIL.convert('RGB'))
                imgFrame = cv2.cvtColor(imgFrame, cv2.COLOR_RGB2BGR)
                imgAug.append(imgFrame)
            
            augDics[key] = imgAug  # تخزين إطارات GIF في القاموس
        return augDics

    def findArucoMarkers(self, img, markerSize=6, totalMarkers=250, draw=True):
        """
        دالة لاكتشاف علامات Aruco في الصورة وإرجاع المربعات الحدودية والـ ID الخاصة بها.
        """
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        try:
            key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
        except AttributeError:
            print(f"Invalid marker size or total markers: {markerSize}X{markerSize}_{totalMarkers}")
            return [], []

        arucoDict = aruco.getPredefinedDictionary(key)
        arucoParam = aruco.DetectorParameters()
        bboxes, ids, rejected = aruco.detectMarkers(imgGray, arucoDict, parameters=arucoParam)

        if draw:
            aruco.drawDetectedMarkers(img, bboxes)

        return [bboxes, ids]

    def augmentAruco(self, bbox, id, img, imgAugList, drawId=True, frameIndex=0):
        """
        دالة لإضافة تأثير الـ GIF على علامات Aruco المكتشفة.
        """
        imgAug = imgAugList[frameIndex % len(imgAugList)]  # اختيار الإطار الحالي بناءً على frameIndex
        tl = int(bbox[0][0][0]), int(bbox[0][0][1])
        tr = int(bbox[0][1][0]), int(bbox[0][1][1])
        br = int(bbox[0][2][0]), int(bbox[0][2][1])
        bl = int(bbox[0][3][0]), int(bbox[0][3][1])
        h, w, c = imgAug.shape

        # إعداد مصفوفة التحويل للإسقاط (Homography)
        pts1 = np.array([tl, tr, br, bl])
        pts2 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        matrix, _ = cv2.findHomography(pts2, pts1)

        # تطبيق الإسقاط على الإطار المحدد من الـ GIF
        imgOut = cv2.warpPerspective(imgAug, matrix, (img.shape[1], img.shape[0]))
        
        # إخفاء منطقة الـ Aruco الأصلية
        cv2.fillConvexPoly(img, pts1.astype(int), (0, 0, 0))

        # دمج الصورة الناتجة مع الإطار الأصلي
        imgOut = img + imgOut

        if drawId:
            # إضافة ID الـ Aruco إلى الصورة
            cv2.putText(imgOut, str(int(id[0])), tl, cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        return imgOut

    def run_streamlit(self, video_placeholder, stop_signal):
        """
        دالة تشغيل الكاميرا وعرض الفيديو داخل تطبيق Streamlit مع القدرة على إيقاف الكاميرا.
        """
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            success, img = cap.read()
            if not success:
                break

            # اكتشاف علامات Aruco
            arucoFound = self.findArucoMarkers(img)

            if len(arucoFound[0]) != 0:
                for bbox, id in zip(arucoFound[0], arucoFound[1]):
                    if int(id[0]) in self.augDics.keys():
                        if self.frameCount % self.slow_factor == 0:
                            self.currentFrameIndex = self.frameCount // self.slow_factor
                        img = self.augmentAruco(bbox, id, img, self.augDics[int(id[0])], frameIndex=self.currentFrameIndex)

            # عرض الفيديو داخل Streamlit باستخدام video_placeholder
            video_placeholder.image(img, channels="BGR")

            self.frameCount += 1

            # إيقاف الكاميرا إذا تم الضغط على زر الإيقاف
            if stop_signal():
                break

        cap.release()
