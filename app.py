from flask import Flask, render_template, request, send_file
from weasyprint import HTML
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
PDF_FOLDER = 'certificates'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', 'Anonymous')
        course = request.form.get('course', 'Course')
        description = request.form.get('description', '')
        issue_date = request.form.get('issue_date', datetime.today().strftime('%Y-%m-%d'))

        # Handle signature upload
        signature_file = request.files.get('signature')
        signature_path = None
        if signature_file and signature_file.filename != '':
            filename = secure_filename(signature_file.filename)
            signature_path = os.path.join(UPLOAD_FOLDER, filename)
            signature_file.save(signature_path)

        # Handle logo upload
        logo_file = request.files.get('logo')
        logo_path = None
        if logo_file and logo_file.filename != '':
            filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(UPLOAD_FOLDER, filename)
            logo_file.save(logo_path)

        # Generate PDF
        html = render_template('certificate.html', 
                               name=name, 
                               course=course, 
                               description=description,
                               issue_date=issue_date,
                               signature=signature_path,
                               logo=logo_path)
        pdf_filename = f"{name.replace(' ','_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
        HTML(string=html).write_pdf(pdf_path)

        # Return PDF to user
        return send_file(pdf_path, as_attachment=True)

    return '''
    <h1>Certificate Generator</h1>
    <form method="post" enctype="multipart/form-data">
        Name: <input type="text" name="name" required><br>
        Course: <input type="text" name="course"><br>
        Date: <input type="date" name="issue_date"><br>
        Description: <textarea name="description"></textarea><br>
        Signature: <input type="file" name="signature"><br>
        Logo: <input type="file" name="logo"><br>
        <button type="submit">Generate PDF</button>
    </form>
    '''
    
if __name__ == '__main__':
    app.run(debug=True)
