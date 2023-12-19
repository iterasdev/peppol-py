import hashlib
from base64 import b64encode
import io
import gzip
from lxml import etree

# the payload must / will be:
# - have all namespaces so that it is valid xml (even if this is not what is submitted over the network)
# - be transformed to a "cannonical" c14n (NOT c14n2!) representation using the exclude option
# - and must have the proper indention!
def generate_hash(element):
    out = io.BytesIO()
    etree.ElementTree(element).write(out, method="c14n", exclusive=True)
    return b64encode(hashlib.sha256(out.getvalue()).digest()).decode('utf-8')

# the document will be:
# - be transformed to a "cannonical" c14n (NOT c14n2!) representation using the exclude option
# - be gzipped (even if different implementations zips differently, the level is not even specified)
def generate_gzipped_document(document):
    xmldoc = etree.fromstring(document)
    et = etree.ElementTree(xmldoc)
    out = io.BytesIO()
    et.write(out, method="c14n", exclusive=True)
    return gzip.compress(out.getvalue())

def generate_document_hash(document):
    gzip_document = generate_gzipped_document(document)
    return [gzip_document, b64encode(hashlib.sha256(gzip_document).digest()).decode('ascii')]
