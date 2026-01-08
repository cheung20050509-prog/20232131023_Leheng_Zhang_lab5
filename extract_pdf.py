from pypdf import PdfReader

try:
    reader = PdfReader("/home/jacob/lab5/2023级-OS课程设计-lab5.pdf")
    number_of_pages = len(reader.pages)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    print(text)
except Exception as e:
    print(f"Error: {e}")
