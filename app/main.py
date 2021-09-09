import secrets
from flask import Flask, render_template, request, current_app, flash
from werkzeug.utils import secure_filename
from lxml import etree
from config.xml_validation import DEFAULT_SCHEMA, XML_ENCODING


app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)


@app.route('/')
def home():
    return render_template('base.html', DEFAULT_SCHEMA=DEFAULT_SCHEMA)


@app.route('/validation/results', methods=['POST'])
def validation_results():
    if request.method == 'POST':
        default_schema = False
        schema_file = request.files.get('xsd_schema')
        if not schema_file:
            if not DEFAULT_SCHEMA:
                flash('Specify default schema path in the configuration or upload yours!', category='danger')
                return render_template('base.html')

            schema_file = open(DEFAULT_SCHEMA)
            default_schema = True

        try:
            schema = etree.parse(schema_file)
            xmlschema = etree.XMLSchema(schema)
        except Exception:
            current_app.logger.error('Invalid schema!', exc_info=1)
            flash('Schema is invalid!', category='danger')
            return render_template('base.html')

        xml_files = request.files.getlist('xml_files')
        if not xml_files or not xml_files[0]:
            flash('No files to validate!', category='danger')
            return render_template('base.html')

        valid_files = []
        invalid_files = []
        for file in xml_files:
            filename = secure_filename(file.filename)
            try:
                content = etree.parse(file)
            except Exception:
                invalid_files.append(filename)
                continue

            if hasattr(content, 'docinfo'):
                doc_info = content.docinfo
                if hasattr(doc_info, 'encoding'):
                    if doc_info.encoding.lower() != XML_ENCODING.lower():
                        invalid_files.append(filename)
                        continue

            valid_file = xmlschema.validate(content)
            if valid_file:
                valid_files.append(filename)
            else:
                invalid_files.append(filename)

        if default_schema:
            flash('Used the default schema', category='info')

        context = {
            'valid_files': valid_files,
            'invalid_files': invalid_files
        }

        return render_template('results.html', **context)
