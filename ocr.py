import numpy as np
import cv2
from PIL import ImageGrab

class OCREngine:
    def __init__(self):
        try:
            from paddleocr import PaddleOCR
            import os
            # 强制使用CPU
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
            self.engine = PaddleOCR(
                use_textline_orientation=False,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                text_detection_model_name="PP-OCRv5_mobile_det",
                text_recognition_model_name="PP-OCRv5_mobile_rec"
            )
        except Exception as e:
            raise Exception(f"PaddleOCR引擎初始化失败：{str(e)}")
    
    def recognize(self, image: np.ndarray):
        try:
            results = self.engine.predict(image)
            texts = []
            for result in results:
                if isinstance(result, dict) and 'rec_texts' in result:
                    for text in result['rec_texts']:
                        # 删除所有空格
                        text = text.replace(' ', '')
                        # 处理包含"|"的文本，分割为多个结果
                        if '|' in text:
                            texts.extend([t.strip() for t in text.split('|') if t.strip()])
                        else:
                            texts.append(text)
                elif isinstance(result, list):
                    for line in result:
                        try:
                            text = line[1][0]
                            # 删除所有空格
                            text = text.replace(' ', '')
                            # 处理包含"|"的文本，分割为多个结果
                            if '|' in text:
                                texts.extend([t.strip() for t in text.split('|') if t.strip()])
                            else:
                                texts.append(text)
                        except:
                            pass
            return texts
        except Exception:
            return []
    
    def recognize_area(self, bbox):
        try:
            # 修正坐标
            x1, y1, x2, y2 = bbox
            # 将坐标转换为数字
            x1 = float(x1)
            y1 = float(y1)
            x2 = float(x2)
            y2 = float(y2)
            # 修正坐标顺序
            x1, x2 = (x1, x2) if x1 < x2 else (x2, x1)
            y1, y2 = (y1, y2) if y1 < y2 else (y2, y1)
            bbox = (x1, y1, x2, y2)
            
            # 截图
            screen_crop = ImageGrab.grab(bbox)
            crop_w, crop_h = screen_crop.size
            if crop_w < 10 or crop_h < 10:
                return []
            
            # 转换为OpenCV格式
            img = cv2.cvtColor(np.array(screen_crop, dtype=np.uint8), cv2.COLOR_RGB2BGR)
            if img is None or img.shape[0] < 10 or img.shape[1] < 10:
                return []
            
            # 识别
            return self.recognize(img)
        except Exception:
            return []