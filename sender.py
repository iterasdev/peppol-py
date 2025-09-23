import argparse
import datetime
from lxml import etree
from lxml.builder import ElementMaker

from smp import get_service_info_for_participant_from_smp
from validation import validate_peppol_document
from exception import make_sendpeppol_error, SendPeppolError
from as4_sender import get_headers_and_body_for_posting_as4_document
from as4_sender import post_edelivery_as4_document

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

    cabundle = 'certs/ap-test-truststore.pem' if test else 'certs/ap-prod-truststore.pem'
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


def send_peppol_document(document_content, xmlsec_path, keyfile, keyfile_password, certfile, sender_id=None, receiver_id=None, sender_country=None, document_type_version=None, test_environment=True, timeout=20, dryrun=False, service_provider_id=None):
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

def enable_debug_logging():
    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1

    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def main():
    parser = argparse.ArgumentParser(description="Send peppol files")
    parser.add_argument('--document', help="The path of the document to send", required=True)
    parser.add_argument('--xmlsec-path', default='xmlsec1', help="The path to latest xmlsec binary")
    parser.add_argument('--schematron-path', nargs='+', help="Schematron XSL files to validate with")
    parser.add_argument('--keyfile', default='test.key.pem', help="The path to the private key")
    parser.add_argument('--password', default='', help="The password for the private key")
    parser.add_argument('--certfile', default='cert.pem', help="The path to the public key")
    parser.add_argument('--unwrap-sbh', action=argparse.BooleanOptionalAction, help="Unwrap standard business header already present in document. Useful for testbed.")
    parser.add_argument('--service-provider', help="Service provider ID", required=True)
    parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, help="Enable debug logging")
    parser.add_argument('--test', action=argparse.BooleanOptionalAction, help="Use test SMP server")

    parsed_args = parser.parse_args()

    if parsed_args.verbose:
        enable_debug_logging()

    with open(parsed_args.document, 'rb') as f:
        document_content = f.read()

    errors = validate_peppol_document(document_content, parsed_args.schematron_path)
    if errors:
        for d in errors:
            print(d)
        return

    if parsed_args.unwrap_sbh:
        document_content = etree.tostring(etree.fromstring(document_content).find('./{*}Invoice'))

    try:
        stats = send_peppol_document(document_content,
                                     parsed_args.xmlsec_path, parsed_args.keyfile,
                                     keyfile_password=parsed_args.password, certfile=parsed_args.certfile,
                                     test_environment=parsed_args.test, document_type_version='2.1',
                                     service_provider_id=parsed_args.service_provider)
        print(stats)
    except SendPeppolError as ex:
        raise
        print(f"Failed with: {ex.code} {ex}")
    except Exception as ex:
        print(f"Failed with: {ex}")

if __name__ == "__main__":
    main()
