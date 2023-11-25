import hashlib
from base64 import b64encode
import io
import zlib
import dns.resolver
import urllib.request
import urllib.parse
from lxml import etree
from uuid import uuid4

from wsse import encrypt, sign
from xmlhelpers import get_unique_id

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

# FIXME: make more general and move to helpers
def add_missing_env_namespace(element, payload):
    return payload.replace("<" + element, "<" + element + " " + 'xmlns:env="http://www.w3.org/2003/05/soap-envelope"')
    
# the payload must / will be:
# - have all namespaces so that it is valid xml (even if this is not what is submitted over the network)
# - be transformed to a "cannonical" c14n (NOT c14n2!) representation using the exclude option
def generate_hash(payload):
    xmldoc = etree.fromstring(payload)
    et = etree.ElementTree(xmldoc)
    out = io.BytesIO()
    et.write(out, method="c14n", exclusive=True)
    return b64encode(hashlib.sha256(out.getvalue()).digest()).decode('utf-8')

# the document will be:
# - be transformed to a "cannonical" c14n (NOT c14n2!) representation using the exclude option
# - be gzipped (even if different implementations zips differently, the level is not even specified)
def generate_gzipped_document(document):
    xmldoc = etree.fromstring(document)
    et = etree.ElementTree(xmldoc)
    out = io.BytesIO()
    et.write(out, method="c14n", exclusive=True)
    return zlib.compress(out.getvalue())

def generate_document_hash(gzip_document):
    return b64encode(hashlib.sha256(gzip_document).digest()).decode('utf-8')

def generate_as4_message_to_post(filename):
    # FIXME: generate this based on xml doc (filename)
    messaging_id = '_009c69da-cafc-43cd-92bc-d11bfb02467b'
    messaging = '<ns2:Messaging xmlns:ns2="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/" xmlns:ns3="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" env:mustUnderstand="true" wsu:Id="_009c69da-cafc-43cd-92bc-d11bfb02467b"><ns2:UserMessage><ns2:MessageInfo><ns2:Timestamp>2023-11-17T11:52:08.464+01:00</ns2:Timestamp><ns2:MessageId>216e0a25-e672-44a1-902e-2edf2225a564@beta.iola.dk</ns2:MessageId></ns2:MessageInfo><ns2:PartyInfo><ns2:From><ns2:PartyId type="urn:fdc:peppol.eu:2017:identifiers:ap">PDK000592</ns2:PartyId><ns2:Role>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator</ns2:Role></ns2:From><ns2:To><ns2:PartyId type="urn:fdc:peppol.eu:2017:identifiers:ap">PGD000005</ns2:PartyId><ns2:Role>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder</ns2:Role></ns2:To></ns2:PartyInfo><ns2:CollaborationInfo><ns2:AgreementRef>urn:fdc:peppol.eu:2017:agreements:tia:ap_provider</ns2:AgreementRef><ns2:Service type="cenbii-procid-ubl">urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</ns2:Service><ns2:Action>busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1</ns2:Action><ns2:ConversationId>f820302d-0329-4d52-a53c-f63275a3bd2f@beta.iola.dk</ns2:ConversationId></ns2:CollaborationInfo><ns2:MessageProperties><ns2:Property name="originalSender" type="iso6523-actorid-upis">0096:pdk000592</ns2:Property><ns2:Property name="finalRecipient" type="iso6523-actorid-upis">9922:ngtbcntrlp1001</ns2:Property></ns2:MessageProperties><ns2:PayloadInfo><ns2:PartInfo href="cid:cd5d3394-0468-4c88-9af1-4de02d5121a0@beta.iola.dk"><ns2:PartProperties><ns2:Property name="CompressionType">application/gzip</ns2:Property><ns2:Property name="MimeType">application/xml</ns2:Property></ns2:PartProperties></ns2:PartInfo></ns2:PayloadInfo></ns2:UserMessage></ns2:Messaging>'

    messaging_hash = generate_hash(add_missing_env_namespace('ns2:Messaging', messaging))
    #print(messaging_hash)

    body_id = get_unique_id()
    body = '<env:Body xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="%s"></env:Body>' % (body_id,)

    body_hash = generate_hash(add_missing_env_namespace('env:Body', body))
    #print(body_hash)
    
    wss_section = '<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" env:mustUnderstand="true"></wsse:Security>'
    
    envelope = '<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope"><env:Header>' + messaging + wss_section + '</env:Header>' + body + '</env:Envelope>'
    
    xml_envelope = etree.fromstring(envelope)

    keyfile = "test.key.pem"
    certfile = "cert.pem"

    doc_id = 'cid:{}@beta.iola.dk'.format(uuid4())
    document_hash = ''
    document_data = None
    with open('TestFile_003__BISv3_Invoice.xml', 'r') as f:
        document_data = generate_gzipped_document(f.read().encode('utf-8'))
        document_hash = generate_document_hash(document_data)

    #print(document_hash)

    password = ''
    
    sign(xml_envelope, doc_id, document_hash, body_id, body_hash, messaging_id, messaging_hash, keyfile, certfile, password)
    encrypt(xml_envelope, doc_id, document_data, certfile)

    print(etree.tostring(xml_envelope, pretty_print=True).decode('utf-8'))
    
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

generate_as4_message_to_post('example-file.txt')
