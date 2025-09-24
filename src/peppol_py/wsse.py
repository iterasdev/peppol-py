"""
Functions for WS-Security (WSSE) signing + encrypting
"""

import base64
import io
from pathlib import Path

from lxml import etree
import xmlsec
import xml.etree.ElementTree
import hashlib
import gzip

from .xmlhelpers import get_element_maker
from .constants import ENV_NS, WSSE_NS, WSU_NS, WSS_BASE
from .exception import make_sendpeppol_error

DS_NS = 'http://www.w3.org/2000/09/xmldsig#'
ENC_NS = 'http://www.w3.org/2001/04/xmlenc#'
ENC11_NS = 'http://www.w3.org/2009/xmlenc11#'
WSSE11_NS = 'http://docs.oasis-open.org/wss/oasis-wss-wssecurity-secext-1.1.xsd'

XML_CANONICAL_C14N = 'http://www.w3.org/2001/10/xml-exc-c14n#'
WSS_ATTACHMENT_SIGNATURE_TRANSFORM = 'http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Content-Signature-Transform'

WSS_BASE64B_ENCODING_TYPE = WSS_BASE + 'oasis-200401-wss-soap-message-security-1.0#Base64Binary'
WSS_X509TOKEN = WSS_BASE + 'oasis-200401-wss-x509-token-profile-1.0#X509v3'

XML_SHA256 = 'http://www.w3.org/2001/04/xmlenc#sha256'
XML_RSA_SHA256 = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
XML_RSA_OAEP = 'http://www.w3.org/2009/xmlenc11#rsa-oaep'
XML_MGF_SHA256 = 'http://www.w3.org/2009/xmlenc11#mgf1sha256'

NAMESPACES = {
    'env': ENV_NS,
    'wsu': WSU_NS,
    'wsse': WSSE_NS,
    'wsse11': WSSE11_NS,
    'ec': XML_CANONICAL_C14N,
    'xenc': ENC_NS,
    'xenc11': ENC11_NS,
    'ds': DS_NS
}

# We need to manually "craft" a signature because xmlsec doesn't
# properly handle external content. It does support cid and tries to
# resolve it to a file in the current working directory, but this only
# works if the file referenced is an xml file. This standard makes no
# sense, why would you use a "canonical" (c14n) encoding before
# gzipping, if gzip itself is implementation specific?
def sign_as4_envelope_and_body(envelope, attachment_id, doc_hash, body, messaging, cert, keyfile, password):
    E, ns = get_element_maker(NAMESPACES)
    header = envelope.find(ns("env", 'Header'))
    security = header.find(ns("wsse", 'Security'))

    security_token = generate_binary_security_token_xml(E, ns, cert, 'signkey')
    security.insert(0, security_token)

    # definition of "canonical":
    # - have all namespaces so that it is valid xml (even if this is not what is submitted over the network)
    # - be transformed using c14n (NOT c14n2!) with the exclude option
    # - proper indentation depending on where in the tree the element is situated
    def canonical_as4_xml(element, indentation_level=0):
        out = io.BytesIO()
        xml.etree.ElementTree.indent(element, ' ', indentation_level)
        etree.ElementTree(element).write(out, method='c14n', exclusive=True)
        return out.getvalue()

    def generate_xml_hash(element, indentation_level=0):
        return base64.b64encode(hashlib.sha256(canonical_as4_xml(element, indentation_level)).digest()).decode('utf-8')

    messaging_hash = generate_xml_hash(messaging, 5)
    messaging_id = messaging.get(ns("wsu", "Id"))

    body_hash = generate_xml_hash(body)
    body_id = body.get(ns("wsu", "Id"))

    signature_info = E(ns('ds', 'SignedInfo'),
                       E(ns('ds', 'CanonicalizationMethod'),
                         E(ns('ec', 'InclusiveNamespaces'), PrefixList='env'),
                         Algorithm=XML_CANONICAL_C14N),
                       E(ns('ds', 'SignatureMethod'), Algorithm=XML_RSA_SHA256),
                       generate_digest_reference(E, ns, body_id, XML_CANONICAL_C14N, body_hash),
                       generate_digest_reference(E, ns, messaging_id, XML_CANONICAL_C14N, messaging_hash),
                       generate_digest_reference(E, ns, attachment_id, WSS_ATTACHMENT_SIGNATURE_TRANSFORM, doc_hash))

    key = xmlsec.Key.from_file(keyfile, xmlsec.KeyFormat.PEM, password)
    key.load_cert_from_memory(cert, xmlsec.KeyFormat.PEM)

    ctx = xmlsec.SignatureContext()
    ctx.key = key

    signature_info_str = canonical_as4_xml(signature_info).decode('utf-8')
    # why is env namespace missing?
    signature_info_str = signature_info_str.replace(
        '<ds:SignedInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">',
        f'<ds:SignedInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:env="{ENV_NS}">')

    sign = ctx.sign_binary(signature_info_str, xmlsec.constants.TransformRsaSha256)
    signature_value = base64.b64encode(sign).decode('utf-8')

    key_info = generate_key_info_with_security_token(E, ns, security_token)

    security.insert(1, E(ns("ds", "Signature"),
                         signature_info,
                         E(ns("ds", "SignatureValue"), signature_value),
                         key_info))

def insert_encryption_info_in_as4_envelope(envelope, receiver_cert, cipher_value, attachment_id):
    E, ns = get_element_maker(NAMESPACES)
    header = envelope.find(ns("env", 'Header'))
    security_node = header.find(ns("wsse", 'Security'))

    security_token = generate_binary_security_token_xml(E, ns, receiver_cert, 'encryptkey')
    key_info = generate_key_info_with_security_token(E, ns, security_token)

    encrypted_key = E(ns('xenc', 'EncryptedKey'),
                      E(ns('xenc', 'EncryptionMethod'),
                        E(ns('ds', 'DigestMethod'), Algorithm=XML_SHA256),
                        E(ns('xenc11', 'MGF'), Algorithm=XML_MGF_SHA256),
                        Algorithm=XML_RSA_OAEP),
                      key_info,
                      E(ns('xenc', 'CipherData'),
                        E(ns('xenc', 'CipherValue'), cipher_value)),
                      E(ns('xenc', 'ReferenceList'),
                        E(ns('xenc', 'DataReference'), URI='#encrypteddata')),
                      Id='encryptedkey')

    encrypted_data = E(ns('xenc', 'EncryptedData'),
                       E(ns('xenc', 'EncryptionMethod'), Algorithm='http://www.w3.org/2009/xmlenc11#aes128-gcm'),
                       E(ns('ds', 'KeyInfo'),
                         E(ns('wsse', 'SecurityTokenReference'),
                           E(ns('wsse', 'Reference'), URI='#encryptedkey'),
                           { ns('wsse11', 'TokenType'):
                             'http://docs.oasis-open.org/wss/oasis-wss-soap-message-security-1.1#EncryptedKey' }
                           )),
                       E(ns('xenc', 'CipherData'),
                         E(ns('xenc', 'CipherReference'),
                           E(ns('xenc', 'Transforms'),
                             E(ns('ds', 'Transform'),
                               Algorithm='http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Ciphertext-Transform')
                             ),
                           URI=attachment_id)),
                       Id='encrypteddata', MimeType='application/octet-stream',
                       Type='http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Content-Only')

    security_node.insert(0, security_token)
    security_node.insert(1, encrypted_key)
    security_node.insert(2, encrypted_data)

def encrypt_as4_document(document_content, receiver_cert, xmlsec_path):
    E, ns = get_element_maker(NAMESPACES)

    gzipped_content = gzip.compress(document_content, compresslevel=6)
    gzipped_document_hash = base64.b64encode(hashlib.sha256(gzipped_content).digest()).decode('ascii')

    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(prefix='temp-sendpeppol-certfile-', suffix='.pem') as receiver_certfile:
        receiver_certfile.write(receiver_cert)
        receiver_certfile.flush()

        # FIXME: it would be better to use the Python wrapper so we could
        # avoid all this file mangling, but it doesn't support xmlsec 1.3
        # yet
        xmlsec_args = [
            xmlsec_path, '--encrypt',
            '--pubkey-cert-pem', receiver_certfile.file.name,
            '--session-key', 'aes-128',
            '--binary-data', '/dev/stdin',
            #'--verbose'
            '--lax-key-search',
            Path(__file__).parent / 'data' / 'xmlsec' / 'sendpeppol_encrypt_template.xml',
        ]

        xmlsec_popen = subprocess.Popen(
            xmlsec_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        xmlsec_output, xmlsec_errors = xmlsec_popen.communicate(input=gzipped_content, timeout=20)
        if xmlsec_popen.returncode != 0:
            raise make_sendpeppol_error('xmlsec: ' + xmlsec_errors.decode(), 'encryption')

    xmlsec_xml = etree.fromstring(xmlsec_output)

    cipher_values = [a.text for a in xmlsec_xml.iter() if a.tag == ns("xenc", 'CipherValue')]
    cipher_value = cipher_values[0].replace('\n', '')
    encrypted_gzip_b64 = cipher_values[1].replace('\n', '')
    encrypted_gzip = base64.b64decode(encrypted_gzip_b64.encode('ascii'))

    return cipher_value, encrypted_gzip, gzipped_document_hash

### HELPERS ###

def generate_digest_reference(E, ns, ref_id, transform, digest_value):
    if transform != WSS_ATTACHMENT_SIGNATURE_TRANSFORM:
        ref_id = '#' + ref_id

    return E(ns('ds', 'Reference'),
             E(ns('ds', 'Transforms'),
               E(ns('ds', 'Transform'), Algorithm=transform)),
             E(ns('ds', 'DigestMethod'), Algorithm=XML_SHA256),
             E(ns('ds', 'DigestValue'), digest_value),
             URI=ref_id)

def generate_key_info_with_security_token(E, ns, security_token):
    return E(ns('ds', 'KeyInfo'),
             E(ns('wsse', 'SecurityTokenReference'),
               E(ns('wsse', 'Reference'),
                 ValueType=security_token.get('ValueType'),
                 URI=f"#{security_token.get(ns('wsu', 'Id'))}"),
               { ns('wsse', 'TokenType'): security_token.get('ValueType') }))

def generate_binary_security_token_xml(E, ns, cert, identifier):
    import asn1crypto.pem

    type_name, headers, der_bytes = asn1crypto.pem.unarmor(cert)
    b64_cert = base64.b64encode(der_bytes).decode('utf-8')

    return E(ns('wsse', 'BinarySecurityToken'), b64_cert,
             {ns('wsu', 'Id'): identifier, 'EncodingType': WSS_BASE64B_ENCODING_TYPE, 'ValueType': WSS_X509TOKEN})
