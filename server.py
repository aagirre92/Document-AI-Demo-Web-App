import os
from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import tempfile
import functions as f
import time


app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/invoices.html')
def invoices():
    return render_template('invoices.html')

@app.route('/receipts.html')
def receipts():
    return render_template('receipts.html')


# INVOICES
@app.route('/r_invoice.html',methods=["POST"])
def r_invoice():
    #print(request.files["invoiceFile"])
    if 'invoiceFile' not in request.files:
        return "No file here"
    file = request.files["invoiceFile"]
    if file.filename == '':
        return "Please select a file"
    if file and f.allowed_files_invoices(file.filename): #here goes the code TODO
        filename = secure_filename(file.filename)
        print(request.files["invoiceFile"])
        document = f.process_document_sample(invoice=file.read(),mime_type=file.mimetype)
        html_table = f.transform_output_to_table(document)
        return html_table
    else:
        return "Not a valid file"

# RECEIPTS
@app.route('/r_receipts.html',methods=["POST"])
def r_receipt():
    #print(request.files["receiptFile"])
    if 'receiptFile' not in request.files:
        return "No file here"
    file = request.files["receiptFile"]
    if file.filename == '':
        return "Select a file"
    if file and f.allowed_files_receipts(file.filename): #here goes the code TODO
        filename = secure_filename(file.filename)
        print(request.files["receiptFile"])
        # HERE GOES THE PAYLOAD
        return filename
    else:
        return "Not a valid file"

if __name__ == '__main__':
    app.run(host='localhost',port=80,debug=True)