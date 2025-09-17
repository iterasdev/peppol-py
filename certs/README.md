# Root PEPPOL certificates

The certificates in this folder are from the [peppol commons repo].
They should be valid until 2035 and are used for validating receiver
certificates before sending.

## Generate pem files

```
openssl pkcs12 -in certs/ap-prod-truststore.p12 -out certs/ap-prod-truststore.pem -cacerts
openssl pkcs12 -in certs/ap-test-truststore.p12 -out certs/ap-test-truststore.pem -cacerts
```

Password is: peppol.

[peppol commons repo]: https://github.com/phax/peppol-commons/tree/master/peppol-commons/src/main/resources/truststore
