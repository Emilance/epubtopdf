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













