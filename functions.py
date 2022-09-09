import os
from google.cloud import documentai_v1beta3 as documentai
import pandas as pd
import config as cfg

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=cfg.PRIVATE_JSON_KEY_PATH

# RECEIPTS
ALLOWED_EXTENSIONS_RECEIPTS = {'png', 'jpg', 'jpeg'}

def allowed_files_receipts(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS_RECEIPTS


def receipt_processing(receipt):
    pass

# INVOICES 
ALLOWED_EXTENSIONS_INVOICES = {'tiff', 'pdf'}

def allowed_files_invoices(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS_INVOICES

def process_document_sample(invoice,mime_type):
    # Instantiates a client
    client_options = {"api_endpoint": "{}-documentai.googleapis.com".format(cfg.LOCATION)}
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    name = f"projects/{cfg.PROJECT_ID}/locations/{cfg.LOCATION}/processors/{cfg.PROCESSOR_ID}"


    # Read the file into memory (TODO: CHANGE MIMETYPE ACCORDINGLY. For some reason it does not allow me to upload jpg/png...)
    document = {"content": invoice, "mime_type": mime_type}

    # Configure the process request
    request = {"name": name, "raw_document": document}

    # Recognizes text entities in the PDF document
    result = client.process_document(request=request)
    document = result.document
    entities = document.entities
    print("Document processing complete.\n\n")

    
    #if result.human_review_operation:
        #print ("Triggered HITL long running operation: {}".format(result.human_review_operation))

    return document

def transform_output_to_table(doc):
    entity_types=[]
    entity_text=[]
    entity_confidence=[]
    entity_norm_value=[]
    for entity in doc.entities:
        if entity.type_ == "line_item":
            entity_types.append(entity.type_)
            entity_text.append(entity.mention_text)
            entity_confidence.append(round(entity.confidence,2))
            entity_norm_value.append(entity.normalized_value.text) if entity.normalized_value.text != "" else entity_norm_value.append("n/a")
            for line_item_property in entity.properties:
                entity_types.append(line_item_property.type_)
                entity_text.append(line_item_property.mention_text)
                entity_confidence.append(round(line_item_property.confidence,2))
                entity_norm_value.append(line_item_property.normalized_value.text) if line_item_property.normalized_value.text != "" else entity_norm_value.append("n/a")
        else:
            entity_types.append(entity.type_)
            entity_text.append(entity.mention_text)
            entity_confidence.append(round(entity.confidence,2))
            entity_norm_value.append(entity.normalized_value.text) if entity.normalized_value.text != "" else entity_norm_value.append("n/a")

    df = pd.DataFrame({"Field":entity_types,"Extraction":entity_text,"Normalization":entity_norm_value,"Confidence":entity_confidence})
    df1_html = df[~ df['Field'].str.contains("line_item")].to_html(index=False) # field items
    df2_html = df[df['Field'].str.contains("line_item")].to_html(index=False)   # line items
    df_tables = df1_html + df2_html
    return df_tables