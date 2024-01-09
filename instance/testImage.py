from os.path import exists

import base64
import yaml


# تابعی که یک رشته کد شده را به فایل عکس تبدیل میکند
def decodeBase64AndSaveToFile(filename,b64,path):
    try:
        file_content=base64.b64decode(b64)
        with open(path+filename,"wb") as f:
            f.write(file_content)  #.decode("utf-8")
    except Exception as e:
        print("error in decoding: "+str(e))   

# خواندن از فایل قالب یمل و ذخیره عکسهای آن در فایلهای جداگانه
def readFromYamlAndsaveImagesToFiles(yamlFileName,path):
    f = open(path+yamlFileName+'.yaml', "r")    
    config = yaml.safe_load(f.read())
    name=1
    for t in config['images']:
        if 'image' in t:
            if len(t['image']) > 0:
                    print('has image')
                    decodeBase64AndSaveToFile(yamlFileName+"_q"+str(name)+"."+ t['format'] , t['image'],path)
                    name+=1
# خواندن یک فایل عکس و تبدیل آن به یک رشته کد شده                    
def readFromFileAndEncode64(fileName,path):
    with  open(path+fileName, 'rb') as image:
        image_read = image.read()
        return base64.b64encode(image_read)
    return None

# خواندن فایلهای عکس جدید و ذخیره آنها در قالب یمل
def readFromfilesAndsaveImagesToYaml(yamlFileName,path):
    f = open(path+yamlFileName+'.yaml', "r")    
    config = yaml.safe_load(f.read())
    name=1
    for t in config['images']:
        if 'image' in t:
            if exists(path+yamlFileName+"_n"+str(name)+'.jpg') : 
                newf= readFromFileAndEncode64(yamlFileName+"_n"+str(name)+'.jpg',path)
                if newf!=None:
                    t['image']= newf
                    t['format']='jpg'

            else :
                if exists(path+yamlFileName+"_n"+str(name)+'.jpeg') : 
                    newf= readFromFileAndEncode64(yamlFileName+"_n"+str(name)+'.jpeg',path)
                    if newf!=None:
                        t['image']= newf
                        t['format']='jpg'

                else :
                    if exists(path+yamlFileName+"_n"+str(name)+'.png') : 
                        newf= readFromFileAndEncode64(yamlFileName+"_n"+str(name)+'.png',path)
                        if newf!=None:
                            t['image']= newf
                            t['format']='png'
            name+=1
    with open(path+yamlFileName+'.yaml', 'w') as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)

path="/Users/macbook/Documents/flask/card/instance/"
yamlFileName="templateMeliNew2"

# اول عکسهای جدید را بخوان و در یمل ذخیره کن 
# نام فایلهای عکس جدید با n شروع میشود
readFromfilesAndsaveImagesToYaml(yamlFileName,path)

# سپس از یمل عکسهارا بخوان در فایلهای جداگانه ذخیره کن
# فایلهای خروجی با حرف p شروع میشوند
readFromYamlAndsaveImagesToFiles(yamlFileName,path)

#حالا باید عکسهای خروجی باید با عکسهای ورودی برابر باشد