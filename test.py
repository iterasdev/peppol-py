from wsse import encrypt_using_external_xmlsec, encrypt, sign
from as4 import envelope_as_string, generate_as4_envelope, document_id

import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# logging
import http.client as http_client
import logging

def generate_as4_message_to_post(filename):
    doc_id = document_id()
    
    file_contents = ''
    with open(filename, 'r') as f:
        file_contents = f.read().encode('utf-8')

    envelope, messaging, body = generate_as4_envelope(file_contents, doc_id)

    keyfile = "test.key.pem"
    certfile = "cert.pem"
    their_cert = "server-cert.pem"
    password = ''

    cipher_value, encrypted_gzip, document_hash = encrypt_using_external_xmlsec(filename, their_cert)

    sign(envelope, doc_id, document_hash, body, messaging, keyfile, certfile, password)
    encrypt(envelope, their_cert, cipher_value, doc_id)

    doc = envelope_as_string(envelope)
    #print(doc)

    return [doc, encrypted_gzip, doc_id]

def enable_logging():
    http_client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def post_multipart(url, filename):
    enable_logging()

    document, gzip, doc_id = generate_as4_message_to_post(filename)

    related = MIMEMultipart('related')

    mt = MIMEText('application', 'soap+xml', 'utf8')
    mt.set_payload(document)
    mt.replace_header("Content-Transfer-Encoding", "Binary")
    mt.add_header("Content-ID", "<root.message@cxf.apache.org>")
    related.attach(mt)

    mt = MIMEApplication(gzip, "gzip")
    mt.add_header("Content-Transfer-Encoding", "Binary")
    mt.add_header("Content-ID", '<' + doc_id[4:] + '>')
    related.attach(mt)

    # java needs CRLF
    body = related.__bytes__().replace(b'\n', b'\r\n')
    headers = dict(related.items())

    r = requests.post(url, data=body, headers=headers)
    print(r.text)
    
# 9922:ngtbcntrlp1001
# 9922:NGTBCNTRLP1001
receiver = '9928:CY99990011B' # final URL er buggy
receiver = '0188:2011001016148' # good example
receiver = '9922:NGTBCNTRLP1001' # from test certification file

# why doesn't test cert do this?
#smp_domain = get_domain_using_sml(receiver)

# ok
#smp_domain = get_domain_using_http(receiver)
#smp_contents = get_smp_info(smp_domain, receiver)
#extract_as4_information(smp_contents)

#generate_as4_message_to_post('TestFile_003__BISv3_Invoice.xml')
#url = 'https://oxalis.beta.iola.dk/as4'
url = 'https://phase4-controller.testbed.peppol.org/as4'
post_multipart(url, 'PEPPOL_TestCase_0232_20231222T0948Z/TestFile_001__BISv3_Invoice.xml')
