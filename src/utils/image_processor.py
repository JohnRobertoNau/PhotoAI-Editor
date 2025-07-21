from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2

class ImageProcessor:
    """Clasă pentru procesarea de bază a imaginilor."""
    
    def __init__(self):
        pass
    
    def resize_for_display(self, image, max_width=800, max_height=600):
        """
        Redimensionează imaginea pentru afișare în UI.
        
        Args:
            image (PIL.Image): Imaginea de redimensionat
            max_width (int): Lățimea maximă
            max_height (int): Înălțimea maximă
        
        Returns:
            PIL.Image: Imaginea redimensionată
        """
        try:
            if not isinstance(image, Image.Image):
                raise ValueError("Input-ul trebuie să fie o imagine PIL")
            
            # Calculează factorul de scalare
            width_ratio = max_width / image.width
            height_ratio = max_height / image.height
            scale_factor = min(width_ratio, height_ratio, 1.0)  # Nu mări imaginea
            
            if scale_factor < 1.0:
                new_width = int(image.width * scale_factor)
                new_height = int(image.height * scale_factor)
                return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            print(f"Eroare la redimensionarea pentru afișare: {e}")
            return image
    
    def enhance_brightness(self, image, factor=1.2):
        """
        Ajustează luminozitatea imaginii.
        
        Args:
            image (PIL.Image): Imaginea de procesat
            factor (float): Factorul de luminozitate (1.0 = original)
        
        Returns:
            PIL.Image: Imaginea cu luminozitatea ajustată
        """
        try:
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(factor)
        except Exception as e:
            print(f"Eroare la ajustarea luminozității: {e}")
            return image
    
    def enhance_contrast(self, image, factor=1.2):
        """
        Ajustează contrastul imaginii.
        
        Args:
            image (PIL.Image): Imaginea de procesat
            factor (float): Factorul de contrast (1.0 = original)
        
        Returns:
            PIL.Image: Imaginea cu contrastul ajustat
        """
        try:
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)
        except Exception as e:
            print(f"Eroare la ajustarea contrastului: {e}")
            return image
    
    def enhance_saturation(self, image, factor=1.2):
        """
        Ajustează saturația imaginii.
        
        Args:
            image (PIL.Image): Imaginea de procesat
            factor (float): Factorul de saturație (1.0 = original)
        
        Returns:
            PIL.Image: Imaginea cu saturația ajustată
        """
        try:
            enhancer = ImageEnhance.Color(image)
            return enhancer.enhance(factor)
        except Exception as e:
            print(f"Eroare la ajustarea saturației: {e}")
            return image
    
    def apply_blur(self, image, radius=2):
        """
        Aplică un efect de blur imaginii.
        
        Args:
            image (PIL.Image): Imaginea de procesat
            radius (int): Raza de blur
        
        Returns:
            PIL.Image: Imaginea cu blur aplicat
        """
        try:
            return image.filter(ImageFilter.GaussianBlur(radius=radius))
        except Exception as e:
            print(f"Eroare la aplicarea blur-ului: {e}")
            return image
    
    def apply_sharpen(self, image):
        """
        Aplică un efect de ascuțire imaginii.
        
        Args:
            image (PIL.Image): Imaginea de procesat
        
        Returns:
            PIL.Image: Imaginea ascuțită
        """
        try:
            return image.filter(ImageFilter.SHARPEN)
        except Exception as e:
            print(f"Eroare la ascuțirea imaginii: {e}")
            return image
    
    def rotate_image(self, image, angle):
        """
        Rotește imaginea cu un unghi specificat.
        
        Args:
            image (PIL.Image): Imaginea de rotit
            angle (float): Unghiul de rotație în grade
        
        Returns:
            PIL.Image: Imaginea rotită
        """
        try:
            return image.rotate(angle, expand=True)
        except Exception as e:
            print(f"Eroare la rotirea imaginii: {e}")
            return image
    
    def flip_horizontal(self, image):
        """
        Întoarce imaginea orizontal.
        
        Args:
            image (PIL.Image): Imaginea de întors
        
        Returns:
            PIL.Image: Imaginea întorsă
        """
        try:
            return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        except Exception as e:
            print(f"Eroare la întoarcerea orizontală: {e}")
            return image
    
    def flip_vertical(self, image):
        """
        Întoarce imaginea vertical.
        
        Args:
            image (PIL.Image): Imaginea de întors
        
        Returns:
            PIL.Image: Imaginea întorsă
        """
        try:
            return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        except Exception as e:
            print(f"Eroare la întoarcerea verticală: {e}")
            return image
    
    def crop_image(self, image, left, top, right, bottom):
        """
        Decupează o porțiune din imagine.
        
        Args:
            image (PIL.Image): Imaginea de decupat
            left, top, right, bottom (int): Coordonatele zonei de decupat
        
        Returns:
            PIL.Image: Imaginea decupată
        """
        try:
            return image.crop((left, top, right, bottom))
        except Exception as e:
            print(f"Eroare la decuparea imaginii: {e}")
            return image
    
    def convert_to_grayscale(self, image):
        """
        Convertește imaginea la tonuri de gri.
        
        Args:
            image (PIL.Image): Imaginea de convertit
        
        Returns:
            PIL.Image: Imaginea în tonuri de gri
        """
        try:
            return image.convert('L').convert('RGB')
        except Exception as e:
            print(f"Eroare la conversia în tonuri de gri: {e}")
            return image
    
    def apply_sepia(self, image):
        """
        Aplică un efect sepia imaginii.
        
        Args:
            image (PIL.Image): Imaginea de procesat
        
        Returns:
            PIL.Image: Imaginea cu efect sepia
        """
        try:
            # Convertește la numpy array
            img_array = np.array(image.convert('RGB'))
            
            # Aplicăm transformarea sepia
            sepia_filter = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            
            sepia_img = img_array.dot(sepia_filter.T)
            sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
            
            return Image.fromarray(sepia_img)
            
        except Exception as e:
            print(f"Eroare la aplicarea efectului sepia: {e}")
            return image
    
    def get_image_histogram(self, image):
        """
        Calculează histograma imaginii.
        
        Args:
            image (PIL.Image): Imaginea de analizat
        
        Returns:
            dict: Histogramele pentru fiecare canal de culoare
        """
        try:
            if image.mode == 'RGB':
                r, g, b = image.split()
                return {
                    'red': r.histogram(),
                    'green': g.histogram(),
                    'blue': b.histogram()
                }
            elif image.mode == 'L':
                return {'gray': image.histogram()}
            else:
                return {}
                
        except Exception as e:
            print(f"Eroare la calcularea histogramei: {e}")
            return {}
    
    def auto_enhance(self, image):
        """
        Îmbunătățește automat imaginea (auto levels, contrast, etc.).
        
        Args:
            image (PIL.Image): Imaginea de îmbunătățit
        
        Returns:
            PIL.Image: Imaginea îmbunătățită
        """
        try:
            # Convertește la numpy pentru procesare
            img_array = np.array(image.convert('RGB'))
            
            # Aplicăm auto-levels pentru fiecare canal
            enhanced = np.zeros_like(img_array)
            
            for i in range(3):  # R, G, B
                channel = img_array[:, :, i]
                
                # Calculăm percentilele 1% și 99%
                p1, p99 = np.percentile(channel, [1, 99])
                
                # Întindem histograma
                if p99 > p1:
                    enhanced[:, :, i] = np.clip(
                        255 * (channel - p1) / (p99 - p1), 0, 255
                    )
                else:
                    enhanced[:, :, i] = channel
            
            result = Image.fromarray(enhanced.astype(np.uint8))
            
            # Aplică o ușoară îmbunătățire a contrastului
            result = self.enhance_contrast(result, 1.1)
            
            return result
            
        except Exception as e:
            print(f"Eroare la auto-îmbunătățire: {e}")
            return image
