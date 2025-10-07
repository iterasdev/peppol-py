from typing import List

from lxml import etree
from lxml.builder import ElementMaker

from .exception import SendPeppolError, make_sendpeppol_error
from .validation import validate_peppol_document
from .sender import send_peppol_document, get_common_name_from_certificate

PEPPOL_ORGANIZATION_ID_TYPES = {
    # https://docs.peppol.eu/edelivery/codelists/v9.3/Peppol%20Code%20Lists%20-%20Participant%20identifier%20schemes%20v9.3.json
    # Backwards-compatibility additions
    'EAN': '0088',  # official name: GLN
    'DK:CVR': '0184',  # official name: DK:DIGST
    'NO:ORGNR': '0192',  # official name: NO:ORG
    'IS:KT': '0196',  # official name: IS:KTNR
    # Official list
    'FR:SIRENE': '0002',
    'SE:ORGNR': '0007',
    'FR:SIRET': '0009',
    'DUNS': '0060',
    'GLN': '0088',
    'DK:P': '0096',
    'IT:FTI': '0097',
    'NL:KVK': '0106',
    'EU:NAL': '0130',
    'IT:SIA': '0135',
    'IT:SECETI': '0142',
    'AU:ABN': '0151',
    'CH:UIDB': '0183',
    'DK:DIGST': '0184',
    'JP:SST': '0188',
    'NL:OINO': '0190',
    'EE:CC': '0191',
    'NO:ORG': '0192',
    'UBLBE': '0193',
    'SG:UEN': '0195',
    'IS:KTNR': '0196',
    'DK:ERST': '0198',
    'LEI': '0199',
    'LT:LEC': '0200',
    'IT:CUUO': '0201',
    'DE:LWID': '0204',
    'IT:COD': '0205',
    'BE:EN': '0208',
    'GS1': '0209',
    'IT:CFI': '0210',
    'IT:IVA': '0211',
    'FI:OVT2': '0216',
    'LV:URN': '0218',
    'JP:IIN': '0221',
    'FR:CTC': '0225',
    'MY:EIF': '0230',
    'AE:TIN': '0235',
    'LU:MAT': '0240',
    'SPIS': '0242',
    'HU:VAT': '9910',
    'EU:REID': '9913',
    'AT:VAT': '9914',
    'AT:GOV': '9915',
    'IBAN': '9918',
    'AT:KUR': '9919',
    'ES:VAT': '9920',
    'AD:VAT': '9922',
    'AL:VAT': '9923',
    'BA:VAT': '9924',
    'BE:VAT': '9925',
    'BG:VAT': '9926',
    'CH:VAT': '9927',
    'CY:VAT': '9928',
    'CZ:VAT': '9929',
    'DE:VAT': '9930',
    'EE:VAT': '9931',
    'GB:VAT': '9932',
    'GR:VAT': '9933',
    'HR:VAT': '9934',
    'IE:VAT': '9935',
    'LI:VAT': '9936',
    'LT:VAT': '9937',
    'LU:VAT': '9938',
    'LV:VAT': '9939',
    'MC:VAT': '9940',
    'ME:VAT': '9941',
    'MK:VAT': '9942',
    'MT:VAT': '9943',
    'NL:VAT': '9944',
    'PL:VAT': '9945',
    'PT:VAT': '9946',
    'RO:VAT': '9947',
    'RS:VAT': '9948',
    'SI:VAT': '9949',
    'SK:VAT': '9950',
    'SM:VAT': '9951',
    'TR:VAT': '9952',
    'VA:VAT': '9953',
    'FR:VAT': '9957',
    'US:EIN': '9959',
}
PEPPOL_REVERSED_ORGANIZATION_ID_TYPES = {v: k for k, v in PEPPOL_ORGANIZATION_ID_TYPES.items()}

PEPPOL_END_USER_STATISTICS_SCHEMATRON_XSLS = ['peppol-end-user-statistics-reporting-1.1.4.xsl']
PEPPOL_TRANSACTION_STATISTICS_SCHEMATRON_XSLS = ['peppol-transaction-statistics-reporting-1.0.4.xsl']

def skip_none_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}

def clean_organization_id(organization_id, organization_id_type):
    if organization_id_type in PEPPOL_REVERSED_ORGANIZATION_ID_TYPES:
        scheme_id = organization_id_type
    else:
        scheme_id = PEPPOL_ORGANIZATION_ID_TYPES.get(organization_id_type)
    return scheme_id, organization_id

def generate_organization_id(E, ns, id_name, organization_id, organization_id_type):
    scheme_id, org_id = clean_organization_id(organization_id, organization_id_type)

    return E(ns("cbc", id_name), org_id, **skip_none_kwargs({'schemeID': scheme_id}))

def generate_common_name(certfile):
    with open(certfile, 'rb') as sender_certfile_f:
        sender_cert = sender_certfile_f.read()
    return get_common_name_from_certificate(sender_cert)

def generate_peppol_statistics_header(E, from_date, to_date, sender_common_name):
    return E('Header',
             E('ReportPeriod',
               E('StartDate', from_date.isoformat()),
               E('EndDate', to_date.isoformat())),
             E('ReporterID', sender_common_name, schemeID='CertSubjectCN'))

def render_peppol_end_user_statistics_xml(stats, sender_common_name):
    E = ElementMaker()

    xml = E('EndUserStatisticsReport',
            E('CustomizationID', 'urn:fdc:peppol.eu:edec:trns:end-user-statistics-report:1.1'),
            E('ProfileID', 'urn:fdc:peppol.eu:edec:bis:reporting:1.0'),
            generate_peppol_statistics_header(E, stats['from_date'], stats['to_date'], sender_common_name),
            xmlns='urn:fdc:peppol:end-user-statistics-report:1.1')

    def generate_senders_and_receivers(s, r=None):
        if s is None:
            s = set()
        if r is None:
            r = set()
        return [E('SendingEndUsers', str(len(s))),
                E('ReceivingEndUsers', str(len(r))),
                E('SendingOrReceivingEndUsers', str(len(s | r)))]

    xml.append(E('FullSet',
                 *generate_senders_and_receivers(stats['senders'])
                 ))

    for country_code, senders in stats['senders_by_country'].items():
        xml.append(E('Subset',
                     E('Key', country_code, metaSchemeID="CC", schemeID="EndUserCountry"),
                     *generate_senders_and_receivers(senders),
                     type='PerEUC'))

    for (document_type, country_code), senders in stats['senders_by_document_type_country'].items():
        xml.append(E('Subset',
                     E('Key', document_type, metaSchemeID="DT", schemeID="busdox-docid-qns"),
                     E('Key', country_code, metaSchemeID="CC", schemeID="EndUserCountry"),
                     *generate_senders_and_receivers(senders),
                     type='PerDT-EUC'))

    for (document_type, process_type), senders in stats['senders_by_document_type_process_type'].items():
        xml.append(E('Subset',
                     E('Key', document_type, metaSchemeID="DT", schemeID="busdox-docid-qns"),
                     E('Key', process_type, metaSchemeID="PR", schemeID="cenbii-procid-ubl"),
                     *generate_senders_and_receivers(senders),
                     type='PerDT-PR'))

    for (document_type, process_type, country_code), senders in stats['senders_by_document_type_process_type_country'].items():
        xml.append(E('Subset',
                     E('Key', document_type, metaSchemeID="DT", schemeID="busdox-docid-qns"),
                     E('Key', process_type, metaSchemeID="PR", schemeID="cenbii-procid-ubl"),
                     E('Key', country_code, metaSchemeID="CC", schemeID="EndUserCountry"),
                     *generate_senders_and_receivers(senders),
                     type='PerDT-PR-EUC'))

    return etree.tostring(xml, xml_declaration=True, encoding='UTF-8', method='xml')


def render_peppol_transaction_statistics_xml(stats, certfile):
    E = ElementMaker()

    xml = E('TransactionStatisticsReport',
            E('CustomizationID', 'urn:fdc:peppol.eu:edec:trns:transaction-statistics-reporting:1.0'),
            E('ProfileID', 'urn:fdc:peppol.eu:edec:bis:reporting:1.0'),
            generate_peppol_statistics_header(E, stats['from_date'], stats['to_date'], certfile),
            xmlns='urn:fdc:peppol:transaction-statistics-report:1.0')

    xml.append(E('Total',
                 E('Incoming', '0'),
                 E('Outgoing', str(stats['outgoing']))
                 ))

    for transport_profile, outgoing in stats['outgoing_by_transport_profile'].items():
        xml.append(E('Subtotal',
                     E('Key', transport_profile, metaSchemeID="TP", schemeID="Peppol"),
                     E('Incoming', '0'),
                     E('Outgoing', str(outgoing)),
                     type='PerTP'))

    for (receiver_common_name, document_type, process_type), outgoing in stats['outgoing_by_receiver_common_name_document_type_process_type'].items():
        xml.append(E('Subtotal',
                     E('Key', receiver_common_name, metaSchemeID="SP", schemeID="CertSubjectCN"),
                     E('Key', document_type, metaSchemeID="DT", schemeID="busdox-docid-qns"),
                     E('Key', process_type, metaSchemeID="PR", schemeID="cenbii-procid-ubl"),
                     E('Incoming', '0'),
                     E('Outgoing', str(outgoing)),
                     type='PerSP-DT-PR'))

    # we don't output PerSP-DT-CC as we're only sending

    return etree.tostring(xml, xml_declaration=True, encoding='UTF-8', method='xml')

def send_peppol_statistics(
    aggr_stats: dict,
    our_endpoint: dict,
    xmlsec_path: str,
    keyfile: str,
    password: str,
    certfile: str,
    test_environment: bool,
    receiver_id: str='9925:BE0848934496'
) -> List[dict]:
    """
    Send peppol statistics to the required reporting endpoint.

    ``aggr_stats`` (dict) should look like this:
    ```
    document_type = 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1',
    process_type = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
    transport_profile = 'peppol-transport-as4-v2_0'
    sender_country = 'DK'
    receiver_common_name = 'PNO000063'
    aggr_stats = {
      'from_date': <DATETIME>,
      'to_date': <DATETIME>,
      'outgoing': <NUM>,
      'outgoing_by_transport_profile': { transport_profile: <NUM> },
      'outgoing_by_receiver_common_name_document_type_process_type': { (receiver_common_name, document_type, process_type): <NUM> },
      'senders': <SET_OF_IDS>,
      'senders_by_country': { sender_country: <SET_OF_IDS> },
      'senders_by_document_type_country': { (document_type, country): <SET_OF_IDS> },
      'senders_by_document_type_process_type': { (document_type, process_type): <SET_OF_IDS> },
      'senders_by_document_type_process_type_country': { (document_type, process_type, sender_country): <SET_OF_IDS> }
    }
    ```

    ``our_endpoint`` (dict) should look like this: ``{ "id": "PDK000592", "type": "DK:P", "country": "DK" }``

    ``xmlsec_path`` (str): specifies the path to a xmlsec 1.3 or higher binary.

    ``keyfile`` (str): the path to the private key of the sender.

    ``password`` (str): the password for the private key of the sender.

    ``certfile`` (str): the path to the public key of the sender.

    ``test_environment`` (bool): use test SML servers?

    ``receiver_id`` (str): Receiver participant, defaults to the OpenPeppol organization
    """
    sender_common_name = generate_common_name(certfile)
    end_user_xml = render_peppol_end_user_statistics_xml(aggr_stats, sender_common_name)
    transaction_xml = render_peppol_transaction_statistics_xml(aggr_stats, sender_common_name)

    sender_id_element = generate_organization_id(ElementMaker(), lambda shorthand, tag: tag, "EndpointID", our_endpoint['id'], our_endpoint['type'])
    sender_id = sender_id_element.get('schemeID') + ':' + sender_id_element.text

    results = []
    failure = None
    for xml, schematron_xsls in [(end_user_xml, PEPPOL_END_USER_STATISTICS_SCHEMATRON_XSLS), (transaction_xml, PEPPOL_TRANSACTION_STATISTICS_SCHEMATRON_XSLS)]:
        errors = validate_peppol_document(xml, schematron_xsls)
        if errors:
            for d in errors:
                print(d)
            raise make_sendpeppol_error('Schematron validation failed.', 'validation', False)

        try:
            results.append(
                send_peppol_document(
                    xml, xmlsec_path, keyfile, password, certfile, sender_id=sender_id, receiver_id=receiver_id, sender_country=our_endpoint['country'], test_environment=test_environment, timeout=20,
                )
            )
        except SendPeppolError as ex:
            print(f"Failed with: {ex.code} {ex}")
            failure = ex
    if failure:
        raise failure
    return results