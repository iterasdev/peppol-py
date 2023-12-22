import hashlib
from base64 import b64encode
import io
from lxml import etree

# the payload must / will be:
# - have all namespaces so that it is valid xml (even if this is not what is submitted over the network)
# - be transformed to a "cannonical" c14n (NOT c14n2!) representation using the exclude option
# - and must have the proper indention!
def generate_hash(element):
    out = io.BytesIO()
    etree.ElementTree(element).write(out, method="c14n", exclusive=True)
    return b64encode(hashlib.sha256(out.getvalue()).digest()).decode('utf-8')

def hash_file(filename):
    with open(filename, 'rb') as f:
        file_contents = f.read()
        return b64encode(hashlib.sha256(file_contents).digest()).decode('ascii')
