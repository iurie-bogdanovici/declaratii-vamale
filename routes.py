from flask import Flask, render_template, request, make_response, jsonify, send_file
import os
import random
import main_app

app = Flask(__name__)

ALLOWED_EXTENSIONS = ['pdf']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#1
#exporting_threads = {}

path = os.getcwd()
print(path)
UPLOAD_FOLDER = os.path.join(path, 'uploads/')
print(UPLOAD_FOLDER)

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods = ['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        #2
        #thread_id = random.randint(0, 10000)
        #exporting_threads[thread_id] = 0
        uploaded_files = list(request.files.listvalues())
        for file in uploaded_files:
            file = file[0]
            if file and allowed_file(file.filename):    
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                main_app.convert_pdf_jpg(file.filename)
        jpg_files = main_app.get_files_by_ext('jpg')
        os.environ['OMP_THREAD_LIMIT'] = '1'
        all_pdf_data = main_app.get_mthread_parsed_text_from_jpg(jpg_files)
        main_app.export_data(all_pdf_data)
        main_app.del_files_by_name(jpg_files)
        main_app.move_file_to_archive(file.filename)
        res = make_response(jsonify({"message": f"{len(uploaded_files)} files have been uploaded and processed",
                                    "parsed_data": all_pdf_data}), 200)
        return res
    else:
        return render_template('upload.html')

@app.route('/export_csv', methods=['GET', 'POST'])
def download():
    print(f"returned csv file")
    return send_file("declaratii_esb.csv", as_attachment=True)

if __name__ == '__main__':
    app.run(port=5000, host='192.168.204.130', debug=True)
