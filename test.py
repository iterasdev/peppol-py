import hashlib
import dns.resolver
import urllib.request
import urllib.parse
from lxml import etree
from uuid import uuid4
from datetime import datetime

from wsse import sign
from xmlhelpers import ns
from constants import NS2, ENV_NS, WSSE_NS, WSU_NS

import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# logging
import http.client as http_client
import logging

sml_server = 'edelivery.tech.ec.europa.eu'
sml_server = 'acc.edelivery.tech.ec.europa.eu' # test

# SML: receiver -> domain (DNS)
# SMP: domain + path -> xml with service descriptions

def get_domain_using_http(receiver):
    smp_id = 'B-' + hashlib.md5((receiver.lower()).encode("utf-8")).hexdigest()
    return smp_id + '.iso6523-actorid-upis.' + sml_server

def get_domain_using_sml(receiver):
    smp_id = 'B-' + hashlib.md5((receiver.lower()).encode("utf-8")).hexdigest()
    name = smp_id + '.iso6523-actorid-upis.' + sml_server
    print(name)
    answers = dns.resolver.resolve(name, 'CNAME')
    domain = str(answers[0])
    if domain[-1] == '.':
        return domain[0:-1]
    else:
        return domain

def get_smp_info(domain, receiver):
    # all the available interfaces (invoice, credit note etc.)
    url = 'http://' + domain + "/iso6523-actorid-upis::" + receiver
    print("looking up", url)
    contents = urllib.request.urlopen(url).read()
    print(contents)
    return contents

invoice_end = urllib.parse.quote("billing:3.0::2.1")

def find_invoice_smp_document(smp_contents):
    root = etree.fromstring(smp_contents)
    for child in root:
        for el in child:
            if el.get('href').endswith(invoice_end):
                return el.get('href')

def extract_as4_information(smp_contents):
    invoice_url = find_invoice_smp_document(smp_contents)
    print("invoice url:", invoice_url)
    invoice_smp = urllib.request.urlopen(invoice_url).read()
    print(invoice_smp)
    root = etree.fromstring(invoice_smp)
    id = root.findall(".//{*}ParticipantIdentifier")[0].text
    print("id", id)
    as4_endpoint = root.findall(".//{*}EndpointReference")[0][0].text
    print("as4_endpoint", as4_endpoint)
    certificate = root.findall(".//{*}Certificate")[0].text
    print("cert:")
    print(certificate)

def generate_as4_envelope(document, doc_id):
    envelope = etree.Element(ns(ENV_NS, 'Envelope'), nsmap={'env': ENV_NS})
    header = etree.SubElement(envelope, ns(ENV_NS, 'Header'), nsmap={'env': ENV_NS})

    attribs = { etree.QName(ENV_NS, 'mustUnderstand'): "true", etree.QName(WSU_NS, "Id"): "_{}".format(uuid4()) }
    messaging = etree.SubElement(header, ns(NS2, 'Messaging'), attribs, nsmap={'ns2': NS2, 'wsu': WSU_NS})
    generate_as4_messaging_part(messaging, document, doc_id)

    etree.SubElement(header, ns(WSSE_NS, 'Security'),
                     { etree.QName(ENV_NS, 'mustUnderstand'): "true" },
                     nsmap={'wsse': WSSE_NS})

    body = etree.SubElement(envelope, ns(ENV_NS, 'Body'),
                            { etree.QName(WSU_NS, 'Id'): "_{}".format(uuid4()) },
                            nsmap={'env': ENV_NS, 'wsu': WSU_NS})

    return envelope, messaging, body
    
def generate_as4_messaging_part(messaging, document, doc_id):
    user_message = etree.SubElement(messaging, ns(NS2, 'UserMessage'))

    now = datetime.now().astimezone().isoformat()
    message_info = etree.SubElement(user_message, ns(NS2, 'MessageInfo'))
    etree.SubElement(message_info, ns(NS2, 'Timestamp')).text='{}'.format(now)
    etree.SubElement(message_info, ns(NS2, 'MessageId')).text='{}@beta.iola.dk'.format(uuid4())

    party_info = etree.SubElement(user_message, ns(NS2, 'PartyInfo'))

    from_info = etree.SubElement(party_info, ns(NS2, 'From'))
    # FIXME: from doc
    etree.SubElement(from_info, ns(NS2, 'PartyId'),
                     { "type": "urn:fdc:peppol.eu:2017:identifiers:ap" }).text='PDK000592'
    etree.SubElement(from_info, ns(NS2, 'Role')).text = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator'
    
    to_info = etree.SubElement(party_info, ns(NS2, 'To'))
    # FIXME: from service description
    etree.SubElement(to_info, ns(NS2, 'PartyId'),
                     { "type": "urn:fdc:peppol.eu:2017:identifiers:ap" }).text='PGD000005'
    etree.SubElement(to_info, ns(NS2, 'Role')).text = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder'

    collab_info = etree.SubElement(user_message, ns(NS2, 'CollaborationInfo'))
    etree.SubElement(collab_info, ns(NS2, 'AgreementRef')).text = 'urn:fdc:peppol.eu:2017:agreements:tia:ap_provider'
    etree.SubElement(collab_info, ns(NS2, 'Service'),
                     { "type": "cenbii-procid-ubl" }).text = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
    etree.SubElement(collab_info, ns(NS2, 'Action')).text = 'busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1'
    etree.SubElement(collab_info, ns(NS2, 'ConversationId')).text = '{}@beta.iola.dk'.format(uuid4())

    message_props = etree.SubElement(user_message, ns(NS2, 'MessageProperties'))
    etree.SubElement(message_props, ns(NS2, 'Property'),
                     { "name": "originalSender", "type": "iso6523-actorid-upis" }).text = '0096:pdk000592' # FIXME: from doc
    etree.SubElement(message_props, ns(NS2, 'Property'),
                     { "name": "finalRecipient", "type": "iso6523-actorid-upis" }).text = '9922:ngtbcntrlp1001' # FIXME: from doc

    payload_info = etree.SubElement(user_message, ns(NS2, 'PayloadInfo'))
    part_info = etree.SubElement(payload_info, ns(NS2, 'PartInfo'),
                                 { "href": doc_id })
    part_props = etree.SubElement(part_info, ns(NS2, 'PartProperties'))
    etree.SubElement(part_props, ns(NS2, 'Property'),
                     { "name": "CompressionType" }).text = 'application/gzip'
    etree.SubElement(part_props, ns(NS2, 'Property'),
                     { "name": "MimeType" }).text = 'application/xml'
    
doc_id = 'cid:{}@beta.iola.dk'.format(uuid4())

public_key = """MIIFwjCCA6qgAwIBAgIQYwzaxgiKwLWaZ5jvucGIOzANBgkqhkiG9w0BAQsFADBr
MQswCQYDVQQGEwJCRTEZMBcGA1UEChMQT3BlblBFUFBPTCBBSVNCTDEWMBQGA1UE
CxMNRk9SIFRFU1QgT05MWTEpMCcGA1UEAxMgUEVQUE9MIEFDQ0VTUyBQT0lOVCBU
RVNUIENBIC0gRzIwHhcNMjMwMzE2MDAwMDAwWhcNMjUwMzA1MjM1OTU5WjBPMQsw
CQYDVQQGEwJCRTETMBEGA1UECgwKT3BlblBlcHBvbDEXMBUGA1UECwwOUEVQUE9M
IFRFU1QgQVAxEjAQBgNVBAMMCVBHRDAwMDAwNTCCASIwDQYJKoZIhvcNAQEBBQAD
ggEPADCCAQoCggEBALV+4GxZZnlSXJfYBZWhUr+f+v/8hn6xmmNP5nTeAMDgRWPg
X1I1WY8n4cljvtzcpsSfF7X4XjQEqyIhZReQIBTzIkfHOijsKt8aowaf1e9QFSNV
/vl/LxOj7maDgTPVuNuVKDz/bG1+G7WqFxEVr0/YJrdYA0WEQauwebMpkE0t7/14
zSlqgj1CH80/85/gLyeKFYjCIzu48dUP6XBF1dTNJo6ryPobqbnCe1UyK6me/b5S
8M95yF+epinLc5CnuL9v5eyE5gF1v6d/sErDgR5UxNW9Wl+wNTFpPyIllu0Y1xe9
1KuIbg2G/VMZ8wT9kzgxBuo7oxMvZ7WLqp46WOUCAwEAAaOCAXwwggF4MAwGA1Ud
EwEB/wQCMAAwDgYDVR0PAQH/BAQDAgOoMBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMC
MB0GA1UdDgQWBBTtXt6B9vIgowdkMr2sfEG7Wcj0vjBdBgNVHR8EVjBUMFKgUKBO
hkxodHRwOi8vcGtpLWNybC5zeW1hdXRoLmNvbS9jYV82YTkzNzczNGEzOTNhMDgw
NWJmMzNjZGE4YjMzMTA5My9MYXRlc3RDUkwuY3JsMDcGCCsGAQUFBwEBBCswKTAn
BggrBgEFBQcwAYYbaHR0cDovL3BraS1vY3NwLnN5bWF1dGguY29tMB8GA1UdIwQY
MBaAFGtvS7bxN7orPH8Yzborsrl8KjfrMC0GCmCGSAGG+EUBEAMEHzAdBhNghkgB
hvhFARABAgMBAYGpkOEDFgY5NTc2MDgwOQYKYIZIAYb4RQEQBQQrMCkCAQAWJGFI
UjBjSE02THk5d2Eya3RjbUV1YzNsdFlYVjBhQzVqYjIwPTANBgkqhkiG9w0BAQsF
AAOCAgEAnsARRoJXUKqtYrrPNW6SnnP1Ta2AgR7qOBnIaLtGnO0+VOAwUKc+zSVs
MF6psSoGUX97KX4RvcK2liBjpfTgS+9XyEn8YTlhEScHUp3rcbwiAxFspm+MqkIv
fJXKt1TqxC+zJ4pyOXiDGnrgaBYdhNrtoeH1K6VSJr06cqsD29UftY+0+fsvvdWe
z7YCZ05kyH88iqTeolVnYQ/PNFbQN2eo+DfUgsP/CJl3MAKrbs8xZ2/AeZBUDDg0
XrOvaQ8ONEw9Y6jtdAA2/asEAij0R6G++QcuZAhgRkSr8kT1cySxHxvXuxontypH
RXq63siGG8txfeVPwJhrhceg5TDz8zdl90yGGhy4LQ98lHDjaEBYq5XwSNNVnS2O
jOJv6fTzuF+cv+PMVu8yzq0CQWhkqS6MRySsUrLmu9hkUP1nNNXt+6kr6qr6d2bk
fXzOO9ugRjcorQO/hOohGerUvbfE1GNuB/Rvw3eKL2/HDekBZNFcx5yOZJPOJ4Rj
qf1UI4Hxos2GvydGPlFDNN8DSDTT0PEkmEwwqx5ToH4QWcx9fyL2hjEVZh91WPvn
pu3mJi7YYT7Vk57zY/jtL4O/43tvHuIqxcOIxxT2qzlLg0yuUfrr4fUSkZ2l6D/k
uUNsPkkrJO3fGQjkelYqOxxF8SiNq97BqcCKRPt/OT6lvf5xlUs="""

cipher_value = "mNhf9oa3SgHMqJ8qeSlnUrT4bSpbxIoe/3+beG25QLBip0aPtZxnioh4/hIEFtg7ebIdcuO4rSIZxaBWGQvaezcZAb7JrCCr7uIApBDjT3EzGu4f4fDXoBuikH+Y8zyK5nueTSbLR1mTZeHGbwOz7DGZNyrJ6f+d+Ex0sQ1RD4SBnJfpzAYD4x4pGfyetidMWwMfS77yhvDPn7BxKr0N4GztZAi8alE4ipesHYSBTZNS359o4EyXflBx8WRS4ZfWfX+fit2/0sK9rvQLcEj6frwXKO9vwhcgBJv40D4EsT0bou5p5wE761wg6AziMhJa1wItPa1BC/tGSsvrWpov9A=="

# generated using external xmlsec (1.3)
encryption_element = """<wsse:BinarySecurityToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary" ValueType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3" wsu:Id="G47abf010-3789-4722-bdba-fbb82ec92fff">{}</wsse:BinarySecurityToken>

<xenc:EncryptedKey xmlns:xenc="http://www.w3.org/2001/04/xmlenc#" Id="EK-82aea516-fe2f-44d6-b7a8-3d66d1ff2da2">
 <xenc:EncryptionMethod Algorithm="http://www.w3.org/2009/xmlenc11#rsa-oaep">
  <ds:DigestMethod xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
  <xenc11:MGF xmlns:xenc11="http://www.w3.org/2009/xmlenc11#" Algorithm="http://www.w3.org/2009/xmlenc11#mgf1sha256"/>
 </xenc:EncryptionMethod>

 <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
  <wsse:SecurityTokenReference>
   <wsse:Reference URI="#G47abf010-3789-4722-bdba-fbb82ec92fff" ValueType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3"/>
  </wsse:SecurityTokenReference>
 </ds:KeyInfo>

 <xenc:CipherData>
  <xenc:CipherValue>{}</xenc:CipherValue>
 </xenc:CipherData>

 <xenc:ReferenceList>
  <xenc:DataReference URI="#ED-368427a8-7b98-473f-b2c9-60421d9b38e1"/>
 </xenc:ReferenceList>
</xenc:EncryptedKey>

<xenc:EncryptedData xmlns:xenc="http://www.w3.org/2001/04/xmlenc#" Id="ED-368427a8-7b98-473f-b2c9-60421d9b38e1" MimeType="application/octet-stream" Type="http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Content-Only">

 <xenc:EncryptionMethod Algorithm="http://www.w3.org/2009/xmlenc11#aes128-gcm"/>

 <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
  <wsse:SecurityTokenReference xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsse11="http://docs.oasis-open.org/wss/oasis-wss-wssecurity-secext-1.1.xsd" wsse11:TokenType="http://docs.oasis-open.org/wss/oasis-wss-soap-message-security-1.1#EncryptedKey">
   <wsse:Reference URI="#EK-82aea516-fe2f-44d6-b7a8-3d66d1ff2da2"/>
  </wsse:SecurityTokenReference>
 </ds:KeyInfo>

 <xenc:CipherData>
  <xenc:CipherReference URI="{}">
   <xenc:Transforms>
    <ds:Transform xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Algorithm="http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Ciphertext-Transform"/>
   </xenc:Transforms>
  </xenc:CipherReference>
 </xenc:CipherData>
</xenc:EncryptedData>""".format(public_key, cipher_value, doc_id)

encrypted_gzip_b64 = """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"""

import base64
encrypted_gzip = base64.b64decode(encrypted_gzip_b64.encode('ascii'))
encrypted_gzip_hash = base64.b64encode(hashlib.sha256(encrypted_gzip).digest()).decode('ascii')

def generate_as4_message_to_post(filename):
    file_contents = ''
    with open(filename, 'r') as f:
        file_contents = f.read().encode('utf-8')

    envelope, messaging, body = generate_as4_envelope(file_contents, doc_id)
    #print(etree.tostring(envelope, pretty_print=True).decode('utf-8'))

    keyfile = "test.key.pem"
    certfile = "cert.pem"
    #their_certfile = "cert.pem" # "server-cert.pem"

    # FIXME: do this differently
    with open('test.xml.gz', 'rb') as f:
        file_contents = f.read()
        from base64 import b64encode
        document_hash = b64encode(hashlib.sha256(file_contents).digest()).decode('ascii')

    password = ''

    sign(envelope, doc_id, document_hash, body, messaging, keyfile, certfile, password)

    doc = etree.tostring(envelope, pretty_print=True).decode('utf-8')

    # add encryption element from external xmlsec
    doc = doc.replace('<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" env:mustUnderstand="true">', '<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" env:mustUnderstand="true">' + encryption_element)

    #print(doc)
    return [doc, encrypted_gzip]

def enable_logging():
    http_client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def post_multipart(url, filename):
    enable_logging()

    document, gzip = generate_as4_message_to_post(filename)

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
url = 'https://oxalis.beta.iola.dk/as4'
url = 'https://phase4-controller.testbed.peppol.org/as4'
post_multipart(url, 'nyt-test-data/PEPPOL_TestCase_0232_20231207T1245Z/TestFile_001__BISv3_Invoice.xml')
