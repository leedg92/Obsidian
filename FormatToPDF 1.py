from fpdf import FPDF, XPos, YPos
import win32com.client
import os
import re

# 전역 카운터 변수 초기화
doc_docx_rtf_TOTAL = 0
hwp_hwpx_TOTAL = 0
ppt_pptx_TOTAL = 0

doc_docx_rtf_CONVERTED = 0
hwp_hwpx_CONVERTED = 0
ppt_pptx_CONVERTED = 0

# 변환에 실패한 파일명을 저장할 리스트
failed_files = []

def log_success_conversion(pdf_path):    
    with open(os.path.join(base_path, "last_success.txt"), "w") as log_file:
        log_file.write(f"Last successful conversion: {pdf_path}\n")   

def convert_to_pdf(input_path, filename):
    global doc_docx_rtf_TOTAL, hwp_hwpx_TOTAL, ppt_pptx_TOTAL
    # 여기서는 CONVERTED 카운트를 증가시키지 않습니다.

    extension = os.path.splitext(filename)[1].lower()
    if extension in ['.doc', '.docx', '.rtf']:
        doc_docx_rtf_TOTAL += 1
        try:
            convert_word_to_pdf(input_path, filename, word)
            
        except Exception as e:
            print(f"Error converting {filename}: {e}")  
            failed_files.append(filename)        
    elif extension in ['.hwp', '.hwpx']:
        hwp_hwpx_TOTAL += 1
        try:
            convert_hwp_to_pdf(input_path, filename, hwp)
            
        except Exception as e:
            print(f"Error converting {filename}: {e}")
            failed_files.append(filename)
    elif extension in ['.ppt', '.pptx']:
        ppt_pptx_TOTAL += 1
        try:
            convert_pptx_to_pdf(input_path, filename, powerpoint)
            
        except Exception as e:
            print(f"Error converting {filename}: {e}")
            failed_files.append(filename)



def initialize_hwp_application():
    hwp = win32com.client.gencache.EnsureDispatch('HWPFrame.HwpObject')
    hwp.XHwpWindows.Item(0).Visible = False
    hwp.RegisterModule("FilePathCheckDLL", "AutomationModule")
    return hwp

def finalize_hwp_application(hwp):
    hwp.Quit()
    del hwp

def initialize_word_application():
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False 
    return word

def finalize_word_application(word):
    word.Quit()
    del word

def initialize_powerpoint_application():
    powerpoint = win32com.client.Dispatch("Powerpoint.Application")
    # powerpoint.Visible = False
    return powerpoint

def finalize_powerpoint_application(powerpoint):
    powerpoint.Quit()
    del powerpoint



def convert_hwp_to_pdf(input_path, filename, hwp):
    global hwp_hwpx_TOTAL, hwp_hwpx_CONVERTED
    try:
        full_path = os.path.join(input_path, filename)
        pdf_path = os.path.join(input_path, os.path.splitext(filename)[0] + ".pdf")
        hwp.Open(full_path)
        hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.HParameterSet.HFileOpenSave.filename = pdf_path
        hwp.HParameterSet.HFileOpenSave.Format = "PDF"
        hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp_hwpx_CONVERTED += 1
        log_success_conversion(pdf_path)
        hwp.Clear(1)  # 현재 문서를 닫습니다.
    except Exception as e:
        print(f"Error converting {filename}: {e}")
        failed_files.append(filename)


def convert_word_to_pdf(input_path, filename, word):
    global doc_docx_rtf_CONVERTED
    doc = None
    try:
        doc_path = os.path.join(input_path, filename)
        pdf_path = os.path.join(input_path, os.path.splitext(filename)[0] + ".pdf")
        doc = word.Documents.Open(doc_path)
        doc.SaveAs(pdf_path, FileFormat=17)  # PDF 형식으로 저장
        doc_docx_rtf_CONVERTED += 1
        log_success_conversion(pdf_path)
    finally:
        if doc is not None:
            doc.Close()

def convert_pptx_to_pdf(input_path, filename, powerpoint):
    global ppt_pptx_CONVERTED
    presentation = None
    try:
        ppt_path = os.path.join(input_path, filename)
        pdf_path = os.path.join(input_path, os.path.splitext(filename)[0] + ".pdf")
        presentation = powerpoint.Presentations.Open(ppt_path)
        presentation.SaveAs(pdf_path, FileFormat=32)  # PDF 형식으로 저장
        ppt_pptx_CONVERTED += 1
        log_success_conversion(pdf_path)
    finally:
        if presentation is not None:
            presentation.Close()

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

# base_path = "C:/Users/sli004/Desktop/courTrans"  # base path for saving and transformating


def save_results_to_file():
    result_file_path = os.path.join(base_path, "conversion_results.txt")
    with open(result_file_path, "w") as file:
        file.write("Conversion Summary:\n")
        file.write(f"DOC/DOCX/RTF converted: {doc_docx_rtf_CONVERTED} / {doc_docx_rtf_TOTAL}\n")
        file.write(f"HWP/HWPX converted: {hwp_hwpx_CONVERTED} / {hwp_hwpx_TOTAL}\n")
        file.write(f"PPT/PPTX converted: {ppt_pptx_CONVERTED} / {ppt_pptx_TOTAL}\n")

def save_failed_files():
    failed_file_path = os.path.join(base_path, "failed_files.txt")
    with open(failed_file_path, "w") as f:
        for file in failed_files:
            f.write(f"{file}\n")
    print("Failed file names have been saved to failed_files.txt.")            

if __name__ == "__main__":
    base_path = "C:\\Users\\sli004\\Desktop\\courTrans"  
    word = initialize_word_application()
    powerpoint = initialize_powerpoint_application()
    hwp = initialize_hwp_application()
 
    for year in range(2018, 2019):
        for month in range(1, 13):
            for day in range(1, 32):
                
                date_path = os.path.join(base_path, str(year), f"{month:02d}", f"{day:02d}")
                if not os.path.exists(date_path):
                    # print(str(year) + f"{month:02d}" + f"{day:02d}" + " 의 날짜폴더 없음")
                    continue                
                files = [f for f in os.listdir(date_path) if re.match('.*\\.(docx|doc|hwp|hwpx|rtf|ppt|pptx)$', f, re.IGNORECASE)]
                # continue when there is no file matching formating
                if not files: 
                    # print(str(year) + f"{month:02d}" + f"{day:02d}" + " 의 날짜폴더에 파일 없음")
                    continue
                for file in files:
                    try:
                        convert_to_pdf(date_path, file)
                        print(f"try converting {file} to PDF in {date_path}.")
                    except Exception as e:
                        print(" ")

    finalize_hwp_application(hwp)
    finalize_word_application(word)
    finalize_powerpoint_application(powerpoint)

    save_results_to_file()
    save_failed_files()
    print("Results and failed file names have been saved to file.")
