from pathlib import Path

import pytest
from lxml import etree

from peppol_py import validate_peppol_document

TESTS_DIR = Path(__file__).parent
SAMPLE_INVOICE = TESTS_DIR / 'data' / 'invoice.xml'
SAMPLE_CREDIT_NOTE = TESTS_DIR / 'data' / 'credit_note.xml'

INVOICE_SCHEMATRONS = ['PEPPOL-EN16931-UBL.xsl', 'CEN-EN16931-UBL.xsl']


def test_valid_invoice_passes_schematron():
    errors = validate_peppol_document(SAMPLE_INVOICE.read_bytes(), INVOICE_SCHEMATRONS)
    assert errors == []


def test_invalid_invoice_fails_schematron():
    # Remove ProfileID to trigger a required-field schematron error
    root = etree.fromstring(SAMPLE_INVOICE.read_bytes())
    profile_id = root.find('.//{*}ProfileID')
    profile_id.getparent().remove(profile_id)

    errors = validate_peppol_document(etree.tostring(root), INVOICE_SCHEMATRONS)

    assert len(errors) > 0
    for e in errors:
        assert 'text' in e
        assert 'code' in e
        assert 'severity' in e


def test_warnings_excluded_by_default():
    errors_without_warnings = validate_peppol_document(
        SAMPLE_INVOICE.read_bytes(), INVOICE_SCHEMATRONS, warnings=False
    )
    errors_with_warnings = validate_peppol_document(
        SAMPLE_INVOICE.read_bytes(), INVOICE_SCHEMATRONS, warnings=True
    )
    fatal_and_errors_only = [e for e in errors_with_warnings if e.get('severity') != 'warning']
    assert errors_without_warnings == fatal_and_errors_only


# Tests that invoices for various sender-country / endpoint-scheme combinations pass
# Schematron. We modify the minimal set of fields in the sample invoice: the supplier
# endpoint schemeID, the supplier postal country, and the buyer endpoint schemeID.
# Currency and amounts are left at EUR/matching values so the tax maths stay valid.
#
# Endpoint ID text is validated against the scheme by the Schematron (e.g. 0184 requires
# 'DK' prefix + 8 digits, 0192 requires a 9-digit mod11 number), so real IDs are needed.
# Some countries (DK via DK-R-014, IS via IS-R-002) additionally require that
# PartyLegalEntity/CompanyID carries a matching schemeID attribute.
COUNTRY_CASES = [
    ('0184', 'DK35681558', 'DK', '0088', '5798009811578', '0184'),  # DK:CVR sender, GLN receiver
    ('0192', '931540939',  'NO', '0192', '931540939',      None),    # NO:ORGNR sender and receiver
    ('0007', '2120000142', 'SE', '0007', '2120000142',     None),    # SE:ORGNR sender and receiver
    ('0196', '123456',     'IS', '0088', '5798009811578',  '0196'),  # IS:KT sender, GLN receiver
    ('0212', '0118950-3',  'FI', '0212', '2914526-2',      None),    # FI:YT sender and receiver
]


@pytest.mark.parametrize(
    "supplier_scheme,supplier_id,supplier_country,receiver_scheme,receiver_id,legal_entity_scheme",
    COUNTRY_CASES,
)
def test_invoice_country_config_passes_schematron(
    supplier_scheme, supplier_id, supplier_country,
    receiver_scheme, receiver_id, legal_entity_scheme,
):
    root = etree.fromstring(SAMPLE_INVOICE.read_bytes())

    supplier_endpoint = root.find('.//{*}AccountingSupplierParty/{*}Party/{*}EndpointID')
    supplier_endpoint.set('schemeID', supplier_scheme)
    supplier_endpoint.text = supplier_id

    root.find(
        './/{*}AccountingSupplierParty/{*}Party/{*}PostalAddress/{*}Country/{*}IdentificationCode'
    ).text = supplier_country

    receiver_endpoint = root.find('.//{*}AccountingCustomerParty/{*}Party/{*}EndpointID')
    receiver_endpoint.set('schemeID', receiver_scheme)
    receiver_endpoint.text = receiver_id

    if legal_entity_scheme:
        company_id = root.find(
            './/{*}AccountingSupplierParty/{*}Party/{*}PartyLegalEntity/{*}CompanyID'
        )
        company_id.set('schemeID', legal_entity_scheme)
        company_id.text = supplier_id

    errors = validate_peppol_document(etree.tostring(root), INVOICE_SCHEMATRONS)
    assert errors == []


# --- credit note tests -------------------------------------------------------

def test_valid_credit_note_passes_schematron():
    errors = validate_peppol_document(SAMPLE_CREDIT_NOTE.read_bytes(), INVOICE_SCHEMATRONS)
    assert errors == []


def test_invalid_credit_note_fails_schematron():
    root = etree.fromstring(SAMPLE_CREDIT_NOTE.read_bytes())
    profile_id = root.find('.//{*}ProfileID')
    profile_id.getparent().remove(profile_id)

    errors = validate_peppol_document(etree.tostring(root), INVOICE_SCHEMATRONS)
    assert len(errors) > 0


@pytest.mark.parametrize(
    "supplier_scheme,supplier_id,supplier_country,receiver_scheme,receiver_id,legal_entity_scheme",
    COUNTRY_CASES,
)
def test_credit_note_country_config_passes_schematron(
    supplier_scheme, supplier_id, supplier_country,
    receiver_scheme, receiver_id, legal_entity_scheme,
):
    root = etree.fromstring(SAMPLE_CREDIT_NOTE.read_bytes())

    supplier_endpoint = root.find('.//{*}AccountingSupplierParty/{*}Party/{*}EndpointID')
    supplier_endpoint.set('schemeID', supplier_scheme)
    supplier_endpoint.text = supplier_id

    root.find(
        './/{*}AccountingSupplierParty/{*}Party/{*}PostalAddress/{*}Country/{*}IdentificationCode'
    ).text = supplier_country

    receiver_endpoint = root.find('.//{*}AccountingCustomerParty/{*}Party/{*}EndpointID')
    receiver_endpoint.set('schemeID', receiver_scheme)
    receiver_endpoint.text = receiver_id

    if legal_entity_scheme:
        company_id = root.find(
            './/{*}AccountingSupplierParty/{*}Party/{*}PartyLegalEntity/{*}CompanyID'
        )
        company_id.set('schemeID', legal_entity_scheme)
        company_id.text = supplier_id

    errors = validate_peppol_document(etree.tostring(root), INVOICE_SCHEMATRONS)
    assert errors == []
