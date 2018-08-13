
from flask import Flask, render_template,request,send_from_directory
import face_recognition,glob,re,os,time,cPickle as pickle
from werkzeug import secure_filename


app = Flask(__name__)

known_faces=[]  # stores encodings of known faces
image_names=[] # stores names corresponding to encondings
has_image_dir=True  # flag if images folder present
UPLOAD_FOLDER='tmp' # tmp save location for uploaded images
IMAGES_FOLDER='images' # training images
SERIALIZED_FILE='known_faces.pkl' # location of precomputed serialized objects

@app.route('/')
def initial_view():

    return render_template('fileUpload.html',train_flag=has_image_dir,image_flag=False)

@app.route('/', methods=['POST'])
def display_result():
    f = request.files['file']
    image_face = True;
    filename = secure_filename(f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, filename))
    try:
        unknown_image = face_recognition.load_image_file(f)
    except IOError: # Invalid image file
        image_face=False

    if image_face:
        try:
            unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
        except IndexError:  # No face detected in image
            image_face=False
        if image_face:
            results = face_recognition.compare_faces(known_faces, unknown_face_encoding)
            if (not True in results):
                answer= "no match"
            else:
                answer=image_names[results.index(True)]
    if(not image_face):
        answer="Either Invalid image file or no face detected in image"
    return  render_template('fileUpload.html',train_flag=has_image_dir,image_flag=True,image='/uploads/'+f.filename,name=answer)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':

    # Check last modified  time of images directory
    try:
        ctime1 = time.ctime(max(os.path.getmtime(root) for root,_,_ in os.walk(IMAGES_FOLDER)))
    # if images folder doesnt exist or has no files
    except ValueError:
        ctime1=-1
        has_image_dir=False
    # check time of last update
    try:
        ctime2 = os.path.getmtime(os.path.join(IMAGES_FOLDER,SERIALIZED_FILE))
    # if file doesn't exist. first run /deleted etc
    except OSError:
        ctime2=0
    # if no more updates than our serialized file. Then we can directly load from our precomputed serialized file.
    if(ctime1==ctime2):
        arr=pickle.load(os.path.join(IMAGES_FOLDER,SERIALIZED_FILE))
        known_faces=arr[0]
        image_names= arr[1]

    # image_dir has flag whether training image files empty. if empty don't even run.
    elif has_image_dir:
        for fileName in glob.glob(os.path.join(IMAGES_FOLDER,'*')): # check all extensions in image folder
            if(re.match('.*\.(png|jpg|jpeg|gif)',fileName)): # checking if valid image files
                try:
                    known_faces.extend(face_recognition.face_encodings(face_recognition.load_image_file(fileName)))
                    image_names.append(re.search('images/(.*)\.',fileName).group(1))
                except IndexError: # no faces detected skip
                    continue
                except IOError:
                    continue

        pickle.dump([known_faces,image_names],open("images/known_faces.pkl","w+")) #Serializing this object for next run of flask

    app.run(debug = True)
