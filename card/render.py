from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import base64, io, os
from werkzeug.utils import secure_filename
# این برنامه پردازش اصلی عکس ها و اطلاعات را بر اساس قالب و اطلاعات بارگزاری شده در دسته انجام می دهد
class Render:
    def __init__(self, config, fontsBasePath, inputBasePath, outputBasePath):
        self.config = config
        self.inputBasePath = inputBasePath
        self.outputBasePath = outputBasePath
        self.fontsBasePath = fontsBasePath

        # تمام عکسهای قالب را بخوان و در حافظه نگه دار
        self.images = {}
        for i in config['images']:
            base64_bytes = i['image'].encode('ascii')
            image_bytes = base64.b64decode(base64_bytes)
            imageName = i['name']
            self.images[imageName] = Image.open(io.BytesIO(image_bytes))

        # تمام حالتهای نمایش متن را از قالب بخوان و در حافظه نگه دار
        self.fontDecorations = {}
        for fd in config['textDecorations']:
            fontFile = "%s/%s.ttf" % (self.fontsBasePath, secure_filename(fd['font']))
            font = ImageFont.truetype(fontFile, fd['size'])
            self.fontDecorations[fd['name']] = font

    def render(self, data, save=True):
        output = {}
        # برای هر فرد میتواند چند قالب پر شود مثلا پشت کارت و روی کارت
        for t in self.config['templates']:
            # از تصویری که نام آن در قالب ذکر شده یک کپی تهیه کن
            image = self.images[t['name']].copy()
            imageDraw = ImageDraw.Draw(image)

            # تمام متنها را از داده های داده شده بخوان و روی تصویر بگذار
            if 'textFields' in t:
                for tf in t['textFields']:
                    text = str(data[tf['dataIndex'] - 1]).strip()
                    font = self.fontDecorations[tf['textDecoration']]
                    color = tuple(self.getTextDecoration(tf['textDecoration'])['color'])
                    pos = tf['position']['x'], tf['position']['y']
                    if tf['coordinateOrigin'] == "right":
                        textSize = imageDraw.textsize(text, font=font)
                        pos = pos[0]-textSize[0], pos[1]
                    
                    imageDraw.text(pos, text, fill=color, font=font)

            #  تمام تصاویر ثابت و متغیر را بخوان و روی تصویر پس زمینه بگذار
            if 'imageFields' in t:
                for fi in t['imageFields']:
                    img = None
                    if fi['source']['type'] == "dynamic":
                        field = secure_filename(str(data[fi['source']['fileNameIndexReference'] - 1]))
                        filePath = "%s/%s.%s" % (self.inputBasePath, field, fi['source']['fileFormat'])
                        if not os.path.exists(filePath):
                            continue
                        img = Image.open(filePath)
                    elif fi['source']['type'] == "static":
                        img = self.images[fi['source']['image']].copy()
                    
                    if 'scale' in fi:
                        if fi['scale']['type'] == "box":
                            resize = fi['scale']['box']['width'], fi['scale']['box']['height']
                            img = img.resize(resize, resample=Image.Resampling.LANCZOS)

                    pos = fi['position']['x'], fi['position']['y']
                    if fi['coordinateOrigin'] == "right":
                        pos = pos[0]-img.size[0], pos[1]

                    image.paste(img, pos, img)
            
            # نام فایل خروجی 
            fileName = secure_filename(str(data[t['output']['fileNameIndexReference'] - 1]).strip())
            # پسوند نام فایل را از قالب بخوان و به نام فایل اضافه کن
            if 'fileNamePostfix' in t['output']:
                fileName += t['output']['fileNamePostfix']
            # پسوند فایل عکس جدید را از پسوند عکس پس زمینه بدست آور و به نام فایل خروجی اضافه کن
            fileExtension = self.getImage(t['backgroundImage'])['format']
            pathToFile = "%s/%s.%s" % (self.outputBasePath, fileName, fileExtension)
            #  فایل خروجی نهایی را ذخیره کن
            if save:
                if os.path.exists(pathToFile):
                    os.remove(pathToFile)
                image.save(pathToFile)
            # اطلاعات عکس تولید شده را در فهرست خروجی اضافه کن
            output[t['name']] = {"obj": image, "path": pathToFile, "fileName": "%s.%s" % (fileName, fileExtension)}
        
        return output


    def getTextDecoration(self, name):
        for td in self.config['textDecorations']:
            if td['name'] == name:
                return td


    def getImage(self, name):
        for fi in self.config['images']:
            if fi['name'] == name:
                return fi
                
