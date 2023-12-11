"""
Functions for WS-Security (WSSE) signing + encrypting

Code based on python-zeep & py-wsee
"""

import base64
import io

from lxml import etree
from OpenSSL import crypto
import xmlsec

from constants import BASE64B, X509TOKEN, DS_NS, ENC_NS, ENV_NS, WSSE_NS, ATTACHMENT, C14N, WSU_NS
from xmlhelpers import ensure_id, ns
from hashing import generate_hash

def sign(envelope, doc_id, doc_hash, body, messaging, keyfile, certfile, password):
    header = envelope.find(ns(ENV_NS, 'Header'))
    security = header.find(ns(WSSE_NS, 'Security'))

    security_token = create_binary_security_token(certfile)
    security.insert(0, security_token)
    
    key = _sign_key(keyfile, certfile, password)

    messaging_hash = generate_hash(messaging)
    messaging_id = messaging.get(etree.QName(WSU_NS, 'Id'))
    body_hash = generate_hash(body)
    body_id = body.get(etree.QName(WSU_NS, 'Id'))

    sig_info = signature_info(doc_id, doc_hash, body_id, body_hash, messaging_id, messaging_hash)
    #print(sig_info)

    ctx = xmlsec.SignatureContext()
    ctx.key = key

    xml_sig_info = etree.fromstring(sig_info.replace("<ds:SignedInfo>", "<ds:SignedInfo xmlns:ds='{}'>".format(DS_NS)))
    et = etree.ElementTree(xml_sig_info)
    out = io.BytesIO()
    et.write(out, method="c14n", exclusive=True)

    sign = ctx.sign_binary(out.getvalue(), xmlsec.constants.TransformRsaSha256)
    signature_value = base64.b64encode(sign).decode('utf-8')
    #print(signature_value)

    key_info = etree.tostring(create_key_info_bst(security_token)).decode('utf-8')

    signature = """
<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
%s
<ds:SignatureValue>%s</ds:SignatureValue>
%s
</ds:Signature>
    """ % (sig_info, signature_value, key_info)

    security.insert(1, etree.fromstring(signature))

def encrypted_data_element(cid, ek_id):
    return """<xenc:EncryptedData xmlns:xenc="http://www.w3.org/2001/04/xmlenc#" MimeType="application/octet-stream" Type="http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Content-Only"><xenc:EncryptionMethod Algorithm="http://www.w3.org/2009/xmlenc11#aes128-gcm"/>
 <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
   <wsse:SecurityTokenReference xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsse11="http://docs.oasis-open.org/wss/oasis-wss-wssecurity-secext-1.1.xsd" wsse11:TokenType="http://docs.oasis-open.org/wss/oasis-wss-soap-message-security-1.1#EncryptedKey">
    <wsse:Reference URI="#{}"/>
   </wsse:SecurityTokenReference>
 </ds:KeyInfo>
 <xenc:CipherData>
  <xenc:CipherReference URI="{}">
   <xenc:Transforms>
    <ds:Transform xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Algorithm="http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Ciphertext-Transform"/>
   </xenc:Transforms>
  </xenc:CipherReference>
 </xenc:CipherData>
</xenc:EncryptedData>""".format(ek_id, cid)

def encrypt(envelope, data_id, data, certfile):
    header = envelope.find(ns(ENV_NS, 'Header'))
    security = header.find(ns(WSSE_NS, 'Security'))

    manager = xmlsec.KeysManager()
    key = xmlsec.Key.from_file(certfile, xmlsec.KeyFormat.CERT_PEM, None)
    manager.add_key(key)

    # EncryptedData node
    enc_data = xmlsec.template.encrypted_data_create(
        envelope,
        xmlsec.constants.TransformAes128Gcm,
        type=xmlsec.EncryptionType.ELEMENT,
        ns='xenc',
    )
    xmlsec.template.encrypted_data_ensure_cipher_value(enc_data)
    key_info = xmlsec.template.encrypted_data_ensure_key_info(enc_data, ns='ds')
    enc_key = xmlsec.template.add_encrypted_key(key_info, xmlsec.Transform.RSA_OAEP)
    xmlsec.template.encrypted_data_ensure_cipher_value(enc_key)

    enc_ctx = xmlsec.EncryptionContext(manager)
    enc_ctx.key = xmlsec.Key.generate(
        xmlsec.constants.KeyDataAes, 128, xmlsec.constants.KeyDataTypeSession
    )
    enc_data = enc_ctx.encrypt_binary(enc_data, data)

    cert_bst = create_binary_security_token(certfile)
    security.insert(0, cert_bst)

    ek_id = ensure_id(enc_key, 'EK')

    # ds:KeyInfo node referencing the BinarySecurityToken
    enc_key.insert(1, create_key_info_bst(cert_bst))
    security.insert(1, enc_key)

    # xenc:EncryptedData
    enc_data_el = etree.fromstring(encrypted_data_element(data_id, ek_id))

    add_data_reference(enc_key, enc_data_el)

    security.insert(2, enc_data_el)

### HELPERS ###

def _sign_key(keyfile, certfile, password):
    key = xmlsec.Key.from_file(keyfile, xmlsec.KeyFormat.PEM, password)
    key.load_cert_from_file(certfile, xmlsec.KeyFormat.PEM)
    return key

def _add_ref(ref_id, transform, digest_value):
    return """
<ds:Reference URI="%s">
 <ds:Transforms>
  <ds:Transform Algorithm="%s"/>
 </ds:Transforms>
 <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
 <ds:DigestValue>%s</ds:DigestValue>
</ds:Reference>
    """ % (ref_id, transform, digest_value)

def signature_info(doc_id, doc_hash, body_id, body_hash, messaging_id, messaging_hash):
    return """
<ds:SignedInfo>
 <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#">
  <ec:InclusiveNamespaces xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#" PrefixList="env"/>
 </ds:CanonicalizationMethod>
 <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
%s
%s
%s
</ds:SignedInfo>
    """ % (_add_ref(doc_id, ATTACHMENT, doc_hash),
           _add_ref(body_id, C14N, body_hash),
           _add_ref(messaging_id, C14N, messaging_hash))

def add_data_reference(enc_key, enc_data):
    data_id = ensure_id(enc_data)
    ref_list = ensure_reference_list(enc_key)

    data_ref = etree.SubElement(ref_list, ns(ENC_NS, 'DataReference'))
    data_ref.set('URI', '#' + data_id)
    return data_ref

def ensure_reference_list(encrypted_key):
    ref_list = encrypted_key.find(ns(ENC_NS, 'ReferenceList'))
    if ref_list is None:
        ref_list = etree.SubElement(encrypted_key, ns(ENC_NS, 'ReferenceList'))
    return ref_list

def create_key_info_bst(security_token):
    key_info = etree.Element(ns(DS_NS, 'KeyInfo'), nsmap={'ds': DS_NS})

    sec_token_ref = etree.SubElement(key_info, ns(WSSE_NS, 'SecurityTokenReference'))
    sec_token_ref.set(ns(WSSE_NS, 'TokenType'), security_token.get('ValueType'))

    # reference BinarySecurityToken
    bst_id = ensure_id(security_token, 'BST')
    reference = etree.SubElement(sec_token_ref, ns(WSSE_NS, 'Reference'))
    reference.set('ValueType', security_token.get('ValueType'))
    reference.set('URI', '#%s' % bst_id)

    return key_info

def create_binary_security_token(certfile):
    node = etree.Element(ns(WSSE_NS, 'BinarySecurityToken'))
    node.set('EncodingType', BASE64B)
    node.set('ValueType', X509TOKEN)

    with open(certfile) as fh:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, fh.read())
        node.text = base64.b64encode(crypto.dump_certificate(crypto.FILETYPE_ASN1, cert))

    return node
