import cv2
import numpy as np
from PIL import Image
from mss import mss
import threading


class ImageDetector:
    def __init__(self):
        """初始化图像检测器"""
        # 为每个线程创建单独的 mss 实例，解决线程安全问题
        self.local = threading.local()
        # 模板图像缓存
        self.template_cache = {}
    
    def _get_sct(self):
        """获取当前线程的 mss 实例"""
        if not hasattr(self.local, 'sct'):
            self.local.sct = mss()
        return self.local.sct
    
    def grab_region(self, region: tuple) -> Image.Image:
        """
        截取指定区域的屏幕
        
        Args:
            region: 区域坐标 (x1, y1, x2, y2)，其中 (x1, y1) 是左上角，(x2, y2) 是右下角
        
        Returns:
            PIL.Image: 截取的图像
        """
        # 将浮点数坐标转换为整数
        x1, y1, x2, y2 = map(int, region)
        width = x2 - x1
        height = y2 - y1
        
        # 获取当前线程的 mss 实例
        sct = self._get_sct()
        
        # 检查坐标是否在任何屏幕范围内
        for monitor in sct.monitors[1:]:  # 跳过 monitors[0] (所有屏幕的汇总)
            if (monitor["left"] <= x1 < monitor["left"] + monitor["width"] and
                    monitor["top"] <= y1 < monitor["top"] + monitor["height"]):
                # 坐标已经是绝对坐标，直接截图
                screenshot = sct.grab({
                    "left": x1,
                    "top": y1,
                    "width": width,
                    "height": height
                })
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra,
                                      "raw", "BGRX")
                return img
        
        # 如果没有找到匹配的屏幕，使用原始坐标
        screenshot = sct.grab({
            "left": x1,
            "top": y1,
            "width": width,
            "height": height
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return img
    
    def match_template(self, image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> bool:
        """
        在图像中匹配模板
        
        Args:
            image: 待匹配的图像
            template: 模板图像
            threshold: 匹配阈值，默认0.8
        
        Returns:
            bool: 是否匹配成功
        """
        if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
            return False
        
        # 使用归一化平方差匹配方法
        result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 对于TM_SQDIFF_NORMED，值越小匹配度越高
        if min_val < (1 - threshold):
            return True
        
        return False
    
    def detect_logo(self, region: tuple[int, int, int, int], logo_path: str, threshold: float = 0.7) -> bool:
        """
        检测指定区域内是否存在指定的logo
        
        Args:
            region: 区域坐标 (x1, y1, x2, y2)
            logo_path: logo图像的路径
            threshold: 匹配阈值，默认0.7（降低阈值提高匹配率）
        
        Returns:
            bool: 是否检测到logo
        """
        try:
            # 截取屏幕区域
            screen_img = self.grab_region(region)
            screen_np = np.array(screen_img)
            screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
            
            # 使用缓存加载模板
            template = self._load_template(logo_path)
            if template is None:
                return False
            
            # 优化尺度匹配，优先检查常用尺度
            scales = np.linspace(0.5, 1.5, 10)
            
            for scale in scales:
                # 调整模板大小
                resized_template = cv2.resize(template, (
                    int(template.shape[1] * scale), 
                    int(template.shape[0] * scale)
                ))
                
                # 检查模板大小是否合适
                if resized_template.shape[0] > screen_gray.shape[0] or resized_template.shape[1] > screen_gray.shape[1]:
                    continue
                
                # 匹配模板
                result = cv2.matchTemplate(screen_gray, resized_template, cv2.TM_SQDIFF_NORMED)
                min_val, _, _, _ = cv2.minMaxLoc(result)
                
                # 对于TM_SQDIFF_NORMED，值越小匹配度越高
                if min_val < (1 - threshold):
                    return True
            
            return False
        except:
            return False
    
    def _load_template(self, logo_path: str):
        """加载模板图像，带缓存机制"""
        if logo_path in self.template_cache:
            return self.template_cache[logo_path]
        
        template = cv2.imread(logo_path, cv2.IMREAD_GRAYSCALE)
        if template is not None:
            self.template_cache[logo_path] = template
        
        return template
