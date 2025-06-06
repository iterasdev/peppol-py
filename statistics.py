from lxml import etree
from lxml.builder import ElementMaker

from exception import SendPeppolError
from validation import validate_peppol_document
from sender import send_peppol_document, get_common_name_from_certificate

PEPPOL_ORGANIZATION_ID_TYPES = {
    # https://docs.peppol.eu/poacc/billing/3.0/codelist/eas/
    'DK:CVR': '0184',
    'DK:P': '0096',
    'NO:ORGNR': '0192',
    'IS:KT': '0196',
    'SE:ORGNR': '0007',
    # 'FO:MVG': '', # not assigned yet in the code list
    'EAN': '0088',
    'GLN': '0088',
}
PEPPOL_REVERSED_ORGANIZATION_ID_TYPES = {v: k for k, v in PEPPOL_ORGANIZATION_ID_TYPES.items()}
PEPPOL_ORGANIZATION_ID_TYPES_WITH_COUNTRY_PREFIX = ['DK:CVR']

PEPPOL_END_USER_STATISTICS_SCHEMATRON_XSLS = ['peppol-end-user-statistics-reporting-1.1.4.xsl']
PEPPOL_TRANSACTION_STATISTICS_SCHEMATRON_XSLS = ['peppol-transaction-statistics-reporting-1.0.4.xsl']

def skip_none_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}

def generate_organization_id(E, ns, variant, options, id_name, organization_id, organization_id_type, country_code):
    if organization_id_type and organization_id_type.startswith('DK:') and country_code in ['GL', 'FO']:
        # the country code must still be DK even if they're outside DK
        country_code = 'DK'

    org_id_without_country = organization_id
    if org_id_without_country.startswith(country_code):
        org_id_without_country = org_id_without_country[len(country_code):]

    org_id_with_country = organization_id
    if not org_id_with_country.startswith(country_code):
        org_id_with_country = country_code + org_id_with_country

    org_id = org_id_with_country
    scheme_id = "ZZZ"

    if organization_id_type in PEPPOL_REVERSED_ORGANIZATION_ID_TYPES:
        scheme_id = organization_id_type
    else:
        scheme_id = PEPPOL_ORGANIZATION_ID_TYPES.get(organization_id_type)

    if PEPPOL_REVERSED_ORGANIZATION_ID_TYPES.get(scheme_id) not in PEPPOL_ORGANIZATION_ID_TYPES_WITH_COUNTRY_PREFIX:
        org_id = org_id_without_country

    return E(ns("cbc", id_name), org_id, **skip_none_kwargs({'schemeID': scheme_id}))

def generate_peppol_statistics_header(E, from_date, to_date, certfile):
    with open(certfile, 'rb') as sender_certfile_f:
        sender_cert = sender_certfile_f.read()
    sender_common_name = get_common_name_from_certificate(sender_cert)

    return E('Header',
             E('ReportPeriod',
               E('StartDate', from_date.isoformat()),
               E('EndDate', to_date.isoformat())),
             E('ReporterID', sender_common_name, schemeID='CertSubjectCN'))

def render_peppol_end_user_statistics_xml(stats, certfile):
    E = ElementMaker()

    xml = E('EndUserStatisticsReport',
            E('CustomizationID', 'urn:fdc:peppol.eu:edec:trns:end-user-statistics-report:1.1'),
            E('ProfileID', 'urn:fdc:peppol.eu:edec:bis:reporting:1.0'),
            generate_peppol_statistics_header(E, stats['from_date'], stats['to_date'], certfile),
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

# examples:
# - document_type = 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1',
# - process_type = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
# - transport_profile = 'peppol-transport-as4-v2_0'
# - sender_country = 'DK'
# - receiver_common_name = 'PNO000063'

# aggr_stats = {
#  'from_date': <DATETIME>,
#  'to_date': <DATETIME>,
#  'outgoing': <NUM>,
#  'outgoing_by_transport_profile': # { 'transport_profile': <NUM> },
#  'outgoing_by_receiver_common_name_document_type_process_type': # { ('receiver_common_name', 'document_type', 'process_type'): <NUM> },
#  'senders': <SET_OF_IDS>,
#  'senders_by_country': { 'country': <SET_OF_IDS> },
#  'senders_by_document_type_country': { ('document_type', 'country'): <SET_OF_IDS> },
#  'senders_by_document_type_process_type': { ('document_type', 'process_type'): <SET_OF_IDS> },
#  'senders_by_document_type_process_type_country': { ('document_type', 'process_type', 'country'): <SET_OF_IDS> }
#}
# our_endpoint = { "id": "PDK000592", "type": "DK:P", "country": "DK" }

def send_peppol_statistics(aggr_stats, our_endpoint, xmlsec_path, keyfile, password, certfile, test_environment):
    end_user_xml = render_peppol_end_user_statistics_xml(aggr_stats, certfile)
    transaction_xml = render_peppol_transaction_statistics_xml(aggr_stats, certfile)

    sender_id_element = generate_organization_id(ElementMaker(), lambda shorthand, tag: tag, 'Peppol', {}, "EndpointID", our_endpoint['id'], our_endpoint['type'], our_endpoint['country'])
    sender_id = sender_id_element.get('schemeID') + ':' + sender_id_element.text
    receiver_id = '9925:BE0848934496'

    for xml, schematron_xsls in [(end_user_xml, PEPPOL_END_USER_STATISTICS_SCHEMATRON_XSLS), (transaction_xml, PEPPOL_TRANSACTION_STATISTICS_SCHEMATRON_XSLS)]:
        errors = validate_peppol_document(xml, schematron_xsls)
        if errors:
            for d in errors:
                print(d)

        try:
            send_peppol_document(xml, xmlsec_path, keyfile, password, certfile, sender_id=sender_id, receiver_id=receiver_id, sender_country=our_endpoint['country'], test_environment=test_environment, timeout=20)
        except SendPeppolError as ex:
            print(f"Failed with: {ex.code} {ex}")
