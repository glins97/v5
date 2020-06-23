from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject, TextStringObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import StringIO, BytesIO

def _set_need_appearances_writer(writer):
    try:
        catalog = writer._root_object
        if "/AcroForm" not in catalog:
            writer._root_object.update({
                NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
    except:
        pass
    return writer

class PDFFileFiller(object):
    def __init__(self, infile):
        self.pdf = PdfFileReader(open(infile, "rb"), strict=False)
        if "/AcroForm" in self.pdf.trailer["/Root"]:
            self.pdf.trailer["/Root"]["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})
            
    def update_form_values(self, outfile, newvals={}, newchecks={}):
        self.pdf2 = CustomPDFFileWriter()
        trailer = self.pdf.trailer["/Root"]["/AcroForm"]
        self.pdf2._root_object.update({
            NameObject('/AcroForm'): trailer})

        _set_need_appearances_writer(self.pdf2)
        if "/AcroForm" in self.pdf2._root_object:
            self.pdf2._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})
        
        for i in range(self.pdf.getNumPages()):
            self.pdf2.addPage(self.pdf.getPage(i))
            if i == 1:
                self.pdf2.updatePageFormFieldValues(self.pdf2.getPage(i), newvals)
                self.pdf2.updatePageFormCheckboxValues(self.pdf2.getPage(i), newchecks)

        with open(outfile, 'wb') as out:
            self.pdf2.write(out)

class CustomPDFFileWriter(PdfFileWriter):
    def __init__(self):
        super().__init__()
    def updatePageFormCheckboxValues(self, page, fields):

        for j in range(0, len(page['/Annots'])):
            writer_annot = page['/Annots'][j].getObject()
            for field in fields:
                if writer_annot.get('/T') == field:
                    writer_annot.update({
                        NameObject("/V"): NameObject(fields[field]),
                        NameObject("/AS"): NameObject(fields[field])
                    })

def fill_pdf_fields(source, values, destination=''):
    if not destination:
        destination = source
    filler = PDFFileFiller(source)
    filler.update_form_values(outfile=destination, newvals=values)

if __name__ == "__main__":
    ''' example usage '''
    fill_pdf_fields('1x/a.pdf', {"a1":"120","a2":"200","a3":"160","a4":"120","a5":"200", "t": "800"}, '_export.pdf')