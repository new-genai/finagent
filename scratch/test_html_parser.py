from html.parser import HTMLParser

class HTMLTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = []
        self.current_cell = []
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag in ('td', 'th'):
            self.in_cell = True
            self.current_cell = []
        elif tag == 'tr':
            self.current_row = []

    def handle_endtag(self, tag):
        if tag in ('td', 'th'):
            if self.in_cell:
                self.current_row.append("".join(self.current_cell).strip())
                self.in_cell = False
        elif tag == 'tr':
            # Only append if we actually got columns in this row
            if self.current_row:
                self.rows.append(self.current_row)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

# Test with nested tags and colspan
complex_html = """
<table>
  <tr>
    <th>Header 1</th>
    <th>Header 2 with <b>bold</b> and <i>italic</i></th>
  </tr>
  <tr>
    <td colspan="2">Span cell</td>
  </tr>
  <tr>
    <td>Val 1</td>
    <td>Val 2</td>
  </tr>
</table>
"""

parser = HTMLTableParser()
parser.feed(complex_html)
print("Extracted rows:")
for r in parser.rows:
    print(r)
