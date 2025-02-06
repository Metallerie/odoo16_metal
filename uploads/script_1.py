from mindee import Client, PredictResponse, product

# Init a new client
mindee_client = Client(api_key="6f85a0b7bbbff23c76d7392514678a61")

# Load a file from disk
input_doc = mindee_client.source_from_path("/home/odoo/metal-odoo16-p8171/uploads/Facture_Free_202411_15511313_1328727379.pdf")

# Load a file from disk and parse it.
# The endpoint name must be specified since it cannot be determined from the class.
result: PredictResponse = mindee_client.parse(product.InvoiceV4, input_doc)

# Print a summary of the API result
print(result.document)

# Print the document-level summary
# print(result.document.inference.prediction)
