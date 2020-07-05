from io import BytesIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen.canvas import Canvas
from PIL import Image

from PyPDF2.generic import (
    DictionaryObject,
    NumberObject,
    FloatObject,
    NameObject,
    TextStringObject,
    ArrayObject,
    createStringObject
)

def hex_to_rgba(color):
    return tuple(int(color.lstrip('#')[i:i+2], 16)/255.0 for i in (0, 2, 4, 6))

class Document():
    def __init__(self, source):
        try:
            im = Image.open(source)
            width, height = im.size

            self.width = 2 * 595
            self.height = 2 * int(height * 1.0 / width * 595)
            self.size = self.width, self.height

            im = im.resize(self.size, Image.ANTIALIAS)
            im.save(source)
            self.ratio = self.height / 2000
            self.pen_size = 30 * self.ratio
        except Exception as e:
            raise Exception('Failed to open image source ' + source + '\n' + repr(e))

        document = BytesIO()
        canvas = Canvas(document, pagesize=(self.size))  
        canvas.setFillColorRGB(1, 1, 1)
        canvas.drawImage(source, 0, 0, mask=(1, 1, 1, 1, 1, 1))
        canvas.save()
        self.pdf = PdfFileWriter()
        self.pdf.addPage(PdfFileReader(BytesIO(document.getvalue())).getPage(0))
        
    def add_line(self, x0, y0, x1, y1, color="000000ff"):
        document = BytesIO()
        canvas = Canvas(document, pagesize=self.size)  
        canvas.setLineWidth(self.pen_size)
        canvas.setStrokeColorRGB(*hex_to_rgba(color))
        canvas.line(x0 * self.width, (1 - y0) * self.height, x1 * self.width, (1 - y1) * self.height) 
        canvas.save()
        self.pdf.getPage(0).mergePage(PdfFileReader(BytesIO(document.getvalue())).getPage(0))

    def add_rect(self, x0, y0, x1, y1, color="000000ff"):
        print('@add_rect', x0, y0, x1, y1, color)
        document = BytesIO()
        canvas = Canvas(document, pagesize=self.size)  
        canvas.setLineWidth(self.pen_size / 7)
        canvas.setStrokeColorRGB(*hex_to_rgba(color))
        canvas.rect(x0 * self.width, (1 - y0) * self.height - max((y1 - y0), (y0 - y1)) * self.height, max((x1 - x0), (x0 - x1)) * self.width, max((y1 - y0), (y0 - y1)) * self.height, stroke=1, fill=0) 
        canvas.save()
        self.pdf.getPage(0).mergePage(PdfFileReader(BytesIO(document.getvalue())).getPage(0))

    def add_note(self, src, x0, y0, comment='', author=''):
        self._add_image(src, x0, y0)
        self._add_highlight(x0, y0, 70, 40, comment, author)
  
    def export(self, fn, objects):
        funcs = {
            'LINE': self.add_line,
            'COMM': self.add_note,
            'RECT': self.add_rect,
        }
        for obj in objects:
            funcs.get(obj['mode'], lambda **kwargs: -1)(**obj['attributes'])
            
        self.pdf.write(open(fn, 'wb'))

    def _add_image(self, source, x, y):
        source = source.replace('/static/', 'static/')
        document = BytesIO()
        canvas = Canvas(document, pagesize=self.size)
        canvas.setFillColorRGB(1, 1, 1)
        canvas.drawImage(source, x * self.width, (1 - y) * self.height - 40 * self.ratio, width=(70 * self.ratio), height=(40 * self.ratio), mask='auto')
        canvas.save()
        self.pdf.getPage(0).mergePage(PdfFileReader(BytesIO(document.getvalue())).getPage(0))

    def _create_highlight(self, x0, y0, width, height, comment, author=''):
        x0 = x0 * self.width
        y0 = (1 - y0) * self.height - 40 * self.ratio
        
        highlight = DictionaryObject()
        highlight.update({
            NameObject("/F"): NumberObject(4),
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Highlight"),

            NameObject("/T"): TextStringObject(author),
            NameObject("/Contents"): createStringObject(comment),

            NameObject("/C"): ArrayObject([FloatObject(c) for c in (0, 0, 0)]),
            NameObject("/CA"): FloatObject(0.005),
            NameObject("/Rect"): ArrayObject([
                FloatObject(x0),
                FloatObject(y0),
                FloatObject(x0 + width),
                FloatObject(y0 + width)
            ]),
            NameObject("/QuadPoints"): ArrayObject([
                FloatObject(x0),
                FloatObject(y0 + width),
                FloatObject(x0 + width),
                FloatObject(y0 + width),
                FloatObject(x0),
                FloatObject(y0),
                FloatObject(x0 + width),
                FloatObject(y0)
            ]),
        })

        return highlight

    def _add_highlight(self, x0, y0, width, height, comment, author=''):
        highlight = self._create_highlight(x0, y0, width, height, comment, author)
        highlight_ref = self.pdf._addObject(highlight)

        if "/Annots" in self.pdf.getPage(0):
            self.pdf.getPage(0)[NameObject("/Annots")].append(highlight_ref)
        else:
            self.pdf.getPage(0)[NameObject("/Annots")] = ArrayObject([highlight_ref])
        
        