import os 
import olefile
import pdfplumber
import win32com.client

def extract_from_hwp(file):
    f = olefile.OleFileIO(file) 
    encoded_text = f.openstream('PrvText').read() 
    decoded_text = encoded_text.decode('utf-16')  
        
    return decoded_text

def extract_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        full_text = ''
        
        for page in pdf.pages:
            full_text += page.extract_text() + '\n'
            
    
    return full_text

# input_folder = 'documents'
# output_folder = 'parsed_texts'

# for filename in os.listdir(input_folder):
#     ext = os.path.splitext(filename)[1].lower()
#     file_path = os.path.join(input_folder, filename)
#     print(ext)
    
#     if ext == '.pdf':
#         # 텍스트 추출
#         full_text = extract_from_pdf(file_path)

#     if ext == '.hwp':
#         print(file_path)
#         full_text = extract_from_hwp(file_path)    
        
#     # 결과 저장할 경로
#     output_filename = os.path.splitext(filename)[0] + '.txt'
#     output_path = os.path.join(output_folder, output_filename)
    
#     with open(output_path, 'w', encoding='utf-8') as f:
#         f.write(full_text)
    
#     print(f"Saved to: {output_path}")



f = olefile.OleFileIO('documents/2003-37.hwp') 
encoded_text = f.openstream('PrvText').read() 
decoded_text = encoded_text.decode('utf-16')  
print(decoded_text)