from uuid import uuid4
from datetime import datetime
from lxml import etree

from xmlhelpers import get_element_maker
from constants import NS2, ENV_NS, WSSE_NS, WSU_NS, STBH

NAMESPACES = {
    'env': ENV_NS,
    'ns2': NS2,
    'wsu': WSU_NS,
    'wsse': WSSE_NS,
    'stbh': STBH
}

def document_id():
    return f'cid:{uuid4()}@beta.iola.dk'

def envelope_as_string(envelope):
    return etree.tostring(envelope, pretty_print=True).decode('utf-8')

def generate_as4_envelope(filename, doc_id):
    E, ns = get_element_maker(NAMESPACES)

    messaging = E(ns("ns2", "Messaging"), generate_as4_messaging_part(E, ns, filename, doc_id),
                  { ns("env", 'mustUnderstand'): "true", ns("wsu", "Id"): "messaging" })

    body = E(ns("env", "Body"), { ns("wsu", 'Id'): "body" })

    envelope = E(ns("env", 'Envelope'),
                 E(ns("env", "Header"),
                   messaging,
                   E(ns("wsse", "Security"), { ns("env", "mustUnderstand"): "true" })),
                 body)

    return envelope, messaging, body

def generate_as4_messaging_part(E, ns, filename, doc_id):
    document = etree.parse(filename)
    header = document.find(ns("stbh", 'StandardBusinessDocumentHeader'))

    original_sender = header.find(ns("stbh", 'Sender')).find(ns("stbh", 'Identifier')).text
    final_recipient = header.find(ns("stbh", 'Receiver')).find(ns("stbh", 'Identifier')).text
    from_id = original_sender.split(':')[1]
    to_id = final_recipient.split(':')[1]

    return E(ns("ns2", "UserMessage"),
             E(ns("ns2", "MessageInfo"),
               E(ns("ns2", "Timestamp"), f'{datetime.now().astimezone().isoformat()}'),
               E(ns("ns2", "MessageId"), f'{uuid4()}@beta.iola.dk')),
             E(ns("ns2", "PartyInfo"),
               E(ns("ns2", "From"),
                 E(ns("ns2", "PartyId"), from_id, type="urn:fdc:peppol.eu:2017:identifiers:ap"),
                 E(ns("ns2", "Role"), "http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator")),
               E(ns("ns2", "To"),
                 E(ns("ns2", "PartyId"), to_id, type="urn:fdc:peppol.eu:2017:identifiers:ap"),
                 E(ns("ns2", "Role"), "http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder"))),
             E(ns("ns2", "CollaborationInfo"),
               E(ns("ns2", "AgreementRef"), "urn:fdc:peppol.eu:2017:agreements:tia:ap_provider"),
               E(ns("ns2", "Service"), "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0", type="cenbii-procid-ubl"),
               E(ns("ns2", "Action"), "busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1"),
               E(ns("ns2", "ConversationId"), f'{uuid4()}@beta.iola.dk')),
             E(ns("ns2", "MessageProperties"),
               E(ns("ns2", "Property"), original_sender, name="originalSender", type="iso6523-actorid-upis"),
               E(ns("ns2", "Property"), final_recipient, name="finalRecipient", type="iso6523-actorid-upis")),
             E(ns("ns2", "PayloadInfo"),
               E(ns("ns2", "PartInfo"),
                 E(ns("ns2", "PartProperties"),
                   E(ns("ns2", "Property"), 'application/gzip', name="CompressionType"),
                   E(ns("ns2", "Property"), 'application/xml', name="MimeType"))
                 , href=doc_id)))
