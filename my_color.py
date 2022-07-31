from pygame import Color

def new_hue(hue, rotation):
    add = True
    if rotation < 0:
        rotation = -rotation
        add = False
    for i in range(0, rotation):
        hue = (hue + 1, hue - 1)[add == False]
        if hue >= 360:
            hue -= 360
    return (hue, 360 + hue)[hue < 0]

class myColor(Color):
    def __init__(self, rgb : tuple[int, int, int]):
        super().__init__(rgb[0], rgb[1], rgb[2])
    
    def complementary_color(self, lightness=-1):
        self.r = 255 - self.r
        self.g = 255 - self.g
        self.b = 255 - self.b
        if lightness >= 0 and lightness <= 100:
            self.hsla = (self.hsla[0], self.hsla[1], lightness, self.hsla[3])
    
    def analogous_colors(self, theme, lightness=-1):
        h, s, l, a = self.hsla
        if lightness >= 0 and lightness <= 100:
            l = lightness
        rotation = (30, -30)[theme=="Analogous 2"]
        self.hsla = (new_hue(h, rotation), s, l, a)
    
    def triadic_colors(self, theme, lightness=-1):
        h, s, l, a = self.hsla
        if lightness >= 0 and lightness <= 100:
            l = lightness
        rotation = (135, -135)[theme=="Triadic 2"]
        self.hsla = (new_hue(h, rotation), s, l, a)
    
    def tetradic_colors(self, theme, lightness=-1):
        h, s, l, a = self.hsla
        if lightness >= 0 and lightness <= 100:
            l = lightness
        rotation = (90, -90)[theme=="Tetradic 2"]
        self.hsla = (new_hue(h, rotation), s, l, a)
    
    def complementary_analogous_colors(self, theme, lightness=-1):
        h, s, l, a = self.hsla
        if lightness >= 0 and lightness <= 100:
            l = lightness
        rotation = (150, -150)[theme=="Comp-analogous 2"]
        self.hsla = (new_hue(h, rotation), s, l, a)
    
    def set_hue(self, degree : float):
        degree = (degree, 0)[degree < 0 or degree >= 360]
        self.hsla = (degree, self.hsla[1], self.hsla[2], self.hsla[3])
    
    def set_saturation(self, percentage : float, unless_grey=False):
        if unless_grey == True and (self.r == self.g == self.b):
            return
        if percentage < 0:
            percentage = 0
        elif percentage > 100:
            percentage = 100
        self.hsla = (self.hsla[0], percentage, self.hsla[2], self.hsla[3])
    
    def set_lightness(self, percentage : float):
        if percentage < 0:
            percentage = 0
        elif percentage > 100:
            percentage = 100
        self.hsla = (self.hsla[0], self.hsla[1], percentage, self.hsla[3])
    
    def multiply_lightness(self, percentage : float):
        if percentage < 0:
            return
        percentage = percentage / 100
        h, s, l, a = self.hsla
        l = (l * percentage, 100)[l * percentage > 100]
        self.hsla = (h, s, l, a)
    
    def emplify_lightness(self, percentage : float):
        percentage = percentage / 100
        h, s, l, a = self.hsla
        if percentage <= 0:
            return
        if l < 50:
            l = (l / percentage, 100)[l / percentage > 100]
        elif l >= 50:
            l = (l * percentage, 100)[l * percentage > 100]
        self.hsla = (h, s, l, a)
    
    def add_lightness(self, amount : float):
        if self.hsla[2] + amount > 100:
            self.hsla = (self.hsla[0], self.hsla[1], 100, self.hsla[3])
        elif self.hsla[2] + amount < 0:
            self.hsla = (self.hsla[0], self.hsla[1], 0, self.hsla[3])
        else:
            self.hsla = (self.hsla[0], self.hsla[1], self.hsla[2] + amount, self.hsla[3])
    
    def set_lightness_with_contrast(self, gray_ref, contrast_diff):
        if gray_ref <= 128:
            if gray_ref + contrast_diff >= 255:
                self.update(255, 255, 255)
                return
            while self.gray_value() < gray_ref + contrast_diff:
                self.add_lightness(1)
        else:
            if gray_ref - contrast_diff <= 0:
                self.update(0, 0, 0)
                return
            while self.gray_value() > gray_ref - contrast_diff:
                self.add_lightness(-1)
    
    def set_background_with_contrast(self, gray_ref, contrast_diff, theme):
        if theme == "light" and gray_ref + contrast_diff <= 255:
            while self.gray_value() < gray_ref + contrast_diff:
                self.add_lightness(1)
            return
        if theme == "light" and gray_ref - contrast_diff >= 0:
            while self.gray_value() > gray_ref - contrast_diff:
                self.add_lightness(-1)
            return
        if theme == "light":
            self.update(255, 255, 255)
            return
        if theme == "dark" and gray_ref - contrast_diff >= 0:
            while self.gray_value() > gray_ref - contrast_diff:
                self.add_lightness(-1)
            return
        if theme == "dark" and gray_ref + contrast_diff <= 255:
            while self.gray_value() < gray_ref + contrast_diff:
                self.add_lightness(1)
            return
        if theme == "dark":
            self.update(0, 0, 0)
            return
    
    def set_lightness_with_gray(self, gray_ref):
        if gray_ref >= 255:
            self.update(255, 255, 255)
            return
        elif gray_ref <= 0:
            self.update(0, 0, 0)
            return
        gray = self.gray_value()
        if gray == gray_ref:
            return
        if gray < gray_ref:
            while self.gray_value() < gray_ref and self.hsla[2] != 100:
                self.add_lightness(1)
        else:
            while self.gray_value() > gray_ref and self.hsla[2] != 0:
                self.add_lightness(-1)
    
    def get_rgb_tuple(self):
        return (self.r, self.g, self.b)
    
    def gray_value(self):
        return 0.2126 * self.r + 0.7152 * self.g + 0.0722 * self.b
    
    def convert_to_gray(self):
        self.r = self.g = self.b = round(self.gray_value())
    
    def get_rgb_for_lightness(self, lightness):
        stock_lightness = self.hsla[2]
        self.set_lightness(lightness)
        rgb = self.get_rgb_tuple()
        self.set_lightness(stock_lightness)
        return rgb
    
    def get_rgb_for_saturation(self, saturation):
        stock_saturation = self.hsla[1]
        self.set_saturation(saturation)
        rgb = self.get_rgb_tuple()
        self.set_saturation(stock_saturation)
        return rgb