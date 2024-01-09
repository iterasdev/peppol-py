import hashlib
from base64 import b64encode
import io
from lxml import etree
import xml.etree.ElementTree as ET

# definition of "canonical":
# - have all namespaces so that it is valid xml (even if this is not what is submitted over the network)
# - be transformed using c14n (NOT c14n2!) with the exclude option
# - proper indention depending on where in the tree the element is situated
def canonical_xml(element, indention_level=0):
    out = io.BytesIO()
    ET.indent(element, " ", indention_level)
    etree.ElementTree(element).write(out, method="c14n", exclusive=True)
    return out.getvalue()

def generate_hash(element, indention_level=0):
    return b64encode(hashlib.sha256(canonical_xml(element, indention_level)).digest()).decode('utf-8')

def hash_file(filename):
    with open(filename, 'rb') as f:
        file_contents = f.read()
        return b64encode(hashlib.sha256(file_contents).digest()).decode('ascii')
