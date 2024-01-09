from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import base64, io, os
from werkzeug.utils import secure_filename

card = Image.new("RGBA", ( 1005,639), (255, 255, 255))
img = Image.open("/Users/macbook/Documents/flask/card/card/assets/output/ddddd/images/asd.png").convert("RGBA")
x, y = img.size

resize = 265,325
img = img.resize(resize, resample=Image.Resampling.LANCZOS)
pos = 65,165

card.paste(img, pos , img)
card.save("/Users/macbook/Documents/flask/card/card/assets/output/ddddd/images/test.png", format="png")