# Root PEPPOL certificates

The files "g2-g3" include the G2 and G3 certificates.

The files "g3" include only the G3 certificates.

Original source for G2: https://openpeppol.atlassian.net/wiki/spaces/OPMA/pages/193069072/Introduction+to+the+revised+PKI+Certificate+infrastructure+and+issuing+process

Original source for G3: https://openpeppol.atlassian.net/wiki/spaces/OPMA/pages/4344053761/Peppol+PKI+2025+-+Certificate+Authorities

Source of the p12 file is the [peppol commons repo].

## Generate pem files

```
openssl pkcs12 -in certs/ap-prod-truststore.p12 -out certs/ap-prod-truststore.pem -cacerts
openssl pkcs12 -in certs/ap-test-truststore.p12 -out certs/ap-test-truststore.pem -cacerts
```

Password is: peppol.

[peppol commons repo]: https://github.com/phax/peppol-commons/tree/master/peppol-commons/src/main/resources/truststore
