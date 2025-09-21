# app.py
from flask import Flask, request, send_file, jsonify, abort
from flask_cors import CORS
import tempfile
import os
import pikepdf
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # si quieres restringir, usar: CORS(app, origins=["https://tu-dominio-lovable"])

# Config
ALLOWED_EXTENSIONS = {"pdf"}
MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB max
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/encrypt", methods=["POST"])
def encrypt_pdf():
    # Validar campos
    if "file" not in request.files:
        return jsonify({"error": "Falta el archivo 'file'"}), 400
    file = request.files["file"]
    password = request.form.get("password", None)

    if not file or file.filename == "":
        return jsonify({"error": "Archivo no proporcionado"}), 400
    if not password or len(password) < 4:
        return jsonify({"error": "Se requiere contraseña (mínimo 4 caracteres) en 'password'"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Sólo se permiten PDFs"}), 400

    filename = secure_filename(file.filename)

    # Usar temp dir para evitar problemas
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, f"input_{filename}")
        out_path = os.path.join(tmp, "document_encrypted.pdf")

        # Guardar el archivo subido
        file.save(in_path)

        # Intentamos abrir y cifrar con pikepdf (AES-256)
        try:
            with pikepdf.open(in_path) as pdf:
                # owner=user = password para que la misma contraseña abra el documento
                pdf.save(
                    out_path,
                    encryption=pikepdf.Encryption(
                        owner=password,
                        user=password,
                        R=6  # AES-256
                    )
                )
        except pikepdf._qpdf.PasswordError:
            return jsonify({"error": "El PDF está protegido con contraseña actualmente"}), 400
        except Exception as e:
            # No devolver el stack completo por seguridad, pero loguear internamente
            app.logger.exception("Error al encriptar PDF")
            return jsonify({"error": "Error al procesar el PDF"}), 500

        # Devolver archivo cifrado como descarga
        return send_file(
            out_path,
            as_attachment=True,
            download_name="document_encrypted.pdf",
            mimetype="application/pdf"
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
