# Examples

Example commands for common xmlsec operations

## xmlsec 1.3 signing

```
~/Downloads/xmlsec1-1.3.2/install/bin/xmlsec1 --sign --id-attr:Id Body --id-attr:Id Messaging --verbose --privkey-pem test.key.pem --output output4-signed.xml --lax-key-search output4-no-sign.xml
```

## xmlsec 1.3 verify

```
~/Downloads/xmlsec1-1.3.2/install/bin/xmlsec1 --verify --id-attr:Id Body --id-attr:Id Messaging --verbose --pubkey-cert-pem cert.pem --lax-key-search output4-signed.xml
```

## xmlsec 1.3 encryption

```
~/Downloads/xmlsec1-1.3.2/install/bin/xmlsec1 --encrypt --pubkey-cert-pem cert.pem --session-key aes-128 --binary-data test.xml.gz --output test-result.xml --verbose --lax-key-search encryption.xml
```

## xmlsec 1.3 decryption

```
~/Downloads/xmlsec1-1.3.2/install/bin/xmlsec1 --decrypt --privkey-pem test.key.pem --verbose --lax-key-search test-result.xml &> test-decrypted.xml.gz
```
