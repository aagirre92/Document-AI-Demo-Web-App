import os
from google.cloud import documentai_v1beta3 as documentai
import pandas as pd
# import config as cfg

#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PRIVATE_JSON_KEY_PATH

# Environment variables (docker)
PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
PROCESSOR_ID = os.environ["PROCESSOR_ID"]  # Create processor in Cloud Console

# RECEIPTS
ALLOWED_EXTENSIONS_RECEIPTS = {'png', 'jpg', 'jpeg'}


def allowed_files_receipts(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_RECEIPTS


def receipt_processing(receipt):
    pass


# INVOICES
ALLOWED_EXTENSIONS_INVOICES = {'tiff', 'pdf'}


def allowed_files_invoices(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_INVOICES


def check_line_items_sum(df_line_items: pd.DataFrame):
    # todo
    pass


def look_for_field_df(df, field_name):
    return df[df["Field"] == field_name]["Normalization"].iloc[0] if len(df[df["Field"] == field_name]["Normalization"]) != 0 and df[df["Field"] == field_name]["Normalization"].iloc[0] != 'n/a' else "Not found"


def process_document_sample(invoice, mime_type):
    """
    Function that uploads the invoice to DocAI and retrieves the document field of the json response
    """
    # Instantiate a client
    client_options = {
        "api_endpoint": "{}-documentai.googleapis.com".format(LOCATION)}
    client = documentai.DocumentProcessorServiceClient(
        client_options=client_options)

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}"

    # Read the file into memory (TODO: CHANGE MIMETYPE ACCORDINGLY. For some reason it does not allow me to upload jpg/png...)
    document = {"content": invoice, "mime_type": mime_type}

    # Configure the process request
    request = {"name": name, "raw_document": document}

    # Recognizes text entities in the PDF document
    result = client.process_document(request=request)
    document = result.document
    entities = document.entities
    print("Document processing complete.\n\n")

    # if result.human_review_operation:
    #print ("Triggered HITL long running operation: {}".format(result.human_review_operation))

    return document


def transform_output_to_table(doc):
    """
    Function that manipulates the document response and returns two html tables containing the
    field and line items
    """
    entity_types = []
    entity_text = []
    entity_confidence = []
    entity_norm_value = []
    for entity in doc.entities:
        if entity.type_ == "line_item":
            entity_types.append(entity.type_)
            entity_text.append(entity.mention_text)
            entity_confidence.append(round(entity.confidence, 2))
            entity_norm_value.append(
                entity.normalized_value.text) if entity.normalized_value.text != "" else entity_norm_value.append("n/a")
            for line_item_property in entity.properties:
                entity_types.append(line_item_property.type_)
                entity_text.append(line_item_property.mention_text)
                entity_confidence.append(
                    round(line_item_property.confidence, 2))
                entity_norm_value.append(
                    line_item_property.normalized_value.text) if line_item_property.normalized_value.text != "" else entity_norm_value.append("n/a")
        else:
            entity_types.append(entity.type_)
            entity_text.append(entity.mention_text)
            entity_confidence.append(round(entity.confidence, 2))
            entity_norm_value.append(
                entity.normalized_value.text) if entity.normalized_value.text != "" else entity_norm_value.append("n/a")

    df = pd.DataFrame({"Field": entity_types, "Extraction": entity_text,
                      "Normalization": entity_norm_value, "Confidence": entity_confidence})
    df1_html = df[~ df['Field'].str.contains(
        "line_item")].to_html(index=False)  # field items
    df2_html = df[df['Field'].str.contains("line_item")].to_html(
        index=False)   # line items

    # Construct ul-li for some fields
    field_names = {
        "Total Amount": look_for_field_df(df, "total_amount"),
        "Net Amount": look_for_field_df(df, "net_amount"),
        "Currency": look_for_field_df(df, "currency"),
    }

    ul_li_html = "<ul class='list-group'>"
    for key, value in field_names.items():
        if value != "Not found":
            ul_li_html += "<li class='list-group-item list-group-item-primary'>" + \
                key + ": " + value + "</li>"
    ul_li_html += "</ul>"

    # Check if the sum of the line item a mount corresponds to the invoice total:
    line_item_amount_sum = round(pd.to_numeric(df[df["Field"] == "line_item/amount"]["Normalization"]).sum(
    ), 2) if 'n/a' not in df[df["Field"] == "line_item/amount"]["Normalization"].values else "n/a"
    line_item_amount_html = ""
    if line_item_amount_sum != 'n/a':
        line_item_amount_html = f"""
        <div class='alert alert-info'>
        <strong>Info:</strong> Line item amount sum is {line_item_amount_sum}
        </div>

        """
    html_output = ul_li_html + line_item_amount_html + '<h1 class="display-2">Field items</h1>' + \
        df1_html + '<h1 class="display-2">Table items</h1>' + df2_html
    # TODO return the tables and a list stating the total amount (con y sin iva) and check if the sum of
    # line item amount correspond to the total net amount
    # ADD CLOUD IAP for authentication! (si no tengo permisos usar una VM interna y ya)
    return html_output
