import pytest

from peppol_py.statistics import clean_organization_id


@pytest.mark.parametrize(
    "organization_id,organization_id_type,country_code,expected_scheme,expected_id", [
        ("PDK000592", "DK:P", "DK", "0096", "PDK000592"),
        ("PDK000592", "0096", "DK", "0096", "PDK000592"),
        ("PDK000592", "DK:P", "GL", "0096", "PDK000592"),
        ("PDK000592", "DK:P", "FO", "0096", "PDK000592"),
        ("DK33955871", "DK:CVR", "DK", "0184", "DK33955871"),
        ("DK33955871", "DK:CVR", "GL", "0184", "DK33955871"),
        ("DK33955871", "DK:CVR", "FO", "0184", "DK33955871"),
        ("919370440", "NO:ORGNR", "NO", "0192", "919370440"),
        ("919370440", "0192", "NO", "0192", "919370440"),
        ("1234567890", "IS:KT", "IS", "0196", "1234567890"),
        ("2120000787", "SE:ORGNR", "SE", "0007", "2120000787"),
        ("1548079098355", "GLN", "US", "0088", "1548079098355"),
        ("1548079098355", "EAN", "US", "0088", "1548079098355"),
        ("CHE012345678", "CH:UIDB", "CH", "0183", "CHE012345678"),
        ("DE123456789", "DE:VAT", "DE", "9930", "DE123456789"),
        ("DE123456789", "9930", "DE", "9930", "DE123456789"),
    ]
)
def test_orgid_generation(organization_id, organization_id_type, country_code, expected_id, expected_scheme):
    # country_code currently not even required
    scheme_id, org_id = clean_organization_id(organization_id, organization_id_type)
    assert scheme_id == expected_scheme
    assert org_id == expected_id
