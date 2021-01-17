from flask import Flask,render_template,request
import requests
import cv2
import re

import pyttsx3
from gtts import gTTS

rgb2hex = lambda r, g, b: '#%02x%02x%02x' % (r, g, b)

app = Flask(__name__)

def text_to_speech_gTTS(mytext,gender,file):

    language="en"
    slow = False 
    #creating audio obj from gTTS engine
    myAudioObj = gTTS(text=mytext, lang=language, slow=slow)

    #saving audio file (pass full path if you want to save to another location)
    myAudioObj.save(file)

    # checking whether file is successfully saves or not by using a print function after save function
    print("Audio file saved.")

def text_to_speech(text, gender, file):
    """
    Function to convert text to speech
    :param text: text
    :param gender: gender
    :return: None
    """
    voice_dict = {'Male': 0, 'Female': 1}
    code = voice_dict[gender]

    engine = pyttsx3.init()

    # Setting up voice rate
    engine.setProperty('rate', 125)

    # Setting up volume level  between 0 and 1
    engine.setProperty('volume', 0.8)

    # Change voices: 0 for male and 1 for female
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[code].id)

    # engine.say(text)
    engine.save_to_file(text, file)
    engine.runAndWait()



colornames = ['AliceBlue','AntiqueWhite','Aqua','Aquamarine','Azure','Beige','Bisque','Black','BlanchedAlmond','Blue','BlueViolet','Brown','BurlyWood','CadetBlue','Chartreuse','Chocolate','Coral','CornflowerBlue','Cornsilk','Crimson','Cyan','DarkBlue','DarkCyan','DarkGoldenRod','DarkGray','DarkGrey','DarkGreen','DarkKhaki','DarkMagenta','DarkOliveGreen','DarkOrange','DarkOrchid','DarkRed','DarkSalmon','DarkSeaGreen','DarkSlateBlue','DarkSlateGray','DarkSlateGrey','DarkTurquoise','DarkViolet','DeepPink','DeepSkyBlue','DimGray','DimGrey','DodgerBlue','FireBrick','FloralWhite','ForestGreen','Fuchsia','Gainsboro','GhostWhite','Gold','GoldenRod','Gray','Grey','Green','GreenYellow','HoneyDew','HotPink','IndianRed','Indigo','Ivory','Khaki','Lavender','LavenderBlush','LawnGreen','LemonChiffon','LightBlue','LightCoral','LightCyan','LightGoldenRodYellow','LightGray','LightGrey','LightGreen','LightPink','LightSalmon','LightSeaGreen','LightSkyBlue','LightSlateGray','LightSlateGrey','LightSteelBlue','LightYellow','Lime','LimeGreen','Linen','Magenta','Maroon','MediumAquaMarine','MediumBlue','MediumOrchid','MediumPurple','MediumSeaGreen','MediumSlateBlue','MediumSpringGreen','MediumTurquoise','MediumVioletRed','MidnightBlue','MintCream','MistyRose','Moccasin','NavajoWhite','Navy','OldLace','Olive','OliveDrab','Orange','OrangeRed','Orchid','PaleGoldenRod','PaleGreen','PaleTurquoise','PaleVioletRed','PapayaWhip','PeachPuff','Peru','Pink','Plum','PowderBlue','Purple','RebeccaPurple','Red','RosyBrown','RoyalBlue','SaddleBrown','Salmon','SandyBrown','SeaGreen','SeaShell','Sienna','Silver','SkyBlue','SlateBlue','SlateGray','SlateGrey','Snow','SpringGreen','SteelBlue','Tan','Teal','Thistle','Tomato','Turquoise','Violet','Wheat','White','WhiteSmoke','Yellow','YellowGreen']
hexes = ['f0f8ff','faebd7','00ffff','7fffd4','f0ffff','f5f5dc','ffe4c4','000000','ffebcd','0000ff','8a2be2','a52a2a','deb887','5f9ea0','7fff00','d2691e','ff7f50','6495ed','fff8dc','dc143c','00ffff','00008b','008b8b','b8860b','a9a9a9','a9a9a9','006400','bdb76b','8b008b','556b2f','ff8c00','9932cc','8b0000','e9967a','8fbc8f','483d8b','2f4f4f','2f4f4f','00ced1','9400d3','ff1493','00bfff','696969','696969','1e90ff','b22222','fffaf0','228b22','ff00ff','dcdcdc','f8f8ff','ffd700','daa520','808080','808080','008000','adff2f','f0fff0','ff69b4','cd5c5c','4b0082','fffff0','f0e68c','e6e6fa','fff0f5','7cfc00','fffacd','add8e6','f08080','e0ffff','fafad2','d3d3d3','d3d3d3','90ee90','ffb6c1','ffa07a','20b2aa','87cefa','778899','778899','b0c4de','ffffe0','00ff00','32cd32','faf0e6','ff00ff','800000','66cdaa','0000cd','ba55d3','9370db','3cb371','7b68ee','00fa9a','48d1cc','c71585','191970','f5fffa','ffe4e1','ffe4b5','ffdead','000080','fdf5e6','808000','6b8e23','ffa500','ff4500','da70d6','eee8aa','98fb98','afeeee','db7093','ffefd5','ffdab9','cd853f','ffc0cb','dda0dd','b0e0e6','800080','663399','ff0000','bc8f8f','4169e1','8b4513','fa8072','f4a460','2e8b57','fff5ee','a0522d','c0c0c0','87ceeb','6a5acd','708090','708090','fffafa','00ff7f','4682b4','d2b48c','008080','d8bfd8','ff6347','40e0d0','ee82ee','f5deb3','ffffff','f5f5f5','ffff00','9acd32']

def getClosestColorName(hexcolor):
    prevcolordiff = 1000000
    hexcolor1 = int("0x" + hexcolor[1:], 16)
    for i in range(len(hexes)):
        hexcolor2 = int("0x" + hexes[i], 16)
        colordiff = abs(hexcolor2-hexcolor1)
        if colordiff < prevcolordiff:
            colorname = colornames[i]
            prevcolordiff = colordiff
    return colorname


def process_image(image_name):
    color_count = {}
    print('Processing the image {}'.format(image_name))
    path = 'static/uploaded_images/' + image_name

    image = cv2.imread(path)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            (b, g, r) = image[i, j]
            h_value = rgb2hex(r, g, b)

            if h_value in color_count:
                color_count[h_value] += 1
            else:
                color_count[h_value] = 1
    return color_count

def dl_img(img_url):
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ur;q=0.8',
    }

    file_name = None
    downloaded_file_name = None
    downloaded_file_name = img_url.split('/')[-1]

    try:
            print('Downloading the file...' + img_url)
            response = requests.get(img_url, headers=headers, timeout=30)

            if response.status_code == 200:
                file_name = downloaded_file_name.replace(' ','-').lower()

                path = 'static/uploaded_images/'+file_name
                with open(path, 'wb') as fi:
                    fi.write(response.content)

    except Exception as ex:
        print('Exception in downloading image')
        print(str(ex))
    finally:
        return file_name


@app.route('/')
def upload():
    message = ''
    color='red'
    imgPath=''
    args = request.args
    if 'message' in args:
        message = args.get('message')
    if 'color' in args:
        color = args.get('color')
    if 'imgPath' in args:
        imgPath = args.get('imgPath')
    
    return render_template('index.html',message=message, color=color, imgPath=imgPath)


@app.route('/',methods=['POST'])
def uploaded():
    msg = ''
    if request.method == 'POST':
        form_data = request.form
        # upload_type = form_data['upload_type']
        color='red'
        if 1 == 1: # or upload_type.strip() == '2':
            download_image_url = form_data['url'] 
            print('THE DOWNLOAD IMAGE = {}'.format(download_image_url))
            img_file_name = dl_img(download_image_url.strip())       
            print(img_file_name) 
            if img_file_name is not None and img_file_name != '':    
                hexcolor = process_image(img_file_name)       
                sortedcolors = sorted(hexcolor.items(), key=lambda x: x[1], reverse=True)   
                print(sortedcolors[0][0], sortedcolors[1][0])
                top5 = []
                for hexcolor in sortedcolors:
                    colorname = getClosestColorName(hexcolor[0])
                    colorname = " ".join(re.sub( r"([A-Z])", r" \1", colorname).split())
                    if colorname not in top5:
                        top5.append(colorname)
                        if len(top5) == 5:
                            break

                msg = 'The predominant colors in your image: ' + top5[0] + ', ' + top5[1] + ', ' + top5[2] + ', '+ top5[3] + ', and '+ top5[4]
                text_to_speech_gTTS(msg, 'Female', 'static/uploaded_images/'+img_file_name+".mp3")
                imgPath = 'static/uploaded_images/'+img_file_name
        try:
            return render_template('index.html', message=msg, color=color, imgPath=imgPath)
        except Exception as e:
            print(e)
    return render_template('index.html', message='')
    
if __name__ == "__main__":
    app.debug = True
    app.run()
