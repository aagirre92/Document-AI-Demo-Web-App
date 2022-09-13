# INTRO
This web application will accept a invoice document (**.tiff or .pdf**) and extract its data using Document AI Invoice processor

# RESULTS
The web application will fetch all entities extracted by Document AI and present them in a tabular form. On top of that it will:
* Present the invoice total, net total and currency (if present)
* Display a info alert with the sum of the line items so that user can check if it corresponds to the total or net total (it will perform this if the processor can extract correctly **all** line item amounts)

# ABOUT
This web application has been developed using Python 3.10.6