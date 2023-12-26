"""
Functions for WS-Security (WSSE) signing + encrypting

Code based on python-zeep & py-wsse
"""

import base64
import textwrap
import os

from lxml import etree
from OpenSSL import crypto
import xmlsec
from base64 import b64decode

from constants import BASE64B, X509TOKEN, DS_NS, ENV_NS, WSSE_NS, ATTACHMENT, C14N, WSU_NS, ENC_NS
from xmlhelpers import ns
from hashing import generate_hash, hash_file

# We need to manually "craft" a signature because xmlsec doesn't
# properly handle external content. It does support cid and tries to
# resolve it to a file in the current working directory, but this only
# works if the file referenced is an xml file. This standard makes no
# sense, why would you use a "cannonical" (c14n) encoding before
# gzipping, if gzip itself is implementation specific?
def sign(envelope, doc_id, doc_hash, body, messaging, keyfile, certfile, password):
    header = envelope.find(ns(ENV_NS, 'Header'))
    security = header.find(ns(WSSE_NS, 'Security'))

    security_token = _create_binary_security_token(certfile, 'signkey')
    security.insert(0, security_token)
    
    # hax hax
    messaging_str = etree.tostring(messaging, pretty_print=True).decode('utf-8')
    # "proper" indention
    messaging_str = textwrap.indent(messaging_str, '    ')
    messaging_hash = generate_hash(etree.fromstring(messaging_str))
    messaging_id = messaging.get(etree.QName(WSU_NS, 'Id'))

    body_hash = generate_hash(body)
    body_id = body.get(etree.QName(WSU_NS, 'Id'))

    signature_info = _signature_info(doc_id, doc_hash, body_id, body_hash, messaging_id, messaging_hash)

    ctx = xmlsec.SignatureContext()
    ctx.key = _sign_key(keyfile, certfile, password)

    sign = ctx.sign_binary(signature_info.encode('utf-8'), xmlsec.constants.TransformRsaSha256)
    signature_value = base64.b64encode(sign).decode('utf-8')

    key_info = _create_key_info_bst(security_token)

    signature = """
<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
%s
<ds:SignatureValue>%s</ds:SignatureValue>
%s
</ds:Signature>
    """ % (signature_info, signature_value, key_info)

    security.insert(1, etree.fromstring(signature))

def encrypt(envelope, certfile, cipher_value, doc_id):
    header = envelope.find(ns(ENV_NS, 'Header'))
    security = header.find(ns(WSSE_NS, 'Security'))

    security_token = _create_binary_security_token(certfile, 'encryptkey')
    key_info = _create_key_info_bst(security_token)

    security.insert(0, security_token)

    encrypted_key = _create_encrypted_key(key_info, cipher_value)
    security.insert(1, etree.fromstring(encrypted_key))

    encrypted_data = _create_encrypted_data(doc_id)
    security.insert(2, etree.fromstring(encrypted_data))

def encrypt_using_external_xmlsec(filename, their_cert):
    base = os.path.basename(filename)
    target = '/tmp/' + base
    xmlsec_result = '/tmp/xmlsec-result.xml'

    os.system("cp {} {} && gzip -f {}".format(filename, target, target))

    target += '.gz'

    document_hash = hash_file(target)

    os.system("~/Downloads/xmlsec1-1.3.2/install/bin/xmlsec1 --encrypt --pubkey-cert-pem {} --session-key aes-128 --binary-data {} --output {} --verbose --lax-key-search encryption.xml".format(their_cert, target, xmlsec_result))

    with open(xmlsec_result, 'r') as f:
        file_contents = f.read()
        xmlsec_xml = etree.fromstring(file_contents)

        cipher_values = [a.text for a in xmlsec_xml.iter() if a.tag == ns(ENC_NS, 'CipherValue')]
        cipher_value = cipher_values[0].replace('\n', '')
        encrypted_gzip_b64 = cipher_values[1].replace('\n', '')
        encrypted_gzip = b64decode(encrypted_gzip_b64.encode('ascii'))

    return [cipher_value, encrypted_gzip, document_hash]

### HELPERS ###

def _sign_key(keyfile, certfile, password):
    key = xmlsec.Key.from_file(keyfile, xmlsec.KeyFormat.PEM, password)
    key.load_cert_from_file(certfile, xmlsec.KeyFormat.PEM)
    return key

def _add_ref(ref_id, transform, digest_value):
    if transform != ATTACHMENT:
        ref_id = '#' + ref_id

    return """
<ds:Reference URI="%s">
 <ds:Transforms>
  <ds:Transform Algorithm="%s"></ds:Transform>
 </ds:Transforms>
 <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"></ds:DigestMethod>
 <ds:DigestValue>%s</ds:DigestValue>
</ds:Reference>""" % (ref_id, transform, digest_value)

def _signature_info(doc_id, doc_hash, body_id, body_hash, messaging_id, messaging_hash):
    return """<ds:SignedInfo xmlns:ds="%s" xmlns:env="%s">
 <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#">
  <ec:InclusiveNamespaces xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#" PrefixList="env"></ec:InclusiveNamespaces>
 </ds:CanonicalizationMethod>
 <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"></ds:SignatureMethod>%s%s%s
</ds:SignedInfo>""" % (
        DS_NS, ENV_NS,
        _add_ref(body_id, C14N, body_hash),
        _add_ref(messaging_id, C14N, messaging_hash),
        _add_ref(doc_id, ATTACHMENT, doc_hash)
    )

def _create_key_info_bst(security_token):
    key_info = etree.Element(ns(DS_NS, 'KeyInfo'), nsmap={'ds': DS_NS})

    sec_token_ref = etree.SubElement(key_info, ns(WSSE_NS, 'SecurityTokenReference'))
    sec_token_ref.set(ns(WSSE_NS, 'TokenType'), security_token.get('ValueType'))

    # reference BinarySecurityToken
    bst_id = security_token.get(etree.QName(WSU_NS, 'Id'))
    reference = etree.SubElement(sec_token_ref, ns(WSSE_NS, 'Reference'))
    reference.set('ValueType', security_token.get('ValueType'))
    reference.set('URI', '#%s' % bst_id)

    return etree.tostring(key_info).decode('utf-8')

def _create_binary_security_token(certfile, id):
    attribs = { etree.QName(WSU_NS, "Id"): id }
    node = etree.Element(ns(WSSE_NS, 'BinarySecurityToken'), attribs, nsmap={'wsu': WSU_NS})
    node.set('EncodingType', BASE64B)
    node.set('ValueType', X509TOKEN)

    with open(certfile) as fh:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, fh.read())
        node.text = base64.b64encode(crypto.dump_certificate(crypto.FILETYPE_ASN1, cert))

    return node

def _create_encrypted_key(key_info, cipher_value):
    return """
<xenc:EncryptedKey xmlns:xenc="http://www.w3.org/2001/04/xmlenc#" Id="encryptedkey">
 <xenc:EncryptionMethod Algorithm="http://www.w3.org/2009/xmlenc11#rsa-oaep">
  <ds:DigestMethod xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
  <xenc11:MGF xmlns:xenc11="http://www.w3.org/2009/xmlenc11#" Algorithm="http://www.w3.org/2009/xmlenc11#mgf1sha256"/>
 </xenc:EncryptionMethod>

 {}

 <xenc:CipherData>
  <xenc:CipherValue>{}</xenc:CipherValue>
 </xenc:CipherData>

 <xenc:ReferenceList>
  <xenc:DataReference URI="#encrypteddata"/>
 </xenc:ReferenceList>
</xenc:EncryptedKey>""".format(key_info, cipher_value)

def _create_encrypted_data(doc_id):
    return """
<xenc:EncryptedData xmlns:xenc="http://www.w3.org/2001/04/xmlenc#" Id="encrypteddata" MimeType="application/octet-stream" Type="http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Content-Only">

 <xenc:EncryptionMethod Algorithm="http://www.w3.org/2009/xmlenc11#aes128-gcm"/>

 <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
  <wsse:SecurityTokenReference xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsse11="http://docs.oasis-open.org/wss/oasis-wss-wssecurity-secext-1.1.xsd" wsse11:TokenType="http://docs.oasis-open.org/wss/oasis-wss-soap-message-security-1.1#EncryptedKey">
   <wsse:Reference URI="#encryptedkey"/>
  </wsse:SecurityTokenReference>
 </ds:KeyInfo>

 <xenc:CipherData>
  <xenc:CipherReference URI="{}">
   <xenc:Transforms>
    <ds:Transform xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Algorithm="http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Ciphertext-Transform"/>
   </xenc:Transforms>
  </xenc:CipherReference>
 </xenc:CipherData>
</xenc:EncryptedData>""".format(doc_id)

