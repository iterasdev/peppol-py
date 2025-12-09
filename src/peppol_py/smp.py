import re

from lxml import etree

import base64
import dns.resolver
import urllib.parse
import requests
import hashlib

from .exception import make_sendpeppol_error


def get_smp_url_from_dns(participant_id, test_environment):
    smp_id = base64.b32encode(hashlib.sha256(participant_id.lower().encode()).digest()).decode().rstrip("=")

    if test_environment:
        base_hostname = 'acc.edelivery.tech.ec.europa.eu'
    else:
        base_hostname = 'edelivery.tech.ec.europa.eu'

    smp_domain = f'{smp_id}.iso6523-actorid-upis.{base_hostname}'

    resolver = dns.resolver.Resolver()
    try:
        answers = resolver.resolve(smp_domain, 'NAPTR')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer) as e:
        raise make_sendpeppol_error(str(e), 'dns-error', temporary=False)
    except dns.resolver.DNSException as e:
        raise make_sendpeppol_error(str(e), 'dns-error', temporary=True)

    result = None
    for rdata in sorted(answers, key=lambda rdata: rdata.order):
        # This is not a full implementation of the NAPTR spec (RFC2915) but should support everything used by Peppol
        # and be somewhat safe against unexpected record contents.
        if rdata.flags.decode().lower() == "u" and rdata.service.decode().lower() == "meta:smp":
            delim_char = rdata.regexp.decode()[0]
            regex_data = rdata.regexp.decode().split(delim_char)
            result = re.sub('^' + regex_data[1] + '$', regex_data[2], smp_domain)

            if not result.startswith("https://") and not result.startswith("http://"):
                raise make_sendpeppol_error("Regexp result of NATPR record is not an URL", 'dns-error', temporary=False)
            break

    if not result:
        raise make_sendpeppol_error("The NATPR record could not be resolved to an URL", 'dns-error', temporary=False)

    # SMP: domain + path -> xml with service descriptions
    # get all available interfaces (invoice, credit note etc.)
    return urllib.parse.urljoin(result, "./iso6523-actorid-upis::" + participant_id)


def get_service_urls_for_participant_from_smp(participant_id, test_environment, timeout):
    # SML: receiver -> SMP domain (DNS)
    smp_url = get_smp_url_from_dns(participant_id, test_environment)

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
