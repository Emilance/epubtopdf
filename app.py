from flask import Flask, render_template, request, send_file, after_this_request
import ebooklib
from ebooklib import epub
from weasyprint import HTML , CSS

import os
import base64
import imghdr
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Check if the file has an allowed extension (EPUB)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'epub'

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# EPUB to PDF conversion route
@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Check if 'epubFile' is in request.files
        if 'epubFile' not in request.files:
            return "No file part in the request.", 400

        epub_file = request.files['epubFile']

        # Check if the file is an EPUB
        if not allowed_file(epub_file.filename):
            return "Invalid file format. Please upload an EPUB file.", 400

        # Save EPUB file to a temporary location
        epub_filename = secure_filename(epub_file.filename)
        epub_path = os.path.join("temp", epub_filename)
        epub_file.save(epub_path)

        print(epub_path)
        # Parse EPUB metadata
        book = epub.read_epub(epub_path)

        title = book.get_metadata('DC', 'title')[0][0]
       
      # Extract HTML content from EPUB
        html_content = ""
        styles = ""
        for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_IMAGE:
                    image_data = base64.b64encode(item.content).decode('utf-8')
                    image_format = imghdr.what(None, h=item.content)
                    html_content += f'<img src="data:image/{image_format};base64,{image_data}" />'
                elif item.get_type() == ebooklib.ITEM_STYLE:
                    styles += item.content.decode('utf-8')
                elif hasattr(item, 'get_body_content'):
                    html_content += item.get_body_content().decode('utf-8')

        # Include styles in the content
        html_content = f'<style>{styles}</style>{html_content}'
        # Save HTML content to a temporary file
        html_filename = secure_filename(title + ".html")
        html_path = os.path.join("temp", html_filename)
        with open(html_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)

        css = CSS(string='''
            @page {
                margin-top: 20mm;
                margin-bottom: 20mm;
            }
        ''')
        # Use WeasyPrint to convert HTML to PDF
        pdf_path = os.path.join("temp", title + ".pdf")
        HTML(string=html_content).write_pdf(pdf_path , stylesheets=[css])

        # Send the converted PDF as a response
        @after_this_request
        def remove_temp_files(response):
            os.remove(epub_path)
            os.remove(html_path)
            os.remove(pdf_path)
            return response

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=title + ".pdf"
         )
      
    except Exception as e:
        print(f"Error converting EPUB to PDF: {e}")
        return "Internal Server Error", 500

# Run the application
if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(debug=True)

























# from flask import Flask, render_template, request, send_file, after_this_request
# import ebooklib
# from ebooklib import epub
# import pdfkit
# import os
# import base64
# import imghdr
# from io import BytesIO
# from werkzeug.utils import secure_filename

# app = Flask(__name__)

# # Check if the file has an allowed extension (EPUB)
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'epub'

# # Convert EPUB to PDF
# def convert_epub_to_pdf(html_content):
#     font_size='20px'
#     print("about to convert")
#     options = {
#         'quiet': '',
#         'no-images': '',
#         'disable-smart-shrinking': '',
#         'margin-top': '20mm',
#         'margin-right': '20mm',
#         'margin-bottom': '20mm',
#         'margin-left': '20mm',
#     }
    
#     # # Convert bytes to string
#     # html_content_str = html_content.decode('utf-8')
  
#     return pdfkit.from_string(html_content, False, options=options )


# # Home page
# @app.route('/')
# def index():
#     return render_template('index.html')

# # EPUB to PDF conversion route
# @app.route('/convert', methods=['POST'])
# def convert():
#     try:
#         # Check if 'epubFile' is in request.files
#         if 'epubFile' not in request.files:
#             return "No file part in the request.", 400

#         epub_file = request.files['epubFile']

#         # Check if the file is an EPUB
#         if not allowed_file(epub_file.filename):
#             return "Invalid file format. Please upload an EPUB file.", 400

#         # Save EPUB file to a temporary location
#         epub_filename = secure_filename(epub_file.filename)
#         epub_path = os.path.join("temp", epub_filename)
#         epub_file.save(epub_path)

#         print(epub_path)
#         # Parse EPUB metadata
#         book = epub.read_epub(epub_path)

#         title = book.get_metadata('DC', 'title')[0][0]
       
#       # Extract HTML content from EPUB
#         html_content = ""
#         styles = ""
#         for item in book.get_items():
#             if item.get_type() == ebooklib.ITEM_IMAGE:
#                 image_data = base64.b64encode(item.content).decode('utf-8')
#                 image_format = imghdr.what(None, h=item.content)
#                 html_content += f'<img src="data:image/{image_format};base64,{image_data}" />'
#             elif item.get_type() == ebooklib.ITEM_STYLE:
#                 styles += item.content.decode('utf-8')
#             elif hasattr(item, 'get_body_content'):
#                 html_content += item.get_body_content().decode('utf-8')

#         # Include styles in the content
#         html_content = f'<style>{styles}</style>{html_content}'
#         print(html_content)
#         # for item in book.get_items_of_type(9):  # Type 9 corresponds to text content
#         #     html_content += item.get_body_content().decode('utf-8')

#     # Save HTML content to a temporary file
#         html_filename = secure_filename(title + ".html")
#         html_path = os.path.join("temp", html_filename)
#         with open(html_path, 'w', encoding='utf-8') as html_file:
#             html_file.write(html_content)

#         # Send the converted HTML as a response
#         # @after_this_request
#         # def remove_temp_files(response):
#         #     os.remove(html_path)
#         #     return response

#         # return send_file(
#         #     html_path,
#         #     as_attachment=True,
#         #     download_name=html_filename
#         # )
      
#         pdf_buffer = convert_epub_to_pdf(html_content)

#         print("it is geetting heeeree o")

#         # Save PDF to a temporary file
#         pdf_filename = secure_filename(title + ".pdf")
#         pdf_path = os.path.join("temp", pdf_filename)
#         with open(pdf_path, 'wb') as pdf_file:
#             pdf_file.write(pdf_buffer)


#         # Send the converted PDF as a response
#         @after_this_request
#         def remove_temp_files(response):
#             os.remove(epub_path)
#             os.remove(pdf_path)
#             return response

#         return send_file(
#             pdf_path,
#             as_attachment=True,
#             download_name=pdf_filename
#          )
      

#     except Exception as e:
#         print(f"Error converting EPUB to PDF: {e}")
#         return "Internal Server Error", 500

# # Run the application
# if __name__ == '__main__':
#     if not os.path.exists('temp'):
#         os.makedirs('temp')
#     app.run(debug=True)


















# from flask import Flask, render_template, request, send_file, after_this_request
# from ebooklib import epub
# import pdfkit
# import os
# from io import BytesIO
# from werkzeug.utils import secure_filename

# app = Flask(__name__)

# # Check if the file has an allowed extension (EPUB)
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'epub'

# # Convert EPUB to PDF
# def convert_epub_to_pdf(html_content):
#     options = {
#         'quiet': '',
#         'no-images': '',
#         'disable-smart-shrinking': '',
#         'margin-top': '0',
#         'margin-right': '0',
#         'margin-bottom': '0',
#         'margin-left': '0',
#     }
    
#     # Convert bytes to string
#     html_content_str = html_content.decode('utf-8')

#     return pdfkit.from_string(html_content_str, False, options=options)


# # Home page
# @app.route('/')
# def index():
#     return render_template('index.html')

# # EPUB to PDF conversion route
# @app.route('/convert', methods=['POST'])
# def convert():
#     try:
#         # Check if 'epubFile' is in request.files
#         if 'epubFile' not in request.files:
#             return "No file part in the request.", 400

#         epub_file = request.files['epubFile']

#         # Check if the file is an EPUB
#         if not allowed_file(epub_file.filename):
#             return "Invalid file format. Please upload an EPUB file.", 400

#         # Save EPUB file to a temporary location
#         epub_filename = secure_filename(epub_file.filename)
#         epub_path = os.path.join("temp", epub_filename)
#         epub_file.save(epub_path)

#         print(epub_path)
#         # Parse EPUB metadata
#         book = epub.read_epub(epub_path)

#         title = book.get_metadata('DC', 'title')[0][0]
#         # print(book)
     

#      # Convert EPUB to PDF
#         html_content = epub_file.read()
#         print( html_content)
#         pdf_buffer = convert_epub_to_pdf(html_content)

#         print("it is geetting heeeree o")
        
#         # Save PDF to a temporary file
#         pdf_filename = secure_filename(title + ".pdf")
#         pdf_path = os.path.join("temp", pdf_filename)
#         with open(pdf_path, 'wb') as pdf_file:
#             pdf_file.write(pdf_buffer)


#         # Send the converted PDF as a response
#         @after_this_request
#         def remove_temp_files(response):
#             os.remove(epub_path)
#             os.remove(pdf_path)
#             return response

#         return send_file(
#             pdf_path,
#             as_attachment=True,
#             download_name=pdf_filename
#         )
      

#     except Exception as e:
#         print(f"Error converting EPUB to PDF: {e}")
#         return "Internal Server Error", 500

# # Run the application
# if __name__ == '__main__':
#     if not os.path.exists('temp'):
#         os.makedirs('temp')
#     app.run(debug=True)
























# from flask import Flask, render_template, request, send_file, after_this_request
# from ebooklib import epub
# import pdfkit
# import os
# from io import BytesIO
# from werkzeug.utils import secure_filename

# app = Flask(__name__)

# # Check if the file has an allowed extension (EPUB)
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'epub'

# # Convert EPUB to PDF
# def convert_epub_to_pdf(html_content, images):
#     options = {
#         'quiet': '',
#         'margin-top': '10mm',
#         'margin-right': '10mm',
#         'margin-bottom': '10mm',
#         'margin-left': '10mm',
#     }

#     # Convert bytes to string
#     # html_content_str = html_content.decode('utf-8')

#     # Include image tags in the HTML content
#     for image in images:
#         html_content += f'<img src="data:{image.media_type};base64,{image.content}" />'
#         print(html_content)
#     return pdfkit.from_string(html_content, False, options=options)

# # Home page
# @app.route('/')
# def index():
#     return render_template('index.html')

# # EPUB to PDF conversion route
# @app.route('/convert', methods=['POST'])
# def convert():
#     try:
#         # Check if 'epubFile' is in request.files
#         if 'epubFile' not in request.files:
#             return "No file part in the request.", 400

#         epub_file = request.files['epubFile']

#         # Check if the file is an EPUB
#         if not allowed_file(epub_file.filename):
#             return "Invalid file format. Please upload an EPUB file.", 400

#         # Save EPUB file to a temporary location
#         epub_filename = secure_filename(epub_file.filename)
#         epub_path = os.path.join("temp", epub_filename)
#         epub_file.save(epub_path)

#         print(f"EPUB saved at: {epub_path}")

#         # Parse EPUB metadata
#         book = epub.read_epub(epub_path)
#         title = book.get_metadata('DC', 'title')[0][0]

#         # Extract HTML content
#         html_content = ""
#         images = []

#         for item in book.get_items():
#             if item.get_type() == 9:  # Use 9 for text content (adjust based on your EPUB structure)
#                 html_content += item.get_body_content().decode('utf-8')
#             elif item.get_type() == 5:  # Use 5 for images (adjust based on your EPUB structure)
#                 images.append(item)

#         # Convert EPUB to PDF
#         pdf_buffer = convert_epub_to_pdf(html_content, images)

#         print("Conversion successful")

#         # Save PDF to a temporary file
#         pdf_filename = secure_filename(title + ".pdf")
#         pdf_path = os.path.join("temp", pdf_filename)
#         with open(pdf_path, 'wb') as pdf_file:
#             pdf_file.write(pdf_buffer)

#         # Send the converted PDF as a response
#         @after_this_request
#         def remove_temp_files(response):
#             os.remove(epub_path)
#             os.remove(pdf_path)
#             return response

#         return send_file(
#             pdf_path,
#             as_attachment=True,
#             download_name=pdf_filename
#         )

#     except Exception as e:
#         print(f"Error converting EPUB to PDF: {e}")
#         return "Internal Server Error", 500

# # Run the application
# if __name__ == '__main__':
#     if not os.path.exists('temp'):
#         os.makedirs('temp')
#     app.run(debug=True)
