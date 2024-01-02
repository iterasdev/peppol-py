from sml import get_domain_using_http
from smp import get_smp_info, extract_as4_information
from as4_sender import post_multipart

# params
xmlsec_path = "~/Downloads/xmlsec1-1.3.2/install/bin/xmlsec1"
keyfile = "test.key.pem"
certfile = "cert.pem"
password = ""

filename = "PEPPOL_TestCase_0232_20231222T1138Z/TestFile_001__BISv3_Invoice.xml"

their_certfile = "server-cert.pem"
url = "https://phase4-controller.testbed.peppol.org/as4"
#url = "https://oxalis.beta.iola.dk/as4"

#receiver = '9928:CY99990011B' # final URL is buggy
#receiver = '0188:2011001016148' # good example
#receiver = '9922:NGTBCNTRLP1001' # from test certification file
receiver = '0192:992957433'


# this doesn't seem to work properly and test cert uses http instead?
#smp_domain = get_domain_using_sml(receiver)

smp_domain = get_domain_using_http(receiver)
smp_contents = get_smp_info(smp_domain, receiver)
url, their_cert = extract_as4_information(smp_contents)

their_certfile = '/tmp/their-cert.pem'
with open(their_certfile, 'w') as f:
    f.write('-----BEGIN CERTIFICATE-----\n' + their_cert + '\n-----END CERTIFICATE-----')

post_multipart(url, xmlsec_path, filename, keyfile, password, certfile, their_certfile)
