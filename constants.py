ENV_NS = 'http://www.w3.org/2003/05/soap-envelope'
DS_NS = 'http://www.w3.org/2000/09/xmldsig#'
ENC_NS = 'http://www.w3.org/2001/04/xmlenc#'
ENC11_NS = 'http://www.w3.org/2009/xmlenc11#'

SHA256 = 'http://www.w3.org/2001/04/xmlenc#sha256'
RSA_SHA256 = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
RSA_OAEP = 'http://www.w3.org/2009/xmlenc11#rsa-oaep'
MGF_SHA256 = 'http://www.w3.org/2009/xmlenc11#mgf1sha256'

WSS_BASE = 'http://docs.oasis-open.org/wss/2004/01/'
WSSE_NS = WSS_BASE + 'oasis-200401-wss-wssecurity-secext-1.0.xsd'
WSU_NS = WSS_BASE + 'oasis-200401-wss-wssecurity-utility-1.0.xsd'

WSSE11_NS = 'http://docs.oasis-open.org/wss/oasis-wss-wssecurity-secext-1.1.xsd'

BASE64B = WSS_BASE + 'oasis-200401-wss-soap-message-security-1.0#Base64Binary'
X509TOKEN = WSS_BASE + 'oasis-200401-wss-x509-token-profile-1.0#X509v3'

NS2 = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/'
ATTACHMENT = 'http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Content-Signature-Transform'
C14N = 'http://www.w3.org/2001/10/xml-exc-c14n#'

STBH = 'http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader'
