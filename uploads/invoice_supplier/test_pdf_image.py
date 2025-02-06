from pdf2image import convert_from_path

# Remplace 'chemin/vers/fichier.pdf' par le chemin de ton fichier PDF
pdf_path = '/home/odoo/metal-odoo16-p8171/uploads/invoice_supplier/test.pdf'
try:
    images = convert_from_path(pdf_path, dpi=200)
    for i, image in enumerate(images):
        image_path = f"{pdf_path}_page_{i + 1}.png"
        image.save(image_path, "PNG")
        print(f"Image enregistrée : {image_path}")
except Exception as e:
    print(f"Erreur lors de la conversion du PDF : {e}")
