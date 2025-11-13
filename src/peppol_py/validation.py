import os
from pathlib import Path
from typing import List

from lxml import etree
from saxonche import PySaxonProcessor


def validate_peppol_document(
    document_content: bytes,
    schematron_xsls: List[str],
    remove_namespaces_from_errors=True,
    warnings=False
) -> List[dict]:
    """
    Validate peppol document. Returns a list of errors.

    ``document_content`` (bytes): XML content

    ``schematron_xsls`` (list of str): Either full paths to xsl files, or names of xsl files shipped with peppol_py.

    ``remove_namespaces_from_errors`` (bool): For shorter output of error messages.

    ``warnings`` (bool): If ``True``, warnings will be returned as well out.
    """
    errors = []
    # we need saxonche (SaxonC Home Edition) because lxml (libxsl)
    # only works with XSLT 1.0, and the Schematron is written in XSLT
    # 2.0
    with PySaxonProcessor(license=False) as proc:
        # Prevent XXE: disallow access to any type of URL
        proc.set_configuration_property("http://saxon.sf.net/feature/allowedProtocols", "")
        for validation_xsl_file in schematron_xsls:
            if not os.path.exists(validation_xsl_file):
                # Resolve internal files
                validation_xsl_file = str(Path(__file__).parent / 'data' / 'sendpeppol-schematron' / validation_xsl_file)
            xsltproc = proc.new_xslt30_processor()
            document = proc.parse_xml(xml_text=document_content.decode())
            executable = xsltproc.compile_stylesheet(stylesheet_file=validation_xsl_file)
            output = executable.transform_to_string(xdm_node=document)

            parsed_output = etree.fromstring(output.encode())
            for e in parsed_output.findall('{http://purl.oclc.org/dsdl/svrl}failed-assert'):
                location = e.get('location')
                if remove_namespaces_from_errors:
                    import re
                    location = re.sub('Q{.+?}', '', location)

                severity = e.get('flag')
                if severity == 'warning' and not warnings:
                    continue

                errors.append({
                    'text': e.findtext('{*}text'),
                    'code': e.get('id'),
                    'severity': severity,
                    'test': e.get('test'),
                    'location': location,
                })

    return errors


def convert_schematron_file_to_xsl_file(input_sch_file, output_xsl_file, schxslt_path):
    # This function can be used to preprocess Schematron files. It
    # should only be used when there's a new release of the Schematron
    # file. schxscl_path is path to unzipped schxslt-*-xslt-only.zip -
    # the schxscl pipeline-for-svrl.xsl is used to convert the .sch
    # Schematron file to a regular .xls file.
    #
    # E.g. in a shell:
    # from utils.sendpeppol import convert_schematron_file_to_xsl_file
    # cd utils/sendpeppol-schematron
    # convert_schematron_file_to_xsl_file('PEPPOL-EN16931-UBL.sch', 'PEPPOL-EN16931-UBL.xsl', 'schxslt-1.9.5/')

    with open(input_sch_file, 'r') as f:
        input_text = f.read()

    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        document = proc.parse_xml(xml_text=input_text)
        executable = xsltproc.compile_stylesheet(stylesheet_file=os.path.join(schxslt_path, '2.0/pipeline-for-svrl.xsl'))
        output_text = executable.transform_to_string(xdm_node=document)

    with open(output_xsl_file, 'w') as f:
        f.write(output_text)
