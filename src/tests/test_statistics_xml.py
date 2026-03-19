"""
Tests for statistics XML generation and Schematron validation.
"""
import datetime

import pytest
from lxml import etree

from peppol_py import validate_peppol_document
from peppol_py.statistics import (
    PEPPOL_END_USER_STATISTICS_SCHEMATRON_XSLS,
    PEPPOL_TRANSACTION_STATISTICS_SCHEMATRON_XSLS,
    render_peppol_end_user_statistics_xml,
    render_peppol_transaction_statistics_xml,
)

INVOICE_TYPE = (
    'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
    '::Invoice##urn:cen.eu:en16931:2017#compliant'
    '#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1'
)
CREDIT_NOTE_TYPE = (
    'urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2'
    '::CreditNote##urn:cen.eu:en16931:2017#compliant'
    '#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1'
)
PROCESS_TYPE = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
TRANSPORT_PROFILE = 'peppol-transport-as4-v2_0'
SENDER_COMMON_NAME = 'PDK000592'
RECEIVER_COMMON_NAME = 'PDK000000'

FROM_DATE = datetime.date(2025, 1, 1)
TO_DATE = datetime.date(2025, 1, 31)

DELIVERIES = [
    ('TESTSENDER1', INVOICE_TYPE, 'DK'),
    ('TESTSENDER2', INVOICE_TYPE, 'DK'),
    ('TESTSENDER2', CREDIT_NOTE_TYPE, 'DK'),
    ('TESTSENDER3', INVOICE_TYPE, 'NO'),
]


def build_aggr_stats(deliveries):
    senders = set()
    senders_by_country = {}
    senders_by_document_type_country = {}
    senders_by_document_type_process_type = {}
    senders_by_document_type_process_type_country = {}
    outgoing = 0
    outgoing_by_transport_profile = {}
    outgoing_by_rcn_dt_pt = {}

    for sender_end_user, document_type, sender_country in deliveries:
        senders.add(sender_end_user)
        senders_by_country.setdefault(sender_country, set()).add(sender_end_user)
        senders_by_document_type_country.setdefault(
            (document_type, sender_country), set()
        ).add(sender_end_user)
        senders_by_document_type_process_type.setdefault(
            (document_type, PROCESS_TYPE), set()
        ).add(sender_end_user)
        senders_by_document_type_process_type_country.setdefault(
            (document_type, PROCESS_TYPE, sender_country), set()
        ).add(sender_end_user)
        outgoing += 1
        outgoing_by_transport_profile[TRANSPORT_PROFILE] = (
            outgoing_by_transport_profile.get(TRANSPORT_PROFILE, 0) + 1
        )
        key = (RECEIVER_COMMON_NAME, document_type, PROCESS_TYPE)
        outgoing_by_rcn_dt_pt[key] = outgoing_by_rcn_dt_pt.get(key, 0) + 1

    return {
        'from_date': FROM_DATE,
        'to_date': TO_DATE,
        'outgoing': outgoing,
        'outgoing_by_transport_profile': outgoing_by_transport_profile,
        'outgoing_by_receiver_common_name_document_type_process_type': outgoing_by_rcn_dt_pt,
        'senders': senders,
        'senders_by_country': senders_by_country,
        'senders_by_document_type_country': senders_by_document_type_country,
        'senders_by_document_type_process_type': senders_by_document_type_process_type,
        'senders_by_document_type_process_type_country': senders_by_document_type_process_type_country,
    }


@pytest.fixture
def aggr_stats():
    return build_aggr_stats(DELIVERIES)


# --- end-user statistics -----------------------------------------------------

def test_end_user_statistics_passes_schematron(aggr_stats):
    xml = render_peppol_end_user_statistics_xml(aggr_stats, SENDER_COMMON_NAME)
    errors = validate_peppol_document(xml, PEPPOL_END_USER_STATISTICS_SCHEMATRON_XSLS)
    assert errors == []


def test_end_user_statistics_header(aggr_stats):
    xml = render_peppol_end_user_statistics_xml(aggr_stats, SENDER_COMMON_NAME)
    parsed = etree.fromstring(xml)

    assert parsed.findtext('.//{*}Header/{*}ReportPeriod/{*}StartDate') == FROM_DATE.isoformat()
    assert parsed.findtext('.//{*}Header/{*}ReportPeriod/{*}EndDate') == TO_DATE.isoformat()
    assert parsed.findtext('.//{*}Header/{*}ReporterID') == SENDER_COMMON_NAME


def test_end_user_statistics_full_set(aggr_stats):
    xml = render_peppol_end_user_statistics_xml(aggr_stats, SENDER_COMMON_NAME)
    parsed = etree.fromstring(xml)

    full_set = parsed.find('.//{*}FullSet')
    assert full_set.findtext('{*}SendingEndUsers') == '3'
    assert full_set.findtext('{*}ReceivingEndUsers') == '0'
    assert full_set.findtext('{*}SendingOrReceivingEndUsers') == '3'


def test_end_user_statistics_per_dt_euc(aggr_stats):
    xml = render_peppol_end_user_statistics_xml(aggr_stats, SENDER_COMMON_NAME)
    parsed = etree.fromstring(xml)

    per_dt_euc = {
        (
            e.findtext('{*}Key[@schemeID="busdox-docid-qns"]'),
            e.findtext('{*}Key[@schemeID="EndUserCountry"]'),
        ): e
        for e in parsed.findall('.//{*}Subset[@type="PerDT-EUC"]')
    }

    assert per_dt_euc[(INVOICE_TYPE, 'DK')].findtext('{*}SendingEndUsers') == '2'
    assert per_dt_euc[(INVOICE_TYPE, 'NO')].findtext('{*}SendingEndUsers') == '1'
    assert per_dt_euc[(CREDIT_NOTE_TYPE, 'DK')].findtext('{*}SendingEndUsers') == '1'


def test_end_user_statistics_per_dt_pr(aggr_stats):
    xml = render_peppol_end_user_statistics_xml(aggr_stats, SENDER_COMMON_NAME)
    parsed = etree.fromstring(xml)

    per_dt_pr = {
        e.findtext('{*}Key[@schemeID="busdox-docid-qns"]'): e
        for e in parsed.findall('.//{*}Subset[@type="PerDT-PR"]')
    }

    assert per_dt_pr[INVOICE_TYPE].findtext('{*}SendingEndUsers') == '3'
    assert per_dt_pr[CREDIT_NOTE_TYPE].findtext('{*}SendingEndUsers') == '1'


# --- transaction statistics --------------------------------------------------

def test_transaction_statistics_passes_schematron(aggr_stats):
    xml = render_peppol_transaction_statistics_xml(aggr_stats, SENDER_COMMON_NAME)
    errors = validate_peppol_document(xml, PEPPOL_TRANSACTION_STATISTICS_SCHEMATRON_XSLS)
    assert errors == []


def test_transaction_statistics_total(aggr_stats):
    xml = render_peppol_transaction_statistics_xml(aggr_stats, SENDER_COMMON_NAME)
    parsed = etree.fromstring(xml)

    total = parsed.find('.//{*}Total')
    assert total.findtext('{*}Incoming') == '0'
    assert total.findtext('{*}Outgoing') == '4'


def test_transaction_statistics_per_tp(aggr_stats):
    xml = render_peppol_transaction_statistics_xml(aggr_stats, SENDER_COMMON_NAME)
    parsed = etree.fromstring(xml)

    per_tp = parsed.find('.//{*}Subtotal[@type="PerTP"]')
    assert per_tp.findtext('{*}Outgoing') == '4'


def test_transaction_statistics_per_sp_dt_pr(aggr_stats):
    xml = render_peppol_transaction_statistics_xml(aggr_stats, SENDER_COMMON_NAME)
    parsed = etree.fromstring(xml)

    per_sp_dt_pr = {
        e.findtext('{*}Key[@schemeID="busdox-docid-qns"]'): e
        for e in parsed.findall('.//{*}Subtotal[@type="PerSP-DT-PR"]')
    }

    assert per_sp_dt_pr[INVOICE_TYPE].findtext('{*}Outgoing') == '3'
    assert per_sp_dt_pr[CREDIT_NOTE_TYPE].findtext('{*}Outgoing') == '1'
