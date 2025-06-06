<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform xmlns:error="https://doi.org/10.5281/zenodo.1495494#error"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:sch="http://purl.oclc.org/dsdl/schematron"
               xmlns:schxslt="https://doi.org/10.5281/zenodo.1495494"
               xmlns:schxslt-api="https://doi.org/10.5281/zenodo.1495494#api"
               xmlns:tsr="urn:fdc:peppol:transaction-statistics-report:1.0"
               xmlns:xs="http://www.w3.org/2001/XMLSchema"
               xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
               version="2.0">
   <rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/"
                    xmlns:dct="http://purl.org/dc/terms/"
                    xmlns:skos="http://www.w3.org/2004/02/skos/core#">
      <dct:creator>
         <dct:Agent>
            <skos:prefLabel>SchXslt/1.9.5 SAXON/HE 12.4.2</skos:prefLabel>
            <schxslt.compile.typed-variables xmlns="https://doi.org/10.5281/zenodo.1495494#">true</schxslt.compile.typed-variables>
         </dct:Agent>
      </dct:creator>
      <dct:created>2024-05-13T10:15:11.302344+02:00</dct:created>
   </rdf:Description>
   <xsl:output indent="yes"/>
   <xsl:variable name="cl_iso3166"
                 select="' 1A AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH EL ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS XI XK YE YT ZA ZM ZW ZZ '"/>
   <xsl:variable name="cl_spidtype" select="' CertSubjectCN '"/>
   <xsl:variable name="cl_subtotalType" select="' PerTP PerSP-DT-PR PerSP-DT-PR-CC '"/>
   <xsl:variable name="re_seatid" select="'^P[A-Z]{2}[0-9]{6}$'"/>
   <xsl:template match="root()">
      <xsl:variable name="metadata" as="element()?">
         <svrl:metadata xmlns:dct="http://purl.org/dc/terms/"
                        xmlns:skos="http://www.w3.org/2004/02/skos/core#"
                        xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
            <dct:creator>
               <dct:Agent>
                  <skos:prefLabel>
                     <xsl:value-of separator="/"
                                   select="(system-property('xsl:product-name'), system-property('xsl:product-version'))"/>
                  </skos:prefLabel>
               </dct:Agent>
            </dct:creator>
            <dct:created>
               <xsl:value-of select="current-dateTime()"/>
            </dct:created>
            <dct:source>
               <rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/">
                  <dct:creator>
                     <dct:Agent>
                        <skos:prefLabel>SchXslt/1.9.5 SAXON/HE 12.4.2</skos:prefLabel>
                        <schxslt.compile.typed-variables xmlns="https://doi.org/10.5281/zenodo.1495494#">true</schxslt.compile.typed-variables>
                     </dct:Agent>
                  </dct:creator>
                  <dct:created>2024-05-13T10:15:11.302344+02:00</dct:created>
               </rdf:Description>
            </dct:source>
         </svrl:metadata>
      </xsl:variable>
      <xsl:variable name="report" as="element(schxslt:report)">
         <schxslt:report>
            <xsl:call-template name="d12e9"/>
         </schxslt:report>
      </xsl:variable>
      <xsl:variable name="schxslt:report" as="node()*">
         <xsl:sequence select="$metadata"/>
         <xsl:for-each select="$report/schxslt:document">
            <xsl:for-each select="schxslt:pattern">
               <xsl:sequence select="node()"/>
               <xsl:sequence select="../schxslt:rule[@pattern = current()/@id]/node()"/>
            </xsl:for-each>
         </xsl:for-each>
      </xsl:variable>
      <svrl:schematron-output xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                              schemaVersion="ISO19757-3"
                              title="OpenPeppol Transaction Statistics Reporting">
         <svrl:text id="about">
    This is the Schematron for the Peppol Transaction Statistics Reporting
    This is based on the "Internal Regulations" document,
      chapter 4.4 "Service Provider Reporting on Transaction Statistics"

    Author:
      Philip Helger
      Muhammet Yildiz

    History:
      v1.0.4
        2023-11-02, Philip Helger - add country code `ZZ` as an allowed one
      v1.0.3
        2023-10-12, Muhammet Yildiz - replaced $xyz values with `value-of select ="$xyz"` in the messages
      v1.0.2
        2023-09-18, Philip Helger - re-enabled SCH-TSR-11
                                    fixed test and level of SCH-TSR-12
      v1.0.1
        2023-03-14, Philip Helger - removed rule SCH-TSR-13; added rule SCH-TSR-43 
      v1.0.0
        2022-11-14, Muhammet Yildiz, Philip Helger - updates after the review
        2022-04-21, Philip Helger - initial version
  </svrl:text>
         <svrl:ns-prefix-in-attribute-values prefix="tsr" uri="urn:fdc:peppol:transaction-statistics-report:1.0"/>
         <xsl:sequence select="$schxslt:report"/>
      </svrl:schematron-output>
   </xsl:template>
   <xsl:template match="text() | @*" mode="#all" priority="-10"/>
   <xsl:template match="/" mode="#all" priority="-10">
      <xsl:apply-templates mode="#current" select="node()"/>
   </xsl:template>
   <xsl:template match="*" mode="#all" priority="-10">
      <xsl:apply-templates mode="#current" select="@*"/>
      <xsl:apply-templates mode="#current" select="node()"/>
   </xsl:template>
   <xsl:template name="d12e9">
      <schxslt:document>
         <schxslt:pattern id="d12e9">
            <xsl:if test="exists(base-uri(root()))">
               <xsl:attribute name="documents" select="base-uri(root())"/>
            </xsl:if>
            <xsl:for-each select="root()">
               <svrl:active-pattern xmlns:svrl="http://purl.oclc.org/dsdl/svrl" name="default" id="default">
                  <xsl:attribute name="documents" select="base-uri(.)"/>
               </svrl:active-pattern>
            </xsl:for-each>
         </schxslt:pattern>
         <xsl:apply-templates mode="d12e9" select="root()"/>
      </schxslt:document>
   </xsl:template>
   <xsl:template match="/tsr:TransactionStatisticsReport" priority="8" mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:variable name="total" select="tsr:Total/tsr:Incoming + tsr:Total/tsr:Outgoing"/>
      <xsl:variable name="empty" select="$total = 0"/>
      <xsl:variable name="name_tp" select="'Transport Protocol ID'"/>
      <xsl:variable name="name_spdtpr"
                    select="'Service Provider ID, Dataset Type ID and Process ID'"/>
      <xsl:variable name="name_spdtprcc"
                    select="'Service Provider ID, Dataset Type ID, Process ID, Sender Country and Receiver Country'"/>
      <xsl:variable name="cc_empty" select="$empty or tsr:Total/tsr:Incoming = 0"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/tsr:TransactionStatisticsReport" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport</xsl:attribute>
               </svrl:suppressed-rule>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="$schxslt:patterns-matched"/>
            </xsl:next-match>
         </xsl:when>
         <xsl:otherwise>
            <schxslt:rule pattern="d12e9">
               <svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(normalize-space(tsr:CustomizationID) = 'urn:fdc:peppol.eu:edec:trns:transaction-statistics-reporting:1.0')">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-01">
                     <xsl:attribute name="test">normalize-space(tsr:CustomizationID) = 'urn:fdc:peppol.eu:edec:trns:transaction-statistics-reporting:1.0'</xsl:attribute>
                     <svrl:text>[SCH-TSR-01] The customization ID MUST use the value 'urn:fdc:peppol.eu:edec:trns:transaction-statistics-reporting:1.0'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(normalize-space(tsr:ProfileID) = 'urn:fdc:peppol.eu:edec:bis:reporting:1.0')">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-02">
                     <xsl:attribute name="test">normalize-space(tsr:ProfileID) = 'urn:fdc:peppol.eu:edec:bis:reporting:1.0'</xsl:attribute>
                     <svrl:text>[SCH-TSR-02] The profile ID MUST use the value 'urn:fdc:peppol.eu:edec:bis:reporting:1.0'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or tsr:Subtotal[normalize-space(@type) = 'PerTP'])">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-03">
                     <xsl:attribute name="test">$empty or tsr:Subtotal[normalize-space(@type) = 'PerTP']</xsl:attribute>
                     <svrl:text>[SCH-TSR-03] The subtotals per <xsl:value-of select="$name_tp"/> MUST exist</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Incoming) = tsr:Total/tsr:Incoming)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-04">
                     <xsl:attribute name="test">$empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Incoming) = tsr:Total/tsr:Incoming</xsl:attribute>
                     <svrl:text>[SCH-TSR-04] The sum of all subtotals per <xsl:value-of select="$name_tp"/> incoming MUST match the total incoming count</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Outgoing) = tsr:Total/tsr:Outgoing)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-05">
                     <xsl:attribute name="test">$empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Outgoing) = tsr:Total/tsr:Outgoing</xsl:attribute>
                     <svrl:text>[SCH-TSR-05] The sum of all subtotals per <xsl:value-of select="$name_tp"/> outgoing MUST match the total outgoing count</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $key in (tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Key) satisfies                                                     count(tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Key[concat(normalize-space(@schemeID),'::',normalize-space(.)) =                                                                                                                  concat(normalize-space($key/@schemeID),'::',normalize-space($key))]) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-06">
                     <xsl:attribute name="test">every $key in (tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Key) satisfies                                                     count(tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Key[concat(normalize-space(@schemeID),'::',normalize-space(.)) =                                                                                                                  concat(normalize-space($key/@schemeID),'::',normalize-space($key))]) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-06] Each <xsl:value-of select="$name_tp"/> MUST occur only once.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR'])">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-07">
                     <xsl:attribute name="test">$empty or tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']</xsl:attribute>
                     <svrl:text>[SCH-TSR-07] The subtotals per <xsl:value-of select="$name_spdtpr"/> MUST exist</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']/tsr:Incoming) = tsr:Total/tsr:Incoming)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-08">
                     <xsl:attribute name="test">$empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']/tsr:Incoming) = tsr:Total/tsr:Incoming</xsl:attribute>
                     <svrl:text>[SCH-TSR-08] The sum of all subtotals per <xsl:value-of select="$name_spdtpr"/> incoming MUST match the total incoming count</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']/tsr:Outgoing) = tsr:Total/tsr:Outgoing)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-09">
                     <xsl:attribute name="test">$empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']/tsr:Outgoing) = tsr:Total/tsr:Outgoing</xsl:attribute>
                     <svrl:text>[SCH-TSR-09] The sum of all subtotals per <xsl:value-of select="$name_spdtpr"/> outgoing MUST match the total outgoing count</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']),                                                        $stsp in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'SP']),                                                        $stdt in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                        $stpr in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'PR'])  satisfies                                                    count(tsr:Subtotal[normalize-space(@type) ='PerSP-DT-PR'][every $sp in (tsr:Key[normalize-space(@metaSchemeID) = 'SP']),                                                                                                                    $dt in (tsr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                    $pr in (tsr:Key[normalize-space(@metaSchemeID) = 'PR']) satisfies                                                                                                              concat(normalize-space($sp/@schemeID),'::',normalize-space($sp),'::',                                                                                                                     normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                     normalize-space($pr/@schemeID),'::',normalize-space($pr)) =                                                                                                              concat(normalize-space($stsp/@schemeID),'::',normalize-space($stsp),'::',                                                                                                                     normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                     normalize-space($stpr/@schemeID),'::',normalize-space($stpr))]) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-10">
                     <xsl:attribute name="test">every $st in (tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']),                                                        $stsp in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'SP']),                                                        $stdt in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                        $stpr in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'PR'])  satisfies                                                    count(tsr:Subtotal[normalize-space(@type) ='PerSP-DT-PR'][every $sp in (tsr:Key[normalize-space(@metaSchemeID) = 'SP']),                                                                                                                    $dt in (tsr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                    $pr in (tsr:Key[normalize-space(@metaSchemeID) = 'PR']) satisfies                                                                                                              concat(normalize-space($sp/@schemeID),'::',normalize-space($sp),'::',                                                                                                                     normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                     normalize-space($pr/@schemeID),'::',normalize-space($pr)) =                                                                                                              concat(normalize-space($stsp/@schemeID),'::',normalize-space($stsp),'::',                                                                                                                     normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                     normalize-space($stpr/@schemeID),'::',normalize-space($stpr))]) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-10] Each combination of <xsl:value-of select="$name_spdtpr"/> MUST occur only once.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($cc_empty or tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC'])">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-11">
                     <xsl:attribute name="test">$cc_empty or tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC']</xsl:attribute>
                     <svrl:text>[SCH-TSR-11] The subtotals per <xsl:value-of select="$name_spdtprcc"/> MUST exist</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($cc_empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC']/tsr:Incoming) = tsr:Total/tsr:Incoming)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-12">
                     <xsl:attribute name="test">$cc_empty or sum(tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC']/tsr:Incoming) = tsr:Total/tsr:Incoming</xsl:attribute>
                     <svrl:text>[SCH-TSR-12] The sum of all subtotals per <xsl:value-of select="$name_spdtprcc"/> incoming MUST match the total incoming count</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC']),                                                        $stsp in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'SP']),                                                        $stdt in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                        $stpr in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'PR']),                                                        $stsc in ($st/tsr:Key[normalize-space(@schemeID) = 'SenderCountry']),                                                        $strc in ($st/tsr:Key[normalize-space(@schemeID) = 'ReceiverCountry']) satisfies                                                     count(tsr:Subtotal[normalize-space(@type) ='PerSP-DT-PR-CC'][every $sp in (tsr:Key[normalize-space(@metaSchemeID) = 'SP']),                                                                                                                       $dt in (tsr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                       $pr in (tsr:Key[normalize-space(@metaSchemeID) = 'PR']),                                                                                                                       $sc in (tsr:Key[normalize-space(@schemeID) = 'SenderCountry']),                                                                                                                       $rc in (tsr:Key[normalize-space(@schemeID) = 'ReceiverCountry']) satisfies                                                                                                                 concat(normalize-space($sp/@schemeID),'::',normalize-space($sp),'::',                                                                                                                        normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                        normalize-space($pr/@schemeID),'::',normalize-space($pr),'::',                                                                                                                        normalize-space($sc),'::',                                                                                                                        normalize-space($rc)) =                                                                                                                  concat(normalize-space($stsp/@schemeID),'::',normalize-space($stsp),'::',                                                                                                                        normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                        normalize-space($stpr/@schemeID),'::',normalize-space($stpr),'::',                                                                                                                        normalize-space($stsc),'::',                                                                                                                        normalize-space($strc))]) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-14">
                     <xsl:attribute name="test">every $st in (tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC']),                                                        $stsp in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'SP']),                                                        $stdt in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                        $stpr in ($st/tsr:Key[normalize-space(@metaSchemeID) = 'PR']),                                                        $stsc in ($st/tsr:Key[normalize-space(@schemeID) = 'SenderCountry']),                                                        $strc in ($st/tsr:Key[normalize-space(@schemeID) = 'ReceiverCountry']) satisfies                                                     count(tsr:Subtotal[normalize-space(@type) ='PerSP-DT-PR-CC'][every $sp in (tsr:Key[normalize-space(@metaSchemeID) = 'SP']),                                                                                                                       $dt in (tsr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                       $pr in (tsr:Key[normalize-space(@metaSchemeID) = 'PR']),                                                                                                                       $sc in (tsr:Key[normalize-space(@schemeID) = 'SenderCountry']),                                                                                                                       $rc in (tsr:Key[normalize-space(@schemeID) = 'ReceiverCountry']) satisfies                                                                                                                 concat(normalize-space($sp/@schemeID),'::',normalize-space($sp),'::',                                                                                                                        normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                        normalize-space($pr/@schemeID),'::',normalize-space($pr),'::',                                                                                                                        normalize-space($sc),'::',                                                                                                                        normalize-space($rc)) =                                                                                                                  concat(normalize-space($stsp/@schemeID),'::',normalize-space($stsp),'::',                                                                                                                        normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                        normalize-space($stpr/@schemeID),'::',normalize-space($stpr),'::',                                                                                                                        normalize-space($stsc),'::',                                                                                                                        normalize-space($strc))]) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-14] Each combination of <xsl:value-of select="$name_spdtprcc"/> MUST occur only once.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Subtotal[normalize-space(@type) !='PerTP' and                                                                      normalize-space(@type) !='PerSP-DT-PR' and                                                                      normalize-space(@type) !='PerSP-DT-PR-CC']) = 0)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-39">
                     <xsl:attribute name="test">count(tsr:Subtotal[normalize-space(@type) !='PerTP' and                                                                      normalize-space(@type) !='PerSP-DT-PR' and                                                                      normalize-space(@type) !='PerSP-DT-PR-CC']) = 0</xsl:attribute>
                     <svrl:text>[SCH-TSR-39] Only allowed subtotal types MUST be used.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="($schxslt:patterns-matched, 'd12e9')"/>
            </xsl:next-match>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   <xsl:template match="/tsr:TransactionStatisticsReport/tsr:Header"
                 priority="7"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/tsr:TransactionStatisticsReport/tsr:Header" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Header</xsl:attribute>
               </svrl:suppressed-rule>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="$schxslt:patterns-matched"/>
            </xsl:next-match>
         </xsl:when>
         <xsl:otherwise>
            <schxslt:rule pattern="d12e9">
               <svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Header</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(matches(normalize-space(tsr:ReportPeriod/tsr:StartDate), '^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$'))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-40">
                     <xsl:attribute name="test">matches(normalize-space(tsr:ReportPeriod/tsr:StartDate), '^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$')</xsl:attribute>
                     <svrl:text>[SCH-TSR-40] The report period start date (<xsl:value-of select="normalize-space(tsr:ReportPeriod/tsr:StartDate)"/>) MUST NOT contain timezone information</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(matches(normalize-space(tsr:ReportPeriod/tsr:EndDate), '^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$'))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-41">
                     <xsl:attribute name="test">matches(normalize-space(tsr:ReportPeriod/tsr:EndDate), '^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$')</xsl:attribute>
                     <svrl:text>[SCH-TSR-41] The report period end date (<xsl:value-of select="normalize-space(tsr:ReportPeriod/tsr:EndDate)"/>) MUST NOT contain timezone information</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(tsr:ReportPeriod/tsr:EndDate &gt;= tsr:ReportPeriod/tsr:StartDate)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-42">
                     <xsl:attribute name="test">tsr:ReportPeriod/tsr:EndDate &gt;= tsr:ReportPeriod/tsr:StartDate</xsl:attribute>
                     <svrl:text>[SCH-TSR-42] The report period start date (<xsl:value-of select="normalize-space(tsr:ReportPeriod/tsr:StartDate)"/>) MUST NOT be after the report period end date (<xsl:value-of select="normalize-space(tsr:ReportPeriod/tsr:EndDate)"/>)</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="($schxslt:patterns-matched, 'd12e9')"/>
            </xsl:next-match>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   <xsl:template match="/tsr:TransactionStatisticsReport/tsr:Header/tsr:ReporterID"
                 priority="6"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/tsr:TransactionStatisticsReport/tsr:Header/tsr:ReporterID" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Header/tsr:ReporterID</xsl:attribute>
               </svrl:suppressed-rule>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="$schxslt:patterns-matched"/>
            </xsl:next-match>
         </xsl:when>
         <xsl:otherwise>
            <schxslt:rule pattern="d12e9">
               <svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Header/tsr:ReporterID</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(normalize-space(.) != '')">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-16">
                     <xsl:attribute name="test">normalize-space(.) != ''</xsl:attribute>
                     <svrl:text>[SCH-TSR-16] The reporter ID MUST be present</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(not(contains(normalize-space(@schemeID), ' ')) and                                               contains($cl_spidtype, concat(' ', normalize-space(@schemeID), ' ')))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-17">
                     <xsl:attribute name="test">not(contains(normalize-space(@schemeID), ' ')) and                                               contains($cl_spidtype, concat(' ', normalize-space(@schemeID), ' '))</xsl:attribute>
                     <svrl:text>[SCH-TSR-17] The Reporter ID scheme (<xsl:value-of select="normalize-space(@schemeID)"/>) MUST be coded according to the code list</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not((@schemeID='CertSubjectCN' and                                                    matches(normalize-space(.), $re_seatid)) or                                                   not(@schemeID='CertSubjectCN'))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-18">
                     <xsl:attribute name="test">(@schemeID='CertSubjectCN' and                                                    matches(normalize-space(.), $re_seatid)) or                                                   not(@schemeID='CertSubjectCN')</xsl:attribute>
                     <svrl:text>[SCH-TSR-18] The layout of the certificate subject CN (<xsl:value-of select="normalize-space(.)"/>) is not a valid Peppol Seat ID</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="($schxslt:patterns-matched, 'd12e9')"/>
            </xsl:next-match>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   <xsl:template match="/tsr:TransactionStatisticsReport/tsr:Subtotal/tsr:Key[normalize-space(@schemeID) = 'CertSubjectCN']"
                 priority="5"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/tsr:TransactionStatisticsReport/tsr:Subtotal/tsr:Key[normalize-space(@schemeID) = 'CertSubjectCN']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal/tsr:Key[normalize-space(@schemeID) = 'CertSubjectCN']</xsl:attribute>
               </svrl:suppressed-rule>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="$schxslt:patterns-matched"/>
            </xsl:next-match>
         </xsl:when>
         <xsl:otherwise>
            <schxslt:rule pattern="d12e9">
               <svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal/tsr:Key[normalize-space(@schemeID) = 'CertSubjectCN']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(matches(normalize-space(.), $re_seatid))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-19">
                     <xsl:attribute name="test">matches(normalize-space(.), $re_seatid)</xsl:attribute>
                     <svrl:text>[SCH-TSR-19] The layout of the certificate subject CN is not a valid Peppol Seat ID</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="($schxslt:patterns-matched, 'd12e9')"/>
            </xsl:next-match>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   <xsl:template match="/tsr:TransactionStatisticsReport/tsr:Subtotal/tsr:Key[normalize-space(@schemeID) = 'SenderCountry' or                                                                           normalize-space(@schemeID) = 'ReceiverCountry']"
                 priority="4"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/tsr:TransactionStatisticsReport/tsr:Subtotal/tsr:Key[normalize-space(@schemeID) = 'SenderCountry' or normalize-space(@schemeID) = 'ReceiverCountry']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal/tsr:Key[normalize-space(@schemeID) = 'SenderCountry' or                                                                           normalize-space(@schemeID) = 'ReceiverCountry']</xsl:attribute>
               </svrl:suppressed-rule>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="$schxslt:patterns-matched"/>
            </xsl:next-match>
         </xsl:when>
         <xsl:otherwise>
            <schxslt:rule pattern="d12e9">
               <svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal/tsr:Key[normalize-space(@schemeID) = 'SenderCountry' or                                                                           normalize-space(@schemeID) = 'ReceiverCountry']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(not(contains(normalize-space(.), ' ')) and                                                      contains($cl_iso3166, concat(' ', normalize-space(.), ' ')))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-20">
                     <xsl:attribute name="test">not(contains(normalize-space(.), ' ')) and                                                      contains($cl_iso3166, concat(' ', normalize-space(.), ' '))</xsl:attribute>
                     <svrl:text>[SCH-TSR-20] The country code MUST be coded with ISO code ISO 3166-1 alpha-2. Nevertheless, Greece may use the code 'EL', Kosovo may use the code 'XK' or '1A'.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="($schxslt:patterns-matched, 'd12e9')"/>
            </xsl:next-match>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   <xsl:template match="/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerTP']"
                 priority="3"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:variable name="name" select="'The subtotal per Transport Protocol ID'"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerTP']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerTP']</xsl:attribute>
               </svrl:suppressed-rule>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="$schxslt:patterns-matched"/>
            </xsl:next-match>
         </xsl:when>
         <xsl:otherwise>
            <schxslt:rule pattern="d12e9">
               <svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerTP']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(count(tsr:Key) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-21">
                     <xsl:attribute name="test">count(tsr:Key) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-21] <xsl:value-of select="$name"/> MUST have one Key element</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'TP']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-22">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'TP']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-22] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'TP'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@schemeID) = 'Peppol']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-23">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@schemeID) = 'Peppol']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-23] <xsl:value-of select="$name"/> MUST have one Key element with the scheme ID 'Peppol'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="($schxslt:patterns-matched, 'd12e9')"/>
            </xsl:next-match>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   <xsl:template match="/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']"
                 priority="2"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:variable name="name"
                    select="'The subtotal per Service Provider ID, Dataset Type ID and Process ID'"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']</xsl:attribute>
               </svrl:suppressed-rule>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="$schxslt:patterns-matched"/>
            </xsl:next-match>
         </xsl:when>
         <xsl:otherwise>
            <schxslt:rule pattern="d12e9">
               <svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(count(tsr:Key) = 3)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-24">
                     <xsl:attribute name="test">count(tsr:Key) = 3</xsl:attribute>
                     <svrl:text>[SCH-TSR-24] <xsl:value-of select="$name"/> MUST have three Key elements</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'SP']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-25">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'SP']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-25] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'SP'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-26">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-26] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'DT'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'PR']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-27">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'PR']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-27] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'PR'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $x in (tsr:Key[normalize-space(@metaSchemeID) = 'SP']) satisfies                                                    not(contains(normalize-space($x/@schemeID), ' ')) and                                                     contains($cl_spidtype, concat(' ', normalize-space($x/@schemeID), ' ')))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-28">
                     <xsl:attribute name="test">every $x in (tsr:Key[normalize-space(@metaSchemeID) = 'SP']) satisfies                                                    not(contains(normalize-space($x/@schemeID), ' ')) and                                                     contains($cl_spidtype, concat(' ', normalize-space($x/@schemeID), ' '))</xsl:attribute>
                     <svrl:text>[SCH-TSR-28] <xsl:value-of select="$name"/> MUST have one SP Key element with the scheme ID coded according to the code list</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="($schxslt:patterns-matched, 'd12e9')"/>
            </xsl:next-match>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   <xsl:template match="/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC']"
                 priority="1"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:variable name="name"
                    select="'The subtotal per Service Provider ID, Dataset Type ID, Sender Country and Receiver Country'"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC']</xsl:attribute>
               </svrl:suppressed-rule>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="$schxslt:patterns-matched"/>
            </xsl:next-match>
         </xsl:when>
         <xsl:otherwise>
            <schxslt:rule pattern="d12e9">
               <svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal[normalize-space(@type) = 'PerSP-DT-PR-CC']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(count(tsr:Key) = 5)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-29">
                     <xsl:attribute name="test">count(tsr:Key) = 5</xsl:attribute>
                     <svrl:text>[SCH-TSR-29] <xsl:value-of select="$name"/> MUST have five Key elements</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'SP']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-30">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'SP']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-30] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'SP'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-31">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-31] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'DT'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'PR']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-32">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'PR']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-32] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'PR'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'CC']) = 2)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-33">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'CC']) = 2</xsl:attribute>
                     <svrl:text>[SCH-TSR-33] <xsl:value-of select="$name"/> MUST have two Key elements with the meta scheme ID 'CC'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $x in (tsr:Key[normalize-space(@metaSchemeID) = 'SP']) satisfies                                                    not(contains(normalize-space($x/@schemeID), ' ')) and                                                     contains($cl_spidtype, concat(' ', normalize-space($x/@schemeID), ' ')))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-34">
                     <xsl:attribute name="test">every $x in (tsr:Key[normalize-space(@metaSchemeID) = 'SP']) satisfies                                                    not(contains(normalize-space($x/@schemeID), ' ')) and                                                     contains($cl_spidtype, concat(' ', normalize-space($x/@schemeID), ' '))</xsl:attribute>
                     <svrl:text>[SCH-TSR-34] <xsl:value-of select="$name"/> MUST have one SP Key element with the scheme ID coded according to the code list</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'SenderCountry']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-35">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'SenderCountry']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-35] <xsl:value-of select="$name"/> MUST have one CC Key element with the scheme ID 'SenderCountry'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(tsr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'ReceiverCountry']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-36">
                     <xsl:attribute name="test">count(tsr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'ReceiverCountry']) = 1</xsl:attribute>
                     <svrl:text>[SCH-TSR-36] <xsl:value-of select="$name"/> MUST have one CC Key element with the scheme ID 'ReceiverCountry'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(tsr:Outgoing = 0)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-43">
                     <xsl:attribute name="test">tsr:Outgoing = 0</xsl:attribute>
                     <svrl:text>[SCH-TSR-43] <xsl:value-of select="$name"/> MUST have a 'Outgoing' value of '0' because that data cannot be gathered</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="($schxslt:patterns-matched, 'd12e9')"/>
            </xsl:next-match>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   <xsl:template match="/tsr:TransactionStatisticsReport/tsr:Subtotal"
                 priority="0"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/tsr:TransactionStatisticsReport/tsr:Subtotal" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal</xsl:attribute>
               </svrl:suppressed-rule>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="$schxslt:patterns-matched"/>
            </xsl:next-match>
         </xsl:when>
         <xsl:otherwise>
            <schxslt:rule pattern="d12e9">
               <svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/tsr:TransactionStatisticsReport/tsr:Subtotal</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(not(contains(normalize-space(@type), ' ')) and                                                  contains($cl_subtotalType, concat(' ', normalize-space(@type), ' ')))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-TSR-37">
                     <xsl:attribute name="test">not(contains(normalize-space(@type), ' ')) and                                                  contains($cl_subtotalType, concat(' ', normalize-space(@type), ' '))</xsl:attribute>
                     <svrl:text>[SCH-TSR-37] The Subtotal type (<xsl:value-of select="normalize-space(@type)"/>) MUST be coded according to the code list</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
            </schxslt:rule>
            <xsl:next-match>
               <xsl:with-param name="schxslt:patterns-matched"
                               as="xs:string*"
                               select="($schxslt:patterns-matched, 'd12e9')"/>
            </xsl:next-match>
         </xsl:otherwise>
      </xsl:choose>
   </xsl:template>
   <xsl:function name="schxslt:location" as="xs:string">
      <xsl:param name="node" as="node()"/>
      <xsl:variable name="segments" as="xs:string*">
         <xsl:for-each select="($node/ancestor-or-self::node())">
            <xsl:variable name="position">
               <xsl:number level="single"/>
            </xsl:variable>
            <xsl:choose>
               <xsl:when test=". instance of element()">
                  <xsl:value-of select="concat('Q{', namespace-uri(.), '}', local-name(.), '[', $position, ']')"/>
               </xsl:when>
               <xsl:when test=". instance of attribute()">
                  <xsl:value-of select="concat('@Q{', namespace-uri(.), '}', local-name(.))"/>
               </xsl:when>
               <xsl:when test=". instance of processing-instruction()">
                  <xsl:value-of select="concat('processing-instruction(&#34;', name(.), '&#34;)[', $position, ']')"/>
               </xsl:when>
               <xsl:when test=". instance of comment()">
                  <xsl:value-of select="concat('comment()[', $position, ']')"/>
               </xsl:when>
               <xsl:when test=". instance of text()">
                  <xsl:value-of select="concat('text()[', $position, ']')"/>
               </xsl:when>
               <xsl:otherwise/>
            </xsl:choose>
         </xsl:for-each>
      </xsl:variable>
      <xsl:value-of select="concat('/', string-join($segments, '/'))"/>
   </xsl:function>
</xsl:transform>
