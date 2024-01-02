import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# logging
import http.client as http_client
import logging

from wsse import encrypt_using_external_xmlsec, encrypt, sign
from as4 import envelope_as_string, generate_as4_envelope, document_id

def post_multipart(url, xmlsec_path, filename, keyfile, password, certfile, their_cert, logging):
    document, gzip, doc_id = generate_as4_message_to_post(filename, xmlsec_path, keyfile,
                                                          password, certfile, their_cert, logging)

    related = MIMEMultipart('related')

    mt = MIMEText('application', 'soap+xml', 'utf8')
    mt.set_payload(document)
    mt.replace_header("Content-Transfer-Encoding", "Binary")
    mt.add_header("Content-ID", "<root.message@cxf.apache.org>")
    related.attach(mt)

    mt = MIMEApplication(gzip, "gzip")
    mt.add_header("Content-Transfer-Encoding", "Binary")
    mt.add_header("Content-ID", f'<{doc_id[4:]}>')
    related.attach(mt)

    # phase4 needs CRLF, oxalis is fine...
    body = related.__bytes__().replace(b'\n', b'\r\n')
    headers = dict(related.items())

    r = requests.post(url, data=body, headers=headers)
    status = r.status_code ==  200 and 'errorCode' not in r.text
    if logging:
        print("HTTP status:", r.status_code)
        print("response:", r.text)

    print("status:", status)
    return status

def generate_as4_message_to_post(filename, xmlsec_path, keyfile, password, certfile, their_cert, logging):
    doc_id = document_id()

    envelope, messaging, body = generate_as4_envelope(filename, doc_id)

    cipher_value, encrypted_gzip, document_hash = encrypt_using_external_xmlsec(xmlsec_path, filename, their_cert)

    sign(envelope, doc_id, document_hash, body, messaging, keyfile, certfile, password)
    encrypt(envelope, their_cert, cipher_value, doc_id)

    doc = envelope_as_string(envelope)
    if logging:
        print("AS4 document:", doc)

    return [doc, encrypted_gzip, doc_id]

def enable_logging():
    http_client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
