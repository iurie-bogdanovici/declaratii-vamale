from posixpath import supports_unicode_filenames
import cv2
import pytesseract
import os
from pdf2image import convert_from_path
import re
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
import time
import shutil

CUR_PATH = os.getcwd()
WORK_DIR = os.path.join(CUR_PATH, 'uploads/')

def get_files_by_ext(ext):
    all_files = os.listdir(WORK_DIR)
    all_ext_files = [file for file in all_files if f'.{ext}' in file]
    return all_ext_files

def del_files_by_name(files):
    for file in files:
        os.remove(f"{WORK_DIR}/{file}")
        print(f"File {file} has been deleted!")

def convert_pdf_jpg(filename):
    pages = convert_from_path(f"{WORK_DIR}/{filename}")
    for nr, page in enumerate(pages):
        page.save(f"{WORK_DIR}/{filename.split('.')[0]}_{nr}.jpg", "JPEG")

def get_text_from_jpg(filename):
    img = cv2.imread(f"{WORK_DIR}/{filename}")   
    all_text = pytesseract.image_to_string(img)
    print(f"text has been extracted from {filename}")
    return all_text

def move_file_to_archive(filename):
    source = f"{CUR_PATH}/uploads/{filename}"
    destination = f"{CUR_PATH}/archive/{filename}"
    shutil.move(source, destination)
    
def change_date_format(date):
    months = {'ianuarie': '01', 'februarie': '02', 'martie': '03', 
                'aprilie': '04', 'mai': '05', 'iunie': '06', 
                'iulie': '07', 'august': '08', 'septembrie': '09',
                'octombrie': '10', 'noiemrie': '11', 'decembrie': '12'}
    date_spl = date.split(' ')
    date_spl[1] = months[date_spl[1]]
    return '.'.join(date_spl)

def parse_text(text):
    result = []
    for line in text:
        line = line.strip()
        if line:
            match_nr_act = re.search('^Ne (?P<nr_act>\S+) din', line)
            if match_nr_act:
                result.append(match_nr_act.group('nr_act'))

            match_nr_ff_data = re.search('^la FF Ne (?P<nr_ff>\S+) din (?P<data_factura>\d+ \w+ \d{4})', line)
            if match_nr_ff_data:
                result.append(match_nr_ff_data.group('nr_ff'))
                formated_date = change_date_format(match_nr_ff_data.group('data_factura'))
                result.append(formated_date)

            match_nr_dv = re.search('Declaratia Vamala \(DV\) \* (?P<nr_dv>\S+)', line)
            if match_nr_dv:
                result.append(match_nr_dv.group('nr_dv'))

            match_suma = re.search('TOTAL SPRE PLATA (?P<suma>.*\,\d{2})', line)
            if match_suma:
                result.append(match_suma.group('suma'))
    return result

def get_mthread_parsed_text_from_jpg(filenames):
    parsed_text_list = []
    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = []
        for filename in filenames:
            futures.append(executor.submit(get_text_from_jpg, filename))
        counter = 0
        for f in as_completed(futures):
            counter +=1
            parsed_text = parse_text(f.result().split('\n'))
            print(f"{counter} files from total number of {len(futures)} have been processed!")
            parsed_text_list.append(parsed_text)
    return parsed_text_list

def export_data(data):
    with open('declaratii_esb.csv', 'w') as file:
        writer = csv.writer(file)
        headers = ('Nr Act', 'La FF','Data Factura' , 'Nr DV', 'Suma')
        writer.writerow(headers)
        for line in data:
            writer.writerow(line)
    print("Data has been exported to declaratii_esb.csv file")
        

if __name__ == '__main__':
    os.environ['OMP_THREAD_LIMIT'] = '1'
    start_time = time.time()

    pdf_files = get_files_by_ext('pdf')
    for index, pdf_file in enumerate(pdf_files):
        print(f"Converting {pdf_file}, file {index + 1} from total of {len(pdf_files)} files...")
        convert_pdf_jpg(pdf_file)

    jpg_files = get_files_by_ext('jpg')

    all_pdf_data = get_mthread_parsed_text_from_jpg(jpg_files)
    export_data(all_pdf_data)
    del_files_by_name(jpg_files)
    print(f"--- {time.time() - start_time} seconds have passed ---")
