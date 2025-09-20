pip install pikepdf
import pikepdf

# Nombre del archivo PDF original y de salida
input_pdf = "plantillaorigen.pdf"
output_pdf = "plantillaencriptada.pdf"

# Contraseña de cifrado (la misma servirá para abrirlo después)
password = "12345"

# Abrimos el PDF
with pikepdf.open(input_pdf) as pdf:
    # Guardamos con encriptación AES-256
    pdf.save(
        output_pdf,
        encryption=pikepdf.Encryption(
            owner=password,
            user=password,
            R=6,   # AES-256
            allow=pikepdf.Permissions(extract=False, print_lowres=False)
        )
    )

print(f"PDF encriptado con AES-256 guardado en {output_pdf}")
print(f"Contraseña de desencriptación: {password}")
