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
    return result.rstrip("/") + "/iso6523-actorid-upis::" + participant_id


def get_service_urls_for_participant_from_smp(participant_id, test_environment, timeout, user_agent):
    # SML: receiver -> SMP domain (DNS)
    smp_url = get_smp_url_from_dns(participant_id, test_environment)

    try:
        r = requests.get(smp_url, timeout=timeout, headers={"User-Agent": user_agent})
        r.raise_for_status()
    except (ConnectionError, requests.exceptions.RequestException) as e:
        temporary = True
        code = 'server-error'
        if ((isinstance(e, requests.exceptions.HTTPError) and e.response and e.response.status_code < 500)
            or ('[Errno -2] Name or service not known' in str(e))):
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


def get_service_info_for_participant_from_smp(participant_id, document_type, test_environment, timeout, user_agent):
    """Lookup participant in Peppol Service Metadata Publisher for
    information on service type. Service type is Scope.Identifier +
    '::' + Scope.InstanceIdentifier from the Peppol header."""

    service_urls = get_service_urls_for_participant_from_smp(participant_id, test_environment, timeout, user_agent)
    service_url = next((url for url in service_urls if urllib.parse.unquote(url).endswith(document_type)), None)
    if not service_url:
        raise make_sendpeppol_error("{0} not found in {1}".format(document_type, [urllib.parse.unquote(url) for url in service_urls]), 'not-found-in-smp')

    try:
        r = requests.get(service_url, timeout=timeout, headers={"User-Agent": user_agent})
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


def check_missing_peppol_doc_types(service_urls):
    supported_doc_types = [url for url in service_urls if "busdox-docid-qns" in url]
    supported_doc_types = ",".join(supported_doc_types)

    required_doc_types = ['Invoice-2', 'CreditNote-2']
    missing_doc_types = []
    for required_doc_type in required_doc_types:
        if required_doc_type not in supported_doc_types:
            missing_doc_types.append(required_doc_type)

    return missing_doc_types


def validate_peppol_receiver(peppol_recipient, test_environment=True, timeout=20, user_agent="peppol-py", ignore_registry_communication_errors=False):
    """Check whether a recipient is registered in SMP and supports Invoice and CreditNote document types.

    ``peppol_recipient`` (str): the Peppol participant identifier, e.g. ``0184:12345678``.

    ``test_environment`` (bool): use test SML servers?

    ``timeout`` (int): number of seconds to wait for response from SMP.

    ``user_agent`` (str): HTTP User-Agent header value.

    ``ignore_registry_communication_errors`` (bool): if ``True``, server errors during SMP lookup
    will be silently ignored and ``None`` returned instead of raising.

    Raises :class:`SendPeppolError` if the recipient is not found or is missing required document types.
    Returns ``None`` on success.
    """
    try:
        service_urls = get_service_urls_for_participant_from_smp(peppol_recipient, test_environment, timeout, user_agent)
    except (ConnectionError, requests.exceptions.RequestException) as e:
        if ignore_registry_communication_errors:
            return None
        else:
            raise make_sendpeppol_error(str(e), 'server-error', temporary=True)

    if not service_urls:
        raise make_sendpeppol_error("Receiver not found", 'not-found-in-smp')

    missing_doc_types = check_missing_peppol_doc_types(service_urls)
    if missing_doc_types:
        raise make_sendpeppol_error(
            "{0} not found in {1}".format(", ".join(missing_doc_types), [urllib.parse.unquote(url) for url in service_urls]),
            'not-found-in-smp', missing_doc_types=missing_doc_types)

    return None
