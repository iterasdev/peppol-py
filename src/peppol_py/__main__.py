import argparse
import sys
from pathlib import Path

from lxml import etree

from . import validate_peppol_document, send_peppol_document, SendPeppolError


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
    parser = argparse.ArgumentParser(description="Peppol utility", prog="python -m peppol_py")
    parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, help="Enable debug logging")

    subparsers = parser.add_subparsers(help="command", dest="command")

    parser_send = subparsers.add_parser('send', help='Send a Peppol document')
    parser_send.add_argument('--document', help="The path of the document to send", required=True)
    parser_send.add_argument('--xmlsec-path', default='xmlsec1', help="The path to latest xmlsec binary")
    parser_send.add_argument('--schematron-path', default=['PEPPOL-EN16931-UBL.xsl'],
                             nargs='+', help="Schematron XSL files to validate with, defaults to bundled PEPPOL-EN16931-UBL.xsl")
    parser_send.add_argument('--keyfile', default='key.pem', help="The path to the private key, defaults to key.pem")
    parser_send.add_argument('--password', default='', help="The password for the private key, defaults to empty")
    parser_send.add_argument('--certfile', default='cert.pem', help="The path to the public key, defaults to cert.pem")
    parser_send.add_argument('--unwrap-sbh', action=argparse.BooleanOptionalAction,
                             help="Unwrap standard business header already present in document. Useful for testbed.")
    parser_send.add_argument('--test', action=argparse.BooleanOptionalAction, help="Use test SMP server, defaults to production")

    parser_validate = subparsers.add_parser('validate', help='Validate a Peppol document')
    parser_validate.add_argument('--document', help="The path of the document to validate", required=True)
    parser_validate.add_argument('--schematron-path', default=['PEPPOL-EN16931-UBL.xsl'],
                             nargs='+', help="Schematron XSL files to validate with, defaults to bundled PEPPOL-EN16931-UBL.xsl")

    parsed_args = parser.parse_args()

    if parsed_args.verbose:
        enable_debug_logging()

    if parsed_args.command == "send":
        with open(parsed_args.document, 'rb') as f:
            document_content = f.read()

        errors = validate_peppol_document(document_content, parsed_args.schematron_path)
        if errors:
            for d in errors:
                print(d)
            sys.exit(1)

        if parsed_args.unwrap_sbh:
            document_content = etree.tostring(etree.fromstring(document_content).find('./{*}Invoice'))

        try:
            stats = send_peppol_document(document_content,
                                         parsed_args.xmlsec_path, parsed_args.keyfile,
                                         keyfile_password=parsed_args.password, certfile=parsed_args.certfile,
                                         test_environment=parsed_args.test, document_type_version='2.1')
            print(stats)
        except SendPeppolError as ex:
            print(f"Failed with: {ex.code} {ex}")
            sys.exit(1)
        except Exception as ex:
            print(f"Failed with: {ex}")
            sys.exit(1)
    elif parsed_args.command == "validate":
        with open(parsed_args.document, 'rb') as f:
            document_content = f.read()

        errors = validate_peppol_document(document_content, parsed_args.schematron_path)
        if errors:
            for d in errors:
                print(d)
            sys.exit(1)
    else:
        pass


if __name__ == "__main__":
    main()
