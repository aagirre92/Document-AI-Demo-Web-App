from google.cloud import documentai_v1beta3
import pandas as pd

ALLOWED_EXTENSIONS_RECEIPTS = {'png', 'jpg', 'jpeg'}

def allowed_files_receipts(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS_RECEIPTS





def receipt_processing(receipt):
    pass
