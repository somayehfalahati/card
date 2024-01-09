import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

#configuration
font_size=36
width=200
height=100
back_ground_color=(255,255,255)
font_size=36
font_color=(0,0,0)

unicode_text = u"بِسم اللَه"
unicode_text_reshaped = arabic_reshaper.reshape(unicode_text )
unicode_text_reshaped_RTL = get_display(unicode_text_reshaped , base_dir='R')
#You have to do it in this order to work correctly

im  =  Image.new ( "RGB", (width,height), back_ground_color )
draw  =  ImageDraw.Draw ( im )
unicode_font = ImageFont.truetype("/Users/macbook/Documents/flask/card/card/static/tahoma.ttf", font_size)
draw.text ( (10,10), unicode_text_reshaped_RTL , font=unicode_font, fill=font_color )
draw.text ( (10,30), unicode_text_reshaped , font=unicode_font, fill=font_color )
draw.text ( (10,50), unicode_text , font=unicode_font, fill=font_color )

im.save("text.png")