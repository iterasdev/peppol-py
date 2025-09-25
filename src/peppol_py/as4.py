import uuid
import socket

from .xmlhelpers import get_element_maker
from .constants import ENV_NS, WSSE_NS, WSU_NS

NS2_NS = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/'
STBH_NS = 'http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader'

NAMESPACES = {
    'env': ENV_NS,
    'ns2': NS2_NS,
    'wsu': WSU_NS,
    'wsse': WSSE_NS,
    'stbh': STBH_NS
}

def generate_as4_envelope(utc_timestamp, document_type, process_type, sender_id, receiver_id, to_party_id, service_provider_id):
    E, ns = get_element_maker(NAMESPACES)

    hostname = socket.getfqdn()

    attachment_id = 'cid:{}@{}'.format(uuid.uuid4(), hostname)
    message_id = '{}@{}'.format(uuid.uuid4(), hostname)

    user_message = E(ns('ns2', 'UserMessage'),
                    E(ns('ns2', 'MessageInfo'),
                      E(ns('ns2', 'Timestamp'), utc_timestamp),
                      E(ns('ns2', 'MessageId'), message_id)),
                    E(ns('ns2', 'PartyInfo'),
                      E(ns('ns2', 'From'),
                        E(ns('ns2', 'PartyId'), service_provider_id, type='urn:fdc:peppol.eu:2017:identifiers:ap'),
                        E(ns('ns2', 'Role'), 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator')),
                      E(ns('ns2', 'To'),
                        E(ns('ns2', 'PartyId'), to_party_id, type='urn:fdc:peppol.eu:2017:identifiers:ap'),
                        E(ns('ns2', 'Role'), 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder'))),
                    E(ns('ns2', 'CollaborationInfo'),
                      E(ns('ns2', 'AgreementRef'), 'urn:fdc:peppol.eu:2017:agreements:tia:ap_provider'),
                      E(ns('ns2', 'Service'), process_type, type='cenbii-procid-ubl'),
                      E(ns('ns2', 'Action'), 'busdox-docid-qns::{}'.format(document_type)),
                      E(ns('ns2', 'ConversationId'), message_id)),
                    E(ns('ns2', 'MessageProperties'),
                      E(ns('ns2', 'Property'), sender_id, name='originalSender', type='iso6523-actorid-upis'),
                      E(ns('ns2', 'Property'), receiver_id, name='finalRecipient', type='iso6523-actorid-upis')),
                    E(ns('ns2', 'PayloadInfo'),
                      E(ns('ns2', 'PartInfo'),
                        E(ns('ns2', 'PartProperties'),
                          E(ns('ns2', 'Property'), 'application/gzip', name='CompressionType'),
                          E(ns('ns2', 'Property'), 'application/xml', name='MimeType')), href=attachment_id)))

    messaging = E(ns('ns2', 'Messaging'), user_message, {ns('env', 'mustUnderstand'): 'true', ns('wsu', 'Id'): 'messaging'})

    body = E(ns('env', 'Body'), {ns('wsu', 'Id'): 'body'})

    envelope = E(ns('env', 'Envelope'),
                 E(ns('env', 'Header'),
                   messaging,
                   E(ns('wsse', 'Security'), { ns('env', 'mustUnderstand'): 'true' })),
                 body)

    return attachment_id, envelope, messaging, body
