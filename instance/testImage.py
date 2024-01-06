from os.path import exists

import base64
import yaml
# تابعی که یک رشته کد شده را به فایل عکس تبدیل میکند
def decodeBase64AndSaveToFile(filename,b64):
    try:
        file_content=base64.b64decode(b64)
        with open(filename+".jpg","wb") as f:
            f.write(file_content)  #.decode("utf-8")
    except Exception as e:
        print("error in decoding: "+str(e))   

# خواندن از فایل قالب یمل و ذخیره عکسهای آن در فایلهای جداگانه
def readFromYamlAndsaveImagesToFiles():
    f = open("template.yaml", "r")    
    config = yaml.safe_load(f.read())
    name=1
    for t in config['images']:
        if 'image' in t:
            if len(t['image']) > 0:
                    print('has image')
                    decodeBase64AndSaveToFile("q"+str(name) , t['image'])
                    name+=1
# خواندن یک فایل عکس و تبدیل آن به یک رشته کد شده                    
def readFromFileAndEncode64(fileName):
    with  open(fileName+'.jpg', 'rb') as image:
        image_read = image.read()
        return base64.b64encode(image_read)
    return None

# خواندن فایلهای عکس جدید و ذخیره آنها در قالب یمل
def readFromfilesAndsaveImagesToYaml():
    f = open("template.yaml", "r")    
    config = yaml.safe_load(f.read())
    name=1
    for t in config['images']:
        if 'image' in t:
            if exists("n"+str(name)+'.jpg') : 
                newf= readFromFileAndEncode64("n"+str(name))
                if newf!=None:
                    t['image']= newf
            name+=1
    with open('template.yaml', 'w') as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)

# اول عکسهای جدید را بخوان و در یمل ذخیره کن 
# نام فایلهای عکس جدید با n شروع میشود
readFromfilesAndsaveImagesToYaml()

# سپس از یمل عکسهارا بخوان در فایلهای جداگانه ذخیره کن
# فایلهای خروجی با حرف p شروع میشوند
readFromYamlAndsaveImagesToFiles()

#حالا باید عکسهای خروجی باید با عکسهای ورودی برابر باشد