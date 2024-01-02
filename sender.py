from sml import get_domain_using_http
from smp import get_smp_info, extract_as4_information
from as4_sender import post_multipart

# params
xmlsec_path = "~/Downloads/xmlsec1-1.3.2/install/bin/xmlsec1"
keyfile = "test.key.pem"
certfile = "cert.pem"
password = ""

def send_peppel_document(filename, their_id):
    smp_domain = get_domain_using_http(their_id)
    smp_contents = get_smp_info(smp_domain, their_id)
    url, their_cert = extract_as4_information(smp_contents)

    their_certfile = '/tmp/their-cert.pem'
    with open(their_certfile, 'w') as f:
        f.write('-----BEGIN CERTIFICATE-----\n' + their_cert + '\n-----END CERTIFICATE-----')

    post_multipart(url, xmlsec_path, filename, keyfile, password, certfile, their_certfile)

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Send peppol files")
    parser.add_argument('--receiver', default='', help="The receivers id")
    parser.add_argument('--document', default='', help="The path of the document to send")

    parsed_args = parser.parse_args()

    if not parsed_args.receiver and not parsed_args.document:
        sys.stderr.write("Missing --receiver or --document\n")
        sys.exit(1)

    send_peppel_document(parsed_args.document, parsed_args.receiver)
