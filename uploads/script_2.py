from mindee import Client, PredictResponse, product

# Initier le client avec la clé API
mindee_client = Client(api_key="6f85a0b7bbbff23c76d7392514678a61")

# Charger et analyser le fichier PDF
input_doc = mindee_client.source_from_path("/home/odoo/metal-odoo16-p8171/uploads/Facture_Free_202411_15511313_1328727379.pdf")
result: PredictResponse = mindee_client.parse(product.InvoiceV4, input_doc)

# Extraire le document de la réponse
document = result.document
# Inspecter l'objet document pour voir tous les champs


invoice_data = {
    "supplier_name": result.document.inference.prediction.supplier_name.value,
    "customer_name": result.document.inference.prediction.customer_name.value,
    "total_amount": result.document.inference.prediction.total_amount.value,
    "line_items": []
}

# Ajouter chaque élément de ligne avec ses détails
for line_item in result.document.inference.prediction.line_items:
    item_data = {
        "description": line_item.description,
        "total_amount": line_item.total_amount,
        "unit_price": line_item.unit_price,
        "tax_rate": line_item.tax_rate
    }
    invoice_data["line_items"].append(item_data)

# Afficher ou utiliser `invoice_data` pour intégration
print(invoice_data)


