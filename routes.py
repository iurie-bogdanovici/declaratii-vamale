from flask import Flask, render_template, request, make_response, jsonify, send_file
import os
import random
import main_app
import uuid
import main_app

app = Flask(__name__)

path = os.getcwd()

UPLOAD_FOLDER = os.path.join(path, 'uploads/')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods = ['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        uuid_nr = str(uuid.uuid4())
        uploaded_files = list(request.files.listvalues())
        for file in uploaded_files:
            file = file[0]
            if file:    
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid_nr}_{file.filename}"))
                main_app.convert_pdf_jpg(f"{uuid_nr}_{file.filename}")
        jpg_files = main_app.get_files_by_ext('jpg')
        os.environ['OMP_THREAD_LIMIT'] = '1'
        all_pdf_data = main_app.get_mthread_parsed_text_from_jpg(jpg_files)
        main_app.export_data(uuid_nr, all_pdf_data)
        main_app.del_files_by_name(jpg_files)
        main_app.move_files_to_archive([f"{uuid_nr}_{file[0].filename}" for file in uploaded_files])
        res = make_response(jsonify({"message": f"{len(uploaded_files)} files have been uploaded and processed",
                                    "parsed_data": all_pdf_data,
                                    "uuid": uuid_nr}), 200);
        return res
    else:
        return render_template('upload.html')

@app.route('/export_csv', methods=['GET', 'POST'])
def download():
    received_uuid = request.args.get("uuid")
    return send_file(f"declaratii_esb_{received_uuid}.csv", as_attachment=True)

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
