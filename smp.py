from lxml import etree

import urllib.parse
import requests
import hashlib

from exception import make_sendpeppol_error

def get_service_urls_for_participant_from_smp(participant_id, test_environment, timeout):
    # SML: receiver -> SMP domain (DNS)
    smp_id = 'B-' + hashlib.md5((participant_id.lower()).encode('utf-8')).hexdigest()
    if test_environment:
        base_hostname = 'acc.edelivery.tech.ec.europa.eu'
    else:
        base_hostname = 'edelivery.tech.ec.europa.eu'

    smp_domain = f'{smp_id}.iso6523-actorid-upis.{base_hostname}'

    # SMP: domain + path -> xml with service descriptions
    # get all available interfaces (invoice, credit note etc.)
    smp_url = 'http://' + smp_domain + "/iso6523-actorid-upis::" + participant_id

    try:
        r = requests.get(smp_url, timeout=timeout)
        r.raise_for_status()
    except (ConnectionError, requests.exceptions.RequestException) as e:
        temporary = True
        code = 'server-error'
        if isinstance(e, requests.exceptions.HTTPError) and e.response and e.response.status_code < 500:
            temporary = False
            code = 'not-found-in-smp'

        raise make_sendpeppol_error(str(e), code, temporary=temporary, url=smp_url)

    try:
        service_urls_xml = etree.fromstring(r.content)
    except ValueError as e:
        raise make_sendpeppol_error(str(e), 'server-error', temporary=True, url=smp_url)

    service_urls = []
    for el in service_urls_xml.findall(".//{*}ServiceMetadataReference"):
        href = el.get('href')
        if href:
            service_urls.append(href)

    return service_urls


def get_service_info_for_participant_from_smp(participant_id, document_type, test_environment, timeout):
    """Lookup participant in Peppol Service Metadata Publisher for
    information on service type. Service type is Scope.Identifier +
    '::' + Scope.InstanceIdentifier from the Peppol header."""

    service_urls = get_service_urls_for_participant_from_smp(participant_id, test_environment, timeout)
    service_url = next((url for url in service_urls if url.endswith(urllib.parse.quote(document_type))), None)
    if not service_url:
        raise make_sendpeppol_error("{0} not found in {1}".format(document_type, [urllib.parse.unquote(url) for url in service_urls]), 'not-found-in-smp')

    try:
        r = requests.get(service_url, timeout=timeout)
        r.raise_for_status()
    except (ConnectionError, requests.exceptions.RequestException) as e:
        temporary = True
        code = 'server-error'
        if isinstance(e, requests.exceptions.HTTPError) and e.response and e.response.status_code < 500:
            temporary = False
            code = 'not-found-in-smp'

        raise make_sendpeppol_error(str(e), code, temporary=temporary, url=service_url)

    try:
        service_info_xml = etree.fromstring(r.content)
    except ValueError as e:
        raise make_sendpeppol_error(str(e), 'server-error', temporary=True)

    #print(r.content.decode().replace('>', '>\n'))

    # we don't check process match at the moment - to do that we'd to
    # get the process identifier from the Peppol header
    # <Type>PROCESSID</type> like we get the service identifier
    transport_profile = endpoint_url = certificate = None
    for endpoint_e in service_info_xml.findall('.//{*}ServiceInformation//{*}Process//{*}Endpoint'):
        transport_profile = endpoint_e.get('transportProfile')

        if not transport_profile.startswith('peppol-transport-as4'):
            continue

        endpoint_url = endpoint_e.findtext('./{*}EndpointReference/{*}Address')
        certificate = endpoint_e.findtext('./{*}Certificate')
        if certificate:
            certificate = b'-----BEGIN CERTIFICATE-----\n' + certificate.encode('ascii') + b'\n-----END CERTIFICATE-----'

        break

    return transport_profile, endpoint_url, certificate
