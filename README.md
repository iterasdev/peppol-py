# Peppol-py

A python implementation for sending [peppol eDelivery] AS4
documents. Most implementations are written in java such as [oxalis]
and [phase4] and are very complex. This code base is an order of
magnitude smaller.

The implementation makes use of [xmlsec] for signing and
encryption. Version 1.3 is needed for the rsa oaep aes128 gcm
encryption used in peppol. Debian is still using 1.2 in both stable
and unstable as of 5/6 2025 so we use xmlsec 1.3 as an external
binary.

The protocol *should* be relatively simple:
 - Generate a transfer document with:
   - UserMessage describing the sender and receiver
   - Empty body
   - The gzipped actual document as an attachment
 - Hash the 3 elements and sign that.
 - Encrypt the gzipped attachment for the intended receiver
 - POST the transfer document with signature and encryption info, with
   the encrypted attachment as a multipart mime to the AS4 endpoint

The implementation includes support for using the SML and SMP protocol
for finding the AS4 endpoint of the receiver.

## CLI Usage

```
> python3 -m peppol_py --help

usage: python -m peppol_py [-h] [--verbose | --no-verbose] {send,validate} ...

Peppol utility

positional arguments:
  {send,validate}       command
    send                Send a Peppol document
    validate            Validate a Peppol document

options:
  -h, --help            show this help message and exit
  --verbose, --no-verbose
                        Enable debug logging

> python -m peppol_py send --help
usage: python -m peppol_py send [-h] --document DOCUMENT --service-provider SERVICE_PROVIDER
                                     [--xmlsec-path XMLSEC_PATH]
                                     [--schematron-path SCHEMATRON_PATH [SCHEMATRON_PATH ...]]
                                     [--keyfile KEYFILE] [--password PASSWORD] [--certfile CERTFILE]
                                     [--unwrap-sbh | --no-unwrap-sbh]
                                     [--test | --no-test]

options:
  -h, --help            show this help message and exit
  --document DOCUMENT   The path of the document to send
  --xmlsec-path XMLSEC_PATH
                        The path to latest xmlsec binary
  --schematron-path SCHEMATRON_PATH [SCHEMATRON_PATH ...]
                        Schematron XSL files to validate with, defaults to bundled PEPPOL-EN16931-UBL.xsl
  --keyfile KEYFILE     The path to the private key, defaults to key.pem
  --password PASSWORD   The password for the private key, defaults to empty
  --certfile CERTFILE   The path to the public key, defaults to cert.pem
  --unwrap-sbh, --no-unwrap-sbh
                        Unwrap standard business header already present in document. Useful for testbed.
  --service-provider SERVICE_PROVIDER
                        Service provider ID
  --test, --no-test     Use test SMP server, defaults to production

> python -m peppol_py validate --help
usage: python -m peppol_py validate [-h] --document DOCUMENT 
                                         [--schematron-path SCHEMATRON_PATH [SCHEMATRON_PATH ...]]

options:
  -h, --help            show this help message and exit
  --document DOCUMENT   The path of the document to validate
  --schematron-path SCHEMATRON_PATH [SCHEMATRON_PATH ...]
                        Schematron XSL files to validate with, defaults to bundled PEPPOL-EN16931-UBL.xsl
```

### Examples

Send a document:

```
python3 -m peppol_py --verbose send --document test_invoice.xml \
        --schematron-path CEN-EN16931-UBL.xsl --test \
        --certfile cert.pem --keyfile key.pem \
        --service-provider PXX000000 
```

Validate a document:

```
python3 -m peppol_py validate --document test_invoice.xml \
        --schematron-path CEN-EN16931-UBL.xsl
```

## Python API

### Send document

To send a prepared xml document, call `send_peppol_document`:

``` python
from peppol_py import send_peppol_document
stats = send_peppol_document(
    document_content, xmlsec_path, keyfile, keyfile_password, certfile,
    sender_id=None, receiver_id=None, sender_country=None,
    document_type_version=None, test_environment=True, timeout=20, dryrun=False
)
```

See docstring or ``help(peppol_py.send_peppol_document)`` on a Python console for a full parameter description.


### Validate document

To validate a prepared document, call ``validate_peppol_document``:

``` python
from peppol_py import validate_peppol_document
stats = validate_peppol_document(
    document_content, schematron_xsls, remove_namespaces_from_errors=True, warnings=False
)
```

See docstring or ``help(peppol_py.validate_peppol_document)`` on a Python console for a full parameter description.

### Send statistics

To validate a prepared document, call ``send_peppol_statistics``:

``` python
from peppol_py import send_peppol_statistics

stats = send_peppol_statistics(
    aggr_stats, our_endpoint, xmlsec_path, keyfile, password, certfile,
    test_environment
)
```

See docstring or ``help(peppol_py.send_peppol_statistics)`` on a Python console for a full parameter description.

## Background

This implementation was sponsored by [iteras], one of the largest SSAS
solutions in the nordics for managing print and digital media
subscriptions.

[peppol eDelivery]: https://ec.europa.eu/digital-building-blocks/wikis/display/DIGITAL/eDelivery+AS4+-+1.15
[oxalis]: https://github.com/OxalisCommunity
[phase4]: https://github.com/phax/phase4
[xmlsec]: https://github.com/lsh123/xmlsec
[iteras]: https://www.iteras.dk/
