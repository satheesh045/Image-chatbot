from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
import requests
import json
from helpers import *
from preprocess import *
from tag_extraction import *


#intialize flask app 
app = Flask(__name__)
#set config for upload folder and allowed image extentions
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(),"static/images")
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']  

#home route to ender index html file 
@app.route("/")
def home():
    return render_template("index.html")

#chat UI route for user questions  
@app.route("/chat",methods=['GET'])
def get_bot_response():
        #classify user messege wether it is an extract feature or tag feature or help or just a question
        userText = request.args.get('msg')
        if("extract:" in userText):
            #if extract take image name then OCR it and return its text 
            try:    
                image_str=userText[userText.find(":")+1:]
                print(image_str)
                path=os.getcwd()+"/static/images/text-based/"+image_str
                image  = cv2.imread(str(path))
                text = extract_text(image)
                print(text)
                return {"Answer":text,"image_name":image_str,"type":"extract"}
            except:
                return {"Answer":"image not found","type":"error"}    

        elif("tag:" in userText):
            #if tag searched in tags knowledge base then return image name to front end 
            tag=userText[userText.find(":")+1:]
            print("tag entered: ",tag)
            search_result=find_tag(tag)
            if search_result== "not found":
               result={"Answer":"not found","image_name":search_result ,"type":"tag"}
            else:
               result={"Answer": "found" ,"image_name":search_result["image"] ,"type":"tag"}  
            return result  

        elif(userText=="help"):
            help_message="you can ask me any question related to text content in your image and I'll help you find the answer and its image, you also can use extract feature by typing 'extract:' followed by image name to extract text content in the image and 'tag:' followed by a keyword to find any natural image with this tag"
            return {"Answer":help_message ,"type":"help"} 

        
        else:
            print("flask will send this:",userText)
            newdata = {"question": userText} # this is the question we are going to send to the Node server to get it answer 
            # now immediately sending a post request with user question then return it answer to front end 
            try:
                post = requests.post('http://localhost:7000/postdata', json=newdata) # the POST request      
                print("flask recived this :",post.text)
                result=json.loads(post.text) 
                return result
            except:
                print("i failed connecting node")

      
    
#upload route for images
@app.route("/upload",methods=['POST'])
def uploader():
    if request.method == 'POST':
        #store images files 
        uploaded_files =request.files.getlist("file[]")
        for file in uploaded_files:
            #check image extention if it is allowed 
            if file and allowed_file(file.filename):
                filename = file.filename
                #decode image string 
                img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
                #extract image text with ocr to determine if it text-based image or scene (natural image) 
                text= extract_text(img,custom_config = r'-l eng -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz --oem 1')
                page= extract_text(img)
                print(filename,": ",len(text),"p:",len(page))
                #will consider any image with text-length below 200 char to be a scene
                if(len(text)<200): 
                    #if it is a scence image save to it certain folder and add its tage to tag knowledge base 
                    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'],"photo",filename), img) 
                    try:
                        extract_images_tags(filename)
                    except Exception as e: 
                        print("Exception extracting image tags",e)
                else: 
                    #if image is text-based insert it split its text to paragraph and then add to its knowledge base 
                    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'],"text-based",filename), img)
                    insert_into_KB(page=page,filename=file.filename)         

    return render_template("index.html")


if __name__ == "__main__":
   app.run(host='localhost', port=5002,debug=True)



    
       























 

 
