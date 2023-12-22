from as4_sender import post_multipart

# params
keyfile = "test.key.pem"
certfile = "cert.pem"
their_cert = "server-cert.pem"
password = ''
filename = 'PEPPOL_TestCase_0232_20231222T1138Z/TestFile_001__BISv3_Invoice.xml'
url = 'https://phase4-controller.testbed.peppol.org/as4'
#url = 'https://oxalis.beta.iola.dk/as4'

#receiver = '9928:CY99990011B' # final URL is buggy
#receiver = '0188:2011001016148' # good example
#receiver = '9922:NGTBCNTRLP1001' # from test certification file

# why doesn't test cert do this?
#smp_domain = get_domain_using_sml(receiver)

# ok
#smp_domain = get_domain_using_http(receiver)
#smp_contents = get_smp_info(smp_domain, receiver)
#extract_as4_information(smp_contents)

post_multipart(url, filename, keyfile, password, certfile, their_cert)
