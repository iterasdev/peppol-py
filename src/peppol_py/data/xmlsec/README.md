# Examples

Example commands for common xmlsec operations

## xmlsec signing

```
xmlsec1 --sign --id-attr:Id Body --id-attr:Id Messaging --verbose --privkey-pem test.key.pem --output output4-signed.xml --lax-key-search output4-no-sign.xml
```

## xmlsec verify

```
xmlsec1 --verify --id-attr:Id Body --id-attr:Id Messaging --verbose --pubkey-cert-pem cert.pem --lax-key-search output4-signed.xml
```

## xmlsec encryption

```
xmlsec1 --encrypt --pubkey-cert-pem cert.pem --session-key aes-128 --binary-data test.xml.gz --output test-result.xml --verbose --lax-key-search sendpeppol_encrypt_template.xml
```

## xmlsec decryption

```
xmlsec1 --decrypt --privkey-pem test.key.pem --verbose --lax-key-search test-result.xml &> test-decrypted.xml.gz
```
