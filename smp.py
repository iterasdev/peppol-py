from lxml import etree

import urllib.request
import urllib.parse

# SMP: domain + path -> xml with service descriptions

def get_smp_info(domain, receiver):
    # all the available interfaces (invoice, credit note etc.)
    url = 'http://' + domain + "/iso6523-actorid-upis::" + receiver
    contents = urllib.request.urlopen(url).read()
    return contents

invoice_end = urllib.parse.quote("billing:3.0::2.1")

def find_invoice_smp_document(smp_contents):
    root = etree.fromstring(smp_contents)
    for child in root:
        for el in child:
            if el.get('href').endswith(invoice_end):
                return el.get('href')

def extract_as4_information(smp_contents):
    invoice_url = find_invoice_smp_document(smp_contents)
    invoice_smp = urllib.request.urlopen(invoice_url).read()
    root = etree.fromstring(invoice_smp)

    #id = root.findall(".//{*}ParticipantIdentifier")[0].text
    as4_endpoint = root.findall(".//{*}EndpointReference")[0][0].text
    certificate = root.findall(".//{*}Certificate")[0].text

    return [as4_endpoint, certificate]

