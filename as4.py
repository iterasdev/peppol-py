from uuid import uuid4
from datetime import datetime
from lxml import etree

from xmlhelpers import ns
from constants import NS2, ENV_NS, WSSE_NS, WSU_NS, STBH

def document_id():
    return 'cid:{}@beta.iola.dk'.format(uuid4())

def envelope_as_string(envelope):
    return etree.tostring(envelope, pretty_print=True).decode('utf-8')

def generate_as4_envelope(filename, doc_id):
    envelope = etree.Element(ns(ENV_NS, 'Envelope'), nsmap={'env': ENV_NS})
    header = etree.SubElement(envelope, ns(ENV_NS, 'Header'), nsmap={'env': ENV_NS})

    attribs = { etree.QName(ENV_NS, 'mustUnderstand'): "true", etree.QName(WSU_NS, "Id"): "_{}".format(uuid4()) }
    messaging = etree.SubElement(header, ns(NS2, 'Messaging'), attribs, nsmap={'ns2': NS2, 'wsu': WSU_NS})
    generate_as4_messaging_part(messaging, filename, doc_id)

    etree.SubElement(header, ns(WSSE_NS, 'Security'),
                     { etree.QName(ENV_NS, 'mustUnderstand'): "true" },
                     nsmap={'wsse': WSSE_NS})

    body = etree.SubElement(envelope, ns(ENV_NS, 'Body'),
                            { etree.QName(WSU_NS, 'Id'): "_{}".format(uuid4()) },
                            nsmap={'env': ENV_NS, 'wsu': WSU_NS})

    return envelope, messaging, body
    
def generate_as4_messaging_part(messaging, filename, doc_id):
    file_contents = ''
    with open(filename, 'r') as f:
        file_contents = f.read().encode('utf-8')

    document = etree.fromstring(file_contents)
    header = document.find(ns(STBH, 'StandardBusinessDocumentHeader'))

    original_sender = header.find(ns(STBH, 'Sender')).find(ns(STBH, 'Identifier')).text
    final_recipient = header.find(ns(STBH, 'Receiver')).find(ns(STBH, 'Identifier')).text
    from_id = original_sender.split(':')[1]
    to_id = final_recipient.split(':')[1]

    user_message = etree.SubElement(messaging, ns(NS2, 'UserMessage'))

    now = datetime.now().astimezone().isoformat()
    message_info = etree.SubElement(user_message, ns(NS2, 'MessageInfo'))
    etree.SubElement(message_info, ns(NS2, 'Timestamp')).text='{}'.format(now)
    etree.SubElement(message_info, ns(NS2, 'MessageId')).text='{}@beta.iola.dk'.format(uuid4())

    party_info = etree.SubElement(user_message, ns(NS2, 'PartyInfo'))

    from_info = etree.SubElement(party_info, ns(NS2, 'From'))
    etree.SubElement(from_info, ns(NS2, 'PartyId'),
                     { "type": "urn:fdc:peppol.eu:2017:identifiers:ap" }).text=from_id
    etree.SubElement(from_info, ns(NS2, 'Role')).text = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator'
    
    to_info = etree.SubElement(party_info, ns(NS2, 'To'))
    etree.SubElement(to_info, ns(NS2, 'PartyId'),
                     { "type": "urn:fdc:peppol.eu:2017:identifiers:ap" }).text=to_id
    etree.SubElement(to_info, ns(NS2, 'Role')).text = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder'

    collab_info = etree.SubElement(user_message, ns(NS2, 'CollaborationInfo'))
    etree.SubElement(collab_info, ns(NS2, 'AgreementRef')).text = 'urn:fdc:peppol.eu:2017:agreements:tia:ap_provider'
    etree.SubElement(collab_info, ns(NS2, 'Service'),
                     { "type": "cenbii-procid-ubl" }).text = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
    etree.SubElement(collab_info, ns(NS2, 'Action')).text = 'busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1'
    etree.SubElement(collab_info, ns(NS2, 'ConversationId')).text = '{}@beta.iola.dk'.format(uuid4())

    message_props = etree.SubElement(user_message, ns(NS2, 'MessageProperties'))
    etree.SubElement(message_props, ns(NS2, 'Property'),
                     { "name": "originalSender", "type": "iso6523-actorid-upis" }).text = original_sender
    etree.SubElement(message_props, ns(NS2, 'Property'),
                     { "name": "finalRecipient", "type": "iso6523-actorid-upis" }).text = final_recipient

    payload_info = etree.SubElement(user_message, ns(NS2, 'PayloadInfo'))
    part_info = etree.SubElement(payload_info, ns(NS2, 'PartInfo'),
                                 { "href": doc_id })
    part_props = etree.SubElement(part_info, ns(NS2, 'PartProperties'))
    etree.SubElement(part_props, ns(NS2, 'Property'),
                     { "name": "CompressionType" }).text = 'application/gzip'
    etree.SubElement(part_props, ns(NS2, 'Property'),
                     { "name": "MimeType" }).text = 'application/xml'
