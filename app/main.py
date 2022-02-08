import secrets
from flask import Flask, render_template, request, current_app, flash
from werkzeug.utils import secure_filename
from lxml import etree
from collections import defaultdict

from config.xml_validation import DEFAULT_SCHEMA, XML_ENCODING


app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)


@app.route("/")
def home():
    return render_template("base.html", DEFAULT_SCHEMA=DEFAULT_SCHEMA)


@app.route("/validation/results", methods=["POST"])
def validation_results():
    if request.method == "POST":
        default_schema = False
        schema_file = request.files.get("xsd_schema")
        if not schema_file:
            schema_file = open(DEFAULT_SCHEMA)
            default_schema = True

        try:
            schema = etree.parse(schema_file)
            xmlschema = etree.XMLSchema(schema)
        except Exception:
            current_app.logger.error("Invalid schema!", exc_info=1)
            flash("Schema is invalid!", category="danger")
            return render_template("base.html")

        xml_files = request.files.getlist("xml_files")
        if not xml_files or not xml_files[0]:
            flash("No files to validate!", category="danger")
            return render_template("base.html")

        valid_files = []
        non_xml_files = []
        invalid_files = defaultdict(list)
        for file in xml_files:
            filename = secure_filename(file.filename)
            if not filename.endswith(".xml"):
                non_xml_files.append(filename)
                continue

            try:
                parser = etree.XMLParser()
                content = etree.parse(file, parser)
            except etree.XMLSyntaxError:
                for err in parser.error_log:
                    syntax_err_msg = "Line {line}:\n\t{message}".format(
                        line=err.line,
                        message=err.message,
                    )
                    invalid_files[filename].append(syntax_err_msg)
                continue
            except Exception:
                invalid_files[filename].append("Unknown error.")
                continue

            if hasattr(content, "docinfo"):
                doc_info = content.docinfo
                if hasattr(doc_info, "encoding"):
                    if doc_info.encoding.lower() != XML_ENCODING.lower():
                        encoding_err_msg = "Invalid document encoding!"
                        invalid_files[filename].append(encoding_err_msg)
                        continue

            try:
                xmlschema.assertValid(content)
            except etree.DocumentInvalid:
                for validation_error in xmlschema.error_log:
                    validation_err_msg = "Line {line}:\n\t{message}".format(
                        line=validation_error.line,
                        message=validation_error.message,
                    )
                invalid_files[filename].append(validation_err_msg)
            except Exception:
                invalid_files[filename].append("Unknown error.")
            else:
                valid_files.append(filename)

        if default_schema:
            flash("Used the default schema", category="info")
            schema_file.close()

        context = {
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "non_xml_files": non_xml_files
        }
        return render_template("results.html", **context)
