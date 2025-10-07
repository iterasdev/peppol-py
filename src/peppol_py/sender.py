import datetime
from pathlib import Path

from lxml import etree
from lxml.builder import ElementMaker

from .smp import get_service_info_for_participant_from_smp
from .exception import make_sendpeppol_error
from .as4_sender import get_headers_and_body_for_posting_as4_document
from .as4_sender import post_edelivery_as4_document

def split_tag(element):
    ns, tag = element.tag.lstrip('{').split('}')
    return ns, tag

def get_document_type_from_ubl(ubl, document_type_version=None):
    root_ns, root_tag = split_tag(ubl)

    if document_type_version is None:
        document_type_version = ubl.findtext('./{*}CustomizationID').rsplit(':', 1)[1]

    return root_ns + '::' + root_tag + '##' + ubl.findtext('./{*}CustomizationID') + '::' + document_type_version

def wrap_ubl_in_peppol_standard_business_document_header(ubl, utc_timestamp, document_type, process_type, sender_id, sender_country, receiver_id):
    E = ElementMaker(nsmap={})

    unique_id = utc_timestamp.replace(':', '')

    id_element = ubl.find('./{*}ID')
    if id_element is not None:
        unique_id = id_element.text + '-' + unique_id

    root_ns, root_tag = split_tag(ubl)

    document_type_version = document_type.rsplit(':', 1)[1]

    header = E("StandardBusinessDocumentHeader",
          E("HeaderVersion", "1.0"),
          E("Sender",
            E("Identifier", sender_id, Authority="iso6523-actorid-upis")),
          E("Receiver",
            E("Identifier", receiver_id, Authority="iso6523-actorid-upis")),
          E("DocumentIdentification",
            E("Standard", root_ns),
            E("TypeVersion", document_type_version),
            E("InstanceIdentifier", unique_id),
            E("Type", root_tag),
            E("CreationDateAndTime", utc_timestamp)
            ),
          E("BusinessScope",
            E("Scope",
              E("Type", "DOCUMENTID"),
              E("InstanceIdentifier", document_type),
              E("Identifier", "busdox-docid-qns")
              ),
            E("Scope",
              E("Type", "PROCESSID"),
              E("InstanceIdentifier", process_type),
              E("Identifier", "cenbii-procid-ubl")
              ),
            E("Scope",
              E("Type", "COUNTRY_C1"),
              E("InstanceIdentifier", sender_country),
              ),
            )
          )

    business_doc = E("StandardBusinessDocument", header, ubl, xmlns="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader")

    return etree.tostring(business_doc), business_doc

def get_common_name_from_certificate(cert):
    import asn1crypto.pem
    import asn1crypto.x509

    cert_type_name, cert_headers, cert_der_bytes = asn1crypto.pem.unarmor(cert)
    assert cert_type_name == 'CERTIFICATE'
    parsed_cert = asn1crypto.x509.Certificate.load(cert_der_bytes)

    return parsed_cert.subject.native['common_name']

def validate_certificate(cert, test):
    import asn1crypto.pem
    from certvalidator import ValidationContext, CertificateValidator

    certfolder = Path(__file__).parent / "data" / "certs"
    if datetime.datetime.now(datetime.UTC) > datetime.datetime(2026, 4, 1, 0, 0, 0, tzinfo=datetime.UTC):
        # See G2→G3 migration plan: https://openpeppol.atlassian.net/wiki/spaces/RR/pages/4387602465/2025.06.17+PKI+Migration+Plan
        cabundle = certfolder / ('ap-test-truststore-g3.pem' if test else 'ap-prod-truststore-g3.pem')
    else:
        cabundle = certfolder / ('ap-test-truststore-g2-g3.pem' if test else 'ap-prod-truststore-g2-g3.pem')
    trust_roots = []
    with open(cabundle, 'rb') as f:
        for _, _, der_bytes in asn1crypto.pem.unarmor(f.read(), multiple=True):
            trust_roots.append(der_bytes)

    context = ValidationContext(
        allow_fetching=True,
        trust_roots=trust_roots,
        revocation_mode="hard-fail",
    )
    validator = CertificateValidator(cert, validation_context=context)
    validator.validate_usage(
        key_usage={"key_encipherment", "key_agreement", "digital_signature"},
        extended_key_usage={"client_auth"},
        extended_optional=False,
    )


def send_peppol_document(
    document_content: bytes,
    xmlsec_path: str,
    keyfile: str,
    keyfile_password: str,
    certfile: str,
    sender_id: str=None,
    receiver_id: str=None,
    sender_country: str=None,
    document_type_version: str=None,
    test_environment: bool=True,
    timeout: int=20,
    dryrun: bool=False,
) -> dict:
    """
    Send a peppol document. Returned is a dictionary of information you need to record to later send reports to Peppol.

    ``document_content`` (bytes): document to send. Note the standard business header will automatically be added.

    ``xmlsec_path`` (str): specifies the path to a xmlsec 1.3 or higher binary.

    ``keyfile`` (str): the path to the private key of the sender.

    ``password`` (str): the password for the private key of the sender.

    ``certfile`` (str): the path to the public key of the sender.

    ``service_provider_id`` (bool): identifier of the sending service provider.

    ``sender_id`` (str): optional sender id, will be extracted from document if not specified.

    ``receiver_id`` (str): optional receiver id, will be extracted from document if not specified.

    ``sender_country`` (str): optional sender country, will be extracted from document if not specified.

    ``document_type_version`` (str): the document type version, if not specified will be last part of CustomizationID.
                                     For invoices should be set to `2.1`.

    ``test_environment`` (bool): use test SML servers?

    ``timeout`` (int): number of seconds to wait for response from the remote end.

    ``dryrun`` (bool): if specified, will prepare, get the endpoint, test document for validation errors but not send to remote endpoint.
                       Return value will be a tuple of ``body, header, stats``.
    """
    document_xml = etree.fromstring(document_content)
    #print(etree.tostring(document_xml, pretty_print=True).decode())

    if sender_id is None:
        element = document_xml.find("./{*}AccountingSupplierParty/{*}Party/{*}EndpointID")
        sender_id = element.attrib.get('schemeID', '') + ':' + element.text
    if receiver_id is None:
        element = document_xml.find("./{*}AccountingCustomerParty/{*}Party/{*}EndpointID")
        receiver_id = element.attrib.get('schemeID', '') + ':' + element.text
    if sender_country is None:
        sender_country = document_xml.findtext('./{*}AccountingSupplierParty/{*}Party/{*}PostalAddress/{*}Country/{*}IdentificationCode')

    sender_end_user = None
    element = document_xml.find('./{*}AccountingSupplierParty/{*}Party/{*}PartyIdentification/{*}ID')
    if element is not None:
        sender_end_user = element.attrib.get('schemeID', '') + ':' + element.text

    document_type = get_document_type_from_ubl(document_xml, document_type_version=document_type_version)
    process_type = document_xml.findtext('./{*}ProfileID')

    utc_timestamp = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0).isoformat()

    document_content, document_xml = wrap_ubl_in_peppol_standard_business_document_header(document_xml, utc_timestamp, document_type, process_type, sender_id, sender_country, receiver_id)

    transport_profile, endpoint_url, receiver_cert = get_service_info_for_participant_from_smp(receiver_id, document_type, test_environment=test_environment, timeout=timeout)

    if not endpoint_url:
        raise make_sendpeppol_error("Endpoint URL not found", 'not-found-in-smp')

    if not receiver_cert:
        raise make_sendpeppol_error("Receiver certificate not found", 'not-found-in-smp')

    with open(certfile, 'rb') as sender_certfile_f:
        sender_cert = sender_certfile_f.read()
    service_provider_id = get_common_name_from_certificate(sender_cert)

    validate_certificate(receiver_cert, test_environment)
    to_party_id = get_common_name_from_certificate(receiver_cert)

    stats = {
        'timestamp': utc_timestamp,
        'receiver_common_name': to_party_id,
        'document_type': document_type,
        'process_type': process_type,
        'transport_profile': transport_profile,
        'sender_end_user': sender_end_user,
        'sender_country': sender_country,
    }

    body, headers = get_headers_and_body_for_posting_as4_document(document_content, document_xml, utc_timestamp, document_type, process_type, sender_id, receiver_id, to_party_id, xmlsec_path, keyfile, keyfile_password, sender_cert, receiver_cert, service_provider_id)

    if dryrun:
        return body, headers, stats

    post_edelivery_as4_document(endpoint_url, body, headers, timeout=timeout)

    return stats
