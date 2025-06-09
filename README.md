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
   the encrypted attachent as a multipart mime to the AS4 endpoint

The implementation includes support for using the SML and SMP protocol
for finding the AS4 endpoint of the receiver.

## Usage

```
> python3 sender.py --help

Send peppol files

options:
  -h, --help            show this help message and exit
  --document DOCUMENT   The path of the document to send
  --xmlsec-path XMLSEC_PATH
                        The path to latest xmlsec binary
  --schematron-path SCHEMATRON_PATH [SCHEMATRON_PATH ...]
                        Schematron XSL files to validate with
  --keyfile KEYFILE     The path to the private key
  --password PASSWORD   The password for the private key
  --certfile CERTFILE   The path to the public key
  --verbose, --no-verbose
                        Enable debug logging
  --test, --no-test     Use test SMP server
```

## Example

```
python3 sender.py --document test_invoice.xml --schematron-path CEN-EN16931-UBL.xsl --test
```

## API

### Send document

To send a prepared xml document, call `send_peppol_document` in sender.py:

``` python
stats = send_peppol_document(document_content, xmlsec_path, keyfile, keyfile_password, certfile, sender_id=None, receiver_id=None, sender_country=None, document_type_version=None, test_environment=True, timeout=20, dryrun=False)
```

`document_content` to send. Note the standard business header will
automatically be added.

`xmlsec_path` specifies the path to a xmlsec 1.3 or higher binary.

`keyfile` the path to the private key of the sender.

`password` the password for the private key of the sender.

`certfile` the path to the public key of the sender.

`sender_id` optional sender id, will be extracted from document if not
specified.

`receiver_id` optional receiver id, will be extracted from document if
not specified.

`sender_country` optional sender country, will be extracted from
document if not specified.

`document_type_version` the document type version, if not specified
will be last part of CustomizationID. For invoices should be set to
`2.1`.

`test_environment` use test SML servers?

`timeout` number of seconds to wait for response from the remote end.

`dryrun` if specified, will prepare, get the endpoint, test document
for validation errors but not send to remote endpoint.

### Send statistics

To send statistics for access point, call `send_peppol_statistics` in statistics.py:

``` python
stats = send_peppol_statistics(aggr_stats, our_endpoint, xmlsec_path, keyfile, password, certfile, test_environment)
```

`aggr_stats` is a dict of the aggregated statistics to send in the
following format:

``` python
{
  'from_date': <DATETIME>,
  'to_date': <DATETIME>,
  'outgoing': <NUM>,
  'outgoing_by_transport_profile': # { 'transport_profile': <NUM> },
  'outgoing_by_receiver_common_name_document_type_process_type': # { ('receiver_common_name', 'document_type', 'process_type'): <NUM> },
  'senders': <SET_OF_IDS>,
  'senders_by_country': { 'country': <SET_OF_IDS> },
  'senders_by_document_type_country': { ('document_type', 'country'): <SET_OF_IDS> },
  'senders_by_document_type_process_type': { ('document_type', 'process_type'): <SET_OF_IDS> },
  'senders_by_document_type_process_type_country': { ('document_type', 'process_type', 'country'): <SET_OF_IDS> }
}
```

`our_endpoint` is a dict with endpoint information. Example:

``` python
{
  'id': "PDK000592",
  'type': "DK:P",
  'country': "DK"
}
```

`xmlsec_path` specifies the path to a xmlsec 1.3 or higher binary.

`keyfile` the path to the private key of the sender.

`password` the password for the private key of the sender.

`certfile` the path to the public key of the sender.

`test_environment` use test SML servers?

## Background

This implementation was sponsored by [iteras], one of the largest SSAS
solutions in the nordics for managing print and digital media
subscriptions.

## License

The software is free to use and is provided under the [beerware] license.

[peppol eDelivery]: https://ec.europa.eu/digital-building-blocks/wikis/display/DIGITAL/eDelivery+AS4+-+1.15
[oxalis]: https://github.com/OxalisCommunity
[phase4]: https://github.com/phax/phase4
[xmlsec]: https://github.com/lsh123/xmlsec
[iteras]: https://www.iteras.dk/
[beerware]: https://en.wikipedia.org/wiki/Beerware
