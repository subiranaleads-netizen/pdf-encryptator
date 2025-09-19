from flask import Flask, request, send_file
import tempfile
import os
import pikepdf

app = Flask(__name__)

@app.route("/encrypt", methods=["POST"])
def encrypt_pdf():
    password = request.form.get("password")
    file = request.files.get("file")

    if not file or not password:
        return {"error": "Falta archivo o contraseña"}, 400

    # Guardar archivo temporalmente
    input_path = tempfile.mktemp(suffix=".pdf")
    output_path = tempfile.mktemp(suffix="_encrypted.pdf")
    file.save(input_path)

    # Cifrar PDF con pikepdf
    pdf = pikepdf.open(input_path)
    pdf.save(
        output_path,
        encryption=pikepdf.Encryption(
            owner=password,
            user=password,
            R=6  # AES-256
        )
    )
    pdf.close()

    # Enviar archivo cifrado al cliente
    return send_file(output_path, as_attachment=True, download_name="documento_cifrado.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)