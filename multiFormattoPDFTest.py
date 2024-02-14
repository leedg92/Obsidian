from fpdf import FPDF, XPos, YPos
import win32com.client
import os
import re

#should command "pip install fpdf2" for .txt files
#should command "pip install pywin32" for .doc, .docx, .hwp files

def convert_to_pdf(input_path, filename):
    extension = os.path.splitext(filename)[1].lower()
    if extension in ['.doc', '.docx']:
        convert_word_to_pdf(input_path, filename)
    elif extension == '.hwp':
        #print(extension)
        convert_hwp_to_pdf(input_path, filename)
    if extension == '.txt': 
        #print(extension)
        convert_txt_to_pdf(input_path, filename)

def convert_hwp_to_pdf(input_path, filename):
        hwp = win32com.client.gencache.EnsureDispatch('HWPFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')
        hwp_path = os.path.join(input_path, filename)
        hwp.Open(hwp_path)
        pdf_path = os.path.join(input_path, os.path.splitext(filename)[0] + ".pdf")
        hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.HParameterSet.HFileOpenSave.filename = pdf_path
        hwp.HParameterSet.HFileOpenSave.Format = "PDF"
        hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.Quit()

def convert_word_to_pdf(input_path, filename):
        word = win32com.client.Dispatch("Word.Application")
        word.visible = False
        doc_path = os.path.join(input_path, filename)
        doc = word.Documents.Open(doc_path)
        pdf_path = os.path.join(input_path, os.path.splitext(filename)[0] + ".pdf")
        doc.SaveAs(pdf_path, FileFormat=17)  # 17's meaning is PDF format
        doc.Close()
        word.Quit()


def convert_txt_to_pdf(input_path, filename):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        txt_path = os.path.join(input_path, filename)
        pdf_filename = os.path.splitext(filename)[0] + ".pdf"
        pdf_path = os.path.join(input_path, pdf_filename)
        with open(txt_path, 'r', encoding='utf-8') as file:
            for line in file:
                pdf.cell(0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.output(pdf_path)


base_path = "C:/Users/leedg/Desktop/pyTest"  # base path for saving and transformating
for year in range(2018, 2021):
    for month in range(1, 13):
        for day in range(1, 32):
            
            date_path = os.path.join(base_path, str(year), f"{month:02d}", f"{day:02d}")
            if not os.path.exists(date_path):
                # print(str(year) + f"{month:02d}" + f"{day:02d}" + " 의 날짜폴더 없음")
                continue                
            files = [f for f in os.listdir(date_path) if re.match('.*\\.(docx|doc|hwp|txt)$', f, re.IGNORECASE)]
             # continue when there is no file matching formating
            if not files: 
                # print(str(year) + f"{month:02d}" + f"{day:02d}" + " 의 날짜폴더에 파일 없음")
                continue
            for file in files:
                try:
                    convert_to_pdf(date_path, file)
                    print(f"Converted {file} to PDF in {date_path}.")
                except Exception as e:
                    print(f"...Error converting {file} to PDF in {date_path}: {e}...")