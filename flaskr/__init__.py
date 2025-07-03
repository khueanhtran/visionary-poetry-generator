from flask import (
    Flask, render_template, request, jsonify
)
import os
from werkzeug.utils import secure_filename
import glob
from . import main

app = Flask(__name__)

IMAGES_FOLDER = 'flaskr/images'
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER
INSPIRING_POEMS_FOLDER = 'flaskr/inspiring_poems'
GENERATED_POEMS_FOLDER = 'flaskr/generated_poems'

# make sure all folders exist
for folder in [IMAGES_FOLDER, INSPIRING_POEMS_FOLDER, GENERATED_POEMS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# allowed file types for image uploads
ALLOWED_TYPES = ['jpg', 'jpeg', 'png']

def allowed_file(filename):
    """
    Checks if the file has an allowed extension
    """
    if '.' not in filename:
        return False
    name_split = filename.split('.', 1)
    extension = name_split[1].lower()
    return extension in ALLOWED_TYPES

@app.route("/", methods=["GET"])
def hello():
    """
    Displays when the user first navigates to the site.
    """
    # reset the images and inspiring poems folders
    for filename in glob.glob(f"{IMAGES_FOLDER}/*"): 
        os.remove(filename)
    for filename in glob.glob(f"{INSPIRING_POEMS_FOLDER}/*"):
        os.remove(filename)

    # select and parse 10 random poems to be used for this round of generation
    main.parse_poem_csv()

    return render_template('index.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    """
    Retrieves uploaded image files from the user and stores them in the
    images folder.
    """
    if request.method == 'POST':

        # check if the post request has the files part
        if 'files' not in request.files:
            return render_template('index.html', \
                                   files_uploaded = 'No files part')
        
        # retrieves uploaded files
        files = request.files.getlist('files')
        
        # if no files were selected
        if len(files) == 0:
            return render_template('index.html', \
                               files_uploaded = 'No file selected. Try again.')

        # if valid files were uploaded
        for file in files:
            if file and allowed_file(file.filename):
                # ensures no repeating file names
                filename = secure_filename(file.filename)
                # saves uploaded image file to images folder
                file.save(os.path.join(app.config['IMAGES_FOLDER'], filename))
        return render_template('index.html', \
                               files_uploaded = 'Files uploaded successfully!')
    return ''


@app.route('/generate', methods=['POST'])
def generate_poem():
    """
    Generates a new poem, stores it in the generated poems folder, and returns
    a JSON dictionary of the poem name and poem string.
    """
    poem_tuple = main.main()
    poem_name = poem_tuple[0]
    new_poem = poem_tuple[1]

    # don't write into file if no poem generated because of no images
    if not new_poem == "*NO IMAGES*":
        filename = secure_filename(poem_name)
        file_path = f'{GENERATED_POEMS_FOLDER}/{filename}.txt'
        new_file = open(file_path, 'w')
        new_file.write(new_poem)
        new_file.close()
    
    # creates dictionary to return two JSON pieces of data
    poem_data = {'name' : poem_name, 'poem' : new_poem}

    return jsonify(poem_data)

@app.route('/history', methods=["POST"])
def view_old_poems():
    """
    Returns a dictionary of file name to text for all the poems in the 
    generated poems folder.
    """
    path_len = len(GENERATED_POEMS_FOLDER) + 1
    file_to_poem = dict()

    # iterate over all files in the generated poems folder
    for filename in glob.glob(f"{GENERATED_POEMS_FOLDER}/*"): 
        poem_file = open(filename)
        poem_str = poem_file.read()
        # remove the '.txt' in the file name for the key
        file_to_poem[filename[path_len:-4]] = poem_str
        
    return jsonify(file_to_poem)
