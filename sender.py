from sml import get_domain_using_http
from smp import get_smp_info, extract_as4_information
from as4_sender import post_multipart, enable_logging

def send_peppel_document(filename, their_id, xmlsec_path, keyfile, password, certfile, logging, test):
    smp_domain = get_domain_using_http(their_id, test)
    smp_contents = get_smp_info(smp_domain, their_id)
    url, their_cert = extract_as4_information(smp_contents)

    their_certfile = '/tmp/their-cert.pem'
    with open(their_certfile, 'w') as f:
        f.write('-----BEGIN CERTIFICATE-----\n' + their_cert + '\n-----END CERTIFICATE-----')

    return post_multipart(url, xmlsec_path, filename, keyfile, password, certfile,
                          their_certfile, logging)

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Send peppol files")
    parser.add_argument('--receiver', default='', help="The receivers id")
    parser.add_argument('--document', default='', help="The path of the document to send")

    parser.add_argument('--xmlsec-path', default='~/Downloads/xmlsec1-1.3.2/install/bin/xmlsec1',
                        help="The path to latest xmlsec binary")
    parser.add_argument('--keyfile', default='test.key.pem',
                        help="The path to the private key")
    parser.add_argument('--password', default='',
                        help="The password for the private key")
    parser.add_argument('--certfile', default='cert.pem',
                        help="The path to the public key")
    parser.add_argument('--logging', action=argparse.BooleanOptionalAction,
                        help="Enable debug logging")
    parser.add_argument('--test', action=argparse.BooleanOptionalAction,
                        help="Use test SML server")

    parsed_args = parser.parse_args()

    if not parsed_args.receiver and not parsed_args.document:
        sys.stderr.write("Missing --receiver or --document\n")
        sys.exit(1)

    if parsed_args.logging:
        enable_logging()

    send_peppel_document(parsed_args.document, parsed_args.receiver,
                         parsed_args.xmlsec_path, parsed_args.keyfile,
                         parsed_args.password, parsed_args.certfile,
                         parsed_args.logging, parsed_args.test)
