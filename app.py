from flask import Flask, request, jsonify
import os
import PyPDF2
import gemini

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['UPLOAD_FOLDER'] = 'uploads'


@app.route('/job_description', methods=['POST'])
def generate_job_description():
    if request.json:
        data = request.json
        job_title = data.get('job_title')
        location = data.get('location')
        mandatory_skills = data.get('mandatory_skills', [])
        overall_experience = data.get('overall_experience')
        work_type = data.get('work_type')
        mode_of_work = data.get('mode_of_work')
        education_requirement = data.get('education_requirement')
        ctc = data.get('ctc')

        if job_title and location and overall_experience and mandatory_skills and work_type and mode_of_work and education_requirement and ctc:
            jd_text = gemini.generate_job_description(job_title, location, mandatory_skills, overall_experience, work_type, mode_of_work, education_requirement, ctc, app.config['GEMINI_API_KEY'])
            return jsonify({'job_description': jd_text}), 200
        else:
            return jsonify({'error': 'Missing required fields.'}), 400
    else:
        return jsonify({'error': 'Invalid request format.'}), 400


@app.route('/pdf_job_description', methods=['POST'])
def generate_job_description_from_pdf():
    if 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        if pdf_file.filename != '':
            pdf_filename = pdf_file.filename
            pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            pdf_file.save(pdf_file_path)

            with open(pdf_file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                pdf_text = ''
                for page_num in range(len(pdf_reader.pages)):
                    pdf_text += pdf_reader.pages[page_num].extract_text()

            os.remove(pdf_file_path)

            return jsonify({'job_description': pdf_text}), 200
    return jsonify({'error': 'PDF file not provided.'}), 400


if __name__ == '__main__':
    app.run(debug=True)
