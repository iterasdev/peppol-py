"""
Functions for WS-Security (WSSE) signing + encrypting
"""

import base64
import textwrap
import os

from lxml import etree
from OpenSSL import crypto
import xmlsec
from base64 import b64decode

from hashing import generate_hash, hash_file
from xmlhelpers import get_element_maker
from constants import BASE64B, X509TOKEN, C14N, ATTACHMENT
from constants import ENV_NS, WSSE_NS, WSSE11_NS, WSU_NS, ENC_NS, ENC11_NS, DS_NS
from constants import SHA256, RSA_SHA256, RSA_OAEP, MGF_SHA256

NAMESPACES = {
    'env': ENV_NS,
    'wsu': WSU_NS,
    'wsse': WSSE_NS,
    'wsse11': WSSE11_NS,
    'ec': C14N,
    'xenc': ENC_NS,
    'xenc11': ENC11_NS,
    'ds': DS_NS
}

# We need to manually "craft" a signature because xmlsec doesn't
# properly handle external content. It does support cid and tries to
# resolve it to a file in the current working directory, but this only
# works if the file referenced is an xml file. This standard makes no
# sense, why would you use a "cannonical" (c14n) encoding before
# gzipping, if gzip itself is implementation specific?
def sign(envelope, doc_id, doc_hash, body, messaging, keyfile, certfile, password):
    E, ns = get_element_maker(NAMESPACES)
    header = envelope.find(ns("env", 'Header'))
    security = header.find(ns("wsse", 'Security'))

    security_token = _create_binary_security_token(E, ns, certfile, 'signkey')
    security.insert(0, security_token)

    # hax hax
    messaging_str = etree.tostring(messaging, pretty_print=True).decode('utf-8')
    # "proper" indention
    messaging_str = textwrap.indent(messaging_str, '    ')
    messaging_hash = generate_hash(etree.fromstring(messaging_str))
    messaging_id = messaging.get(ns("wsu", "Id"))

    body_hash = generate_hash(body)
    body_id = body.get(ns("wsu", "Id"))

    signature_info = _signature_info(E, ns, doc_id, doc_hash, body_id, body_hash, messaging_id, messaging_hash)

    ctx = xmlsec.SignatureContext()
    ctx.key = _sign_key(keyfile, certfile, password)

    sign = ctx.sign_binary(etree.tostring(signature_info), xmlsec.constants.TransformRsaSha256)
    signature_value = base64.b64encode(sign).decode('utf-8')

    key_info = _create_key_info_bst(E, ns, security_token)

    security.insert(1, E(ns("ds", "Signature"),
                         signature_info,
                         E(ns("ds", "SignatureValue"), signature_value),
                         key_info))

def encrypt(envelope, certfile, cipher_value, doc_id):
    E, ns = get_element_maker(NAMESPACES)
    header = envelope.find(ns("env", 'Header'))
    security = header.find(ns("wsse", 'Security'))

    security_token = _create_binary_security_token(E, ns, certfile, 'encryptkey')
    key_info = _create_key_info_bst(E, ns, security_token)

    security.insert(0, security_token)
    security.insert(1, _create_encrypted_key(E, ns, key_info, cipher_value))
    security.insert(2, _create_encrypted_data(E, ns, doc_id))

def encrypt_using_external_xmlsec(xmlsec_path, filename, their_cert):
    E, ns = get_element_maker(NAMESPACES)

    base = os.path.basename(filename)
    target = '/tmp/' + base
    xmlsec_result = '/tmp/xmlsec-result.xml'

    os.system(f"cp {filename} {target} && gzip -f {target}")

    target += '.gz'

    document_hash = hash_file(target)

    os.system(f"{xmlsec_path} --encrypt --pubkey-cert-pem {their_cert} --session-key aes-128 --binary-data {target} --output {xmlsec_result} --verbose --lax-key-search encryption.xml")

    with open(xmlsec_result, 'r') as f:
        file_contents = f.read()
        xmlsec_xml = etree.fromstring(file_contents)

        cipher_values = [a.text for a in xmlsec_xml.iter() if a.tag == ns("xenc", 'CipherValue')]
        cipher_value = cipher_values[0].replace('\n', '')
        encrypted_gzip_b64 = cipher_values[1].replace('\n', '')
        encrypted_gzip = b64decode(encrypted_gzip_b64.encode('ascii'))

    return [cipher_value, encrypted_gzip, document_hash]

### HELPERS ###

def _sign_key(keyfile, certfile, password):
    key = xmlsec.Key.from_file(keyfile, xmlsec.KeyFormat.PEM, password)
    key.load_cert_from_file(certfile, xmlsec.KeyFormat.PEM)
    return key

def _add_ref(E, ns, ref_id, transform, digest_value):
    if transform != ATTACHMENT:
        ref_id = '#' + ref_id

    return E(ns("ds", "Reference"),
             E(ns("ds", "Transforms"),
               E(ns("ds", "Transform"), Algorithm=transform)),
             E(ns("ds", "DigestMethod"), Algorithm=SHA256),
             E(ns("ds", "DigestValue"), digest_value) 
             ,URI=ref_id)

def _signature_info(E, ns, doc_id, doc_hash, body_id, body_hash, messaging_id, messaging_hash):
    return E(ns("ds", "SignedInfo"),
             E(ns("ds", "CanonicalizationMethod"),
               E(ns("ec", "InclusiveNamespaces"), PrefixList="env"),
               Algorithm=C14N),
             E(ns("ds", "SignatureMethod"), Algorithm=RSA_SHA256),
             _add_ref(E, ns, body_id, C14N, body_hash),
             _add_ref(E, ns, messaging_id, C14N, messaging_hash),
             _add_ref(E, ns, doc_id, ATTACHMENT, doc_hash))

def _create_key_info_bst(E, ns, security_token):
    return E(ns("ds", "KeyInfo"),
             E(ns("wsse", "SecurityTokenReference"),
               E(ns("wsse", "Reference"),
                 ValueType=security_token.get('ValueType'),
                 URI=f'#{security_token.get(ns("wsu", "Id"))}'),
               { ns("wsse", 'TokenType'): security_token.get('ValueType') }))

def _create_binary_security_token(E, ns, certfile, id):
    with open(certfile) as fh:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, fh.read())
        b64_cert = base64.b64encode(crypto.dump_certificate(crypto.FILETYPE_ASN1, cert)).decode('utf-8')

        return E(ns("wsse", "BinarySecurityToken"), b64_cert,
                 { ns("wsu", "Id"): id, "EncodingType": BASE64B, "ValueType": X509TOKEN })

def _create_encrypted_key(E, ns, key_info, cipher_value):
    return E(ns("xenc", "EncryptedKey"),
             E(ns("xenc", "EncryptionMethod"),
               E(ns("ds", "DigestMethod"), Algorithm=SHA256),
               E(ns("xenc11", "MGF"), Algorithm=MGF_SHA256),
               Algorithm=RSA_OAEP),
             key_info,
             E(ns("xenc", "CipherData"),
               E(ns("xenc", "CipherValue"), cipher_value)),
             E(ns("xenc", "ReferenceList"),
               E(ns("xenc", "DataReference"), URI="#encrypteddata")),
             Id="encryptedkey")

def _create_encrypted_data(E, ns, doc_id):
    return E(ns("xenc", "EncryptedData"),
             E(ns("xenc", "EncryptionMethod"), Algorithm="http://www.w3.org/2009/xmlenc11#aes128-gcm"),
             E(ns("ds", "KeyInfo"),
               E(ns("wsse", "SecurityTokenReference"),
                 E(ns("wsse", "Reference"), URI="#encryptedkey"),
                 { ns("wsse11", "TokenType"):
                   "http://docs.oasis-open.org/wss/oasis-wss-soap-message-security-1.1#EncryptedKey" }
                 )
               ),
             E(ns("xenc", "CipherData"),
               E(ns("xenc", "CipherReference"),
                 E(ns("xenc", "Transforms"),
                   E(ns("ds", "Transform"),
                     Algorithm="http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Ciphertext-Transform")
                   ),
                 URI=doc_id),
               ),
             Id="encrypteddata", MimeType="application/octet-stream",
             Type="http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Content-Only")
