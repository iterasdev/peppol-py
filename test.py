import hashlib
import dns.resolver
import urllib.request
import urllib.parse
from lxml import etree
from uuid import uuid4
from datetime import datetime

from wsse import encrypt, sign
from xmlhelpers import ns
from constants import NS2, ENV_NS, WSSE_NS, WSU_NS
from hashing import generate_document_hash

import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import email

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

def generate_as4_message_to_post(filename):
    file_contents = ''
    with open(filename, 'r') as f:
        file_contents = f.read().encode('utf-8')

    envelope, messaging, body = generate_as4_envelope(file_contents, doc_id)
    #print(etree.tostring(envelope, pretty_print=True).decode('utf-8'))

    keyfile = "test.key.pem"
    certfile = "cert.pem"
    their_certfile = "server-cert.pem"

    gzip_document, document_hash = generate_document_hash(file_contents)
    #print(document_hash)

    password = ''

    sign(envelope, doc_id, document_hash, body, messaging, keyfile, certfile, password)
    encrypt(envelope, doc_id, gzip_document, their_certfile)

    doc = etree.tostring(envelope, pretty_print=True).decode('utf-8')
    #print(doc)
    return [doc, gzip_document]

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

    mt = MIMEApplication(gzip, _encoder=email.encoders.encode_noop)
    mt.add_header("Content-Transfer-Encoding", "Binary")
    mt.add_header("Content-ID", doc_id)
    related.attach(mt)

    # java needs CRLF
    body = related.__bytes__().replace(b'\n', b'\r\n')
    headers = dict(related.items())
    #headers['Content-Type'] = headers['Content-Type'] + '; type="application/soap+xml"; start="<root.message@cxf.apache.org>"; start-info="application/soap+xml"'

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
post_multipart('https://phase4-controller.testbed.peppol.org/as4', 'nyt-test-data/PEPPOL_TestCase_0232_20231207T1245Z/TestFile_001__BISv3_Invoice.xml')
