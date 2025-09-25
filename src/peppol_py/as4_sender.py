import requests
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import email.encoders
from lxml import etree

from .exception import make_sendpeppol_error
from .wsse import encrypt_as4_document
from .wsse import sign_as4_envelope_and_body
from .wsse import insert_encryption_info_in_as4_envelope
from .as4 import generate_as4_envelope

def get_headers_and_body_for_posting_as4_document(document_content, document_xml, utc_timestamp, document_type, process_type, sender_id, receiver_id, to_party_id, xmlsec_path, keyfile, keyfile_password, sender_cert, receiver_cert, service_provider_id):
    message, gzip, attachment_id = make_as4_message_to_post(utc_timestamp, document_type, process_type, sender_id, receiver_id, to_party_id, document_content, xmlsec_path, keyfile, keyfile_password, sender_cert, receiver_cert, service_provider_id)

    related = MIMEMultipart('related')

    mt = MIMEApplication(message, 'soap+xml', email.encoders.encode_7or8bit)
    mt.add_header("Content-ID", "<root.message@cxf.apache.org>")
    related.attach(mt)

    mt = MIMEApplication(gzip, 'octet-stream')
    mt.add_header("Content-ID", f'<{attachment_id[4:]}>')
    related.attach(mt)

    # phase4 needs CRLF, oxalis is fine...
    body = bytes(related).replace(b'\n', b'\r\n')
    headers = dict(related.items())

    return body, headers

def post_edelivery_as4_document(endpoint_url, body, headers, timeout):
    try:
        r = requests.post(endpoint_url, data=body, headers=headers, timeout=timeout)
    except (ConnectionError, requests.exceptions.RequestException) as e:
        raise make_sendpeppol_error(str(e), 'server-error', temporary=True, url=endpoint_url)

    try:
        response_xml = etree.fromstring(r.content)
    except (etree.XMLSyntaxError, ValueError) as e:
        raise make_sendpeppol_error(str(e), 'server-error', temporary=True, url=endpoint_url)

    if not r.status_code == 200 or response_xml.find('.//{*}Header//{*}Receipt') is None:
        error_node = response_xml.find('.//{*}Error')
        error_msg = None
        if error_node is not None:
            error_msg = error_node.findtext('{*}ErrorDetail')

        exc_text = "Endpoint error"
        if error_msg:
            exc_text += ': ' + error_msg

        e = make_sendpeppol_error(
            exc_text, 'server-error', temporary=True, url=endpoint_url,
            endpoint={
                'status_code': r.status_code,
                'error_xml': etree.tostring(error_node if error_node is not None else response_xml, pretty_print=True).decode(),
                'error_msg': error_msg,
            })

        raise e

def make_as4_message_to_post(utc_timestamp, document_type, process_type, sender_id, receiver_id, to_party_id, document_content, xmlsec_path, keyfile, password, sender_cert, receiver_cert, service_provider_id):

    cipher_value, encrypted_gzipped_content, document_hash = encrypt_as4_document(document_content, receiver_cert, xmlsec_path)

    attachment_id, envelope, messaging, body = generate_as4_envelope(utc_timestamp, document_type, process_type, sender_id, receiver_id, to_party_id, service_provider_id)

    sign_as4_envelope_and_body(envelope, attachment_id, document_hash, body, messaging, sender_cert, keyfile, password)

    insert_encryption_info_in_as4_envelope(envelope, receiver_cert, cipher_value, attachment_id)

    message = etree.tostring(envelope)

    #print("AS4 message:", etree.tostring(envelope, pretty_print=True).decode('utf-8'))

    return message, encrypted_gzipped_content, attachment_id
