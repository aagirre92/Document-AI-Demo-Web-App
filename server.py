from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import functions as f



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



@app.route('/r_receipts.html',methods=["POST"])
def r_receipts():
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