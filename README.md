# Peppol-py

A python3 implementation of sending [peppol eDelivery] AS4
documents. Most implementations are written in java such as [oxalis]
and [phase4] and are very complex. This code base is an order of
magnitude smaller.

The implementation makes use of [xmlsec] for signing and
encryption. Version 1.3 is needed for the rsa oaep aes128 gcm
encryption used in peppol. The python bindings are not working with
that version so we use xmlsec 1.3 as an external binary.

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

[peppol eDelivery]: https://ec.europa.eu/digital-building-blocks/wikis/display/DIGITAL/eDelivery+AS4+-+1.15
[oxalis]: https://github.com/OxalisCommunity
[phase4]: https://github.com/phax/phase4
[xmlsec]: https://github.com/lsh123/xmlsec
