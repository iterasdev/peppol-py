<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform xmlns:error="https://doi.org/10.5281/zenodo.1495494#error"
               xmlns:eusr="urn:fdc:peppol:end-user-statistics-report:1.1"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:sch="http://purl.oclc.org/dsdl/schematron"
               xmlns:schxslt="https://doi.org/10.5281/zenodo.1495494"
               xmlns:schxslt-api="https://doi.org/10.5281/zenodo.1495494#api"
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
      <dct:created>2024-05-13T10:14:51.13967+02:00</dct:created>
   </rdf:Description>
   <xsl:output indent="yes"/>
   <xsl:variable name="cl_iso3166"
                 select="' 1A AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH EL ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS XI XK YE YT ZA ZM ZW '"/>
   <xsl:variable name="cl_spidtype" select="' CertSubjectCN '"/>
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
                  <dct:created>2024-05-13T10:14:51.13967+02:00</dct:created>
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
                              title="OpenPeppol End User Statistics Report">
         <svrl:text id="about">
    This is the Schematron for the Peppol End User Statistics Reports.
    This is based on the "Internal Regulations" document,
      chapter 4.3 "Service Provider Reporting about End Users"

    Author:
      Philip Helger
      Muhammet Yildiz

    History
      EUSR 1.1.4
        2023-11-10, Philip Helger - reverted the changes from 1.1.3 - the country code `ZZ` is only allowed in TSR
      EUSR 1.1.3
        2023-11-02, Philip Helger - add country code `ZZ` as an allowed one
      EUSR 1.1.2
        2023-10-12, Muhammet Yildiz - replaced $xyz values with `value-of select ="$xyz"` in the messages
      EUSR 1.1.0
        2023-09-18, Philip Helger - using function "max" in rules 03, 04, 22 to fix an issue if the same value appears more then once
                                    explicitly added "xs:integer" casts where necessary
        2023-06-29, Muhammet Yildiz - updates related to changing "PerDTPRCC" to "PerDTPREUC". Rules 28,31,32 removed. Rules 14, 23, 26, 27, 29, 30 modified
      EUSR 1.0.1
        2023-06-23, Philip Helger - hotfix for new subsets "PerEUC" and "PerDT-EUC". Added new rules SCH-EUSR-37 to SCH-EUSR-47
      EUSR 1.0.0
        2023-03-06, Philip Helger - updates after second review
      EUSR RC2
        2022-11-14, Muhammet Yildiz, Philip Helger - updates after the first review
      EUR RC1
        2022-04-15, Philip Helger - initial version
  </svrl:text>
         <svrl:ns-prefix-in-attribute-values prefix="eusr" uri="urn:fdc:peppol:end-user-statistics-report:1.1"/>
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
   <xsl:template match="/eusr:EndUserStatisticsReport" priority="7" mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:variable name="total"
                    select="xs:integer(eusr:FullSet/eusr:SendingEndUsers) + xs:integer(eusr:FullSet/eusr:ReceivingEndUsers)"/>
      <xsl:variable name="empty" select="$total = 0"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/eusr:EndUserStatisticsReport" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport</xsl:attribute>
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
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(normalize-space(eusr:CustomizationID) = 'urn:fdc:peppol.eu:edec:trns:end-user-statistics-report:1.1')">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-01">
                     <xsl:attribute name="test">normalize-space(eusr:CustomizationID) = 'urn:fdc:peppol.eu:edec:trns:end-user-statistics-report:1.1'</xsl:attribute>
                     <svrl:text>[SCH-EUSR-01] The customization ID MUST use the value 'urn:fdc:peppol.eu:edec:trns:end-user-statistics-report:1.1'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(normalize-space(eusr:ProfileID) = 'urn:fdc:peppol.eu:edec:bis:reporting:1.0')">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-02">
                     <xsl:attribute name="test">normalize-space(eusr:ProfileID) = 'urn:fdc:peppol.eu:edec:bis:reporting:1.0'</xsl:attribute>
                     <svrl:text>[SCH-EUSR-02] The profile ID MUST use the value 'urn:fdc:peppol.eu:edec:bis:reporting:1.0'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or max(eusr:Subset/eusr:SendingEndUsers) le xs:integer(eusr:FullSet/eusr:SendingEndUsers))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-03">
                     <xsl:attribute name="test">$empty or max(eusr:Subset/eusr:SendingEndUsers) le xs:integer(eusr:FullSet/eusr:SendingEndUsers)</xsl:attribute>
                     <svrl:text>[SCH-EUSR-03] The maximum of all subsets of SendingEndUsers (<xsl:value-of select="max(eusr:Subset/eusr:SendingEndUsers)"/>) MUST be lower or equal to FullSet/SendingEndUsers (<xsl:value-of select="xs:integer(eusr:FullSet/eusr:SendingEndUsers)"/>)</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or max(eusr:Subset/eusr:ReceivingEndUsers) le xs:integer(eusr:FullSet/eusr:ReceivingEndUsers))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-04">
                     <xsl:attribute name="test">$empty or max(eusr:Subset/eusr:ReceivingEndUsers) le xs:integer(eusr:FullSet/eusr:ReceivingEndUsers)</xsl:attribute>
                     <svrl:text>[SCH-EUSR-04] The maximum of all subsets of ReceivingEndUsers (<xsl:value-of select="max(eusr:Subset/eusr:ReceivingEndUsers)"/>) MUST be lower or equal to FullSet/ReceivingEndUsers (<xsl:value-of select="xs:integer(eusr:FullSet/eusr:ReceivingEndUsers)"/>)</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or max(eusr:Subset/eusr:SendingOrReceivingEndUsers) le xs:integer(eusr:FullSet/eusr:SendingOrReceivingEndUsers))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-22">
                     <xsl:attribute name="test">$empty or max(eusr:Subset/eusr:SendingOrReceivingEndUsers) le xs:integer(eusr:FullSet/eusr:SendingOrReceivingEndUsers)</xsl:attribute>
                     <svrl:text>[SCH-EUSR-22] The maximum of all subsets of SendingOrReceivingEndUsers (<xsl:value-of select="max(eusr:Subset/eusr:SendingOrReceivingEndUsers)"/>) MUST be lower or equal to FullSet/SendingOrReceivingEndUsers (<xsl:value-of select="xs:integer(eusr:FullSet/eusr:SendingOrReceivingEndUsers)"/>)</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(xs:integer(eusr:FullSet/eusr:SendingOrReceivingEndUsers) &lt;= $total)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-19">
                     <xsl:attribute name="test">xs:integer(eusr:FullSet/eusr:SendingOrReceivingEndUsers) &lt;= $total</xsl:attribute>
                     <svrl:text>[SCH-EUSR-19] The number of SendingOrReceivingEndUsers (<xsl:value-of select="eusr:FullSet/eusr:SendingOrReceivingEndUsers"/>) MUST be lower or equal to the sum of the SendingEndUsers and ReceivingEndUsers (<xsl:value-of select="$total"/>)</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(xs:integer(eusr:FullSet/eusr:SendingOrReceivingEndUsers) &gt;= xs:integer(eusr:FullSet/eusr:SendingEndUsers))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-20">
                     <xsl:attribute name="test">xs:integer(eusr:FullSet/eusr:SendingOrReceivingEndUsers) &gt;= xs:integer(eusr:FullSet/eusr:SendingEndUsers)</xsl:attribute>
                     <svrl:text>[SCH-EUSR-20] The number of SendingOrReceivingEndUsers (<xsl:value-of select="eusr:FullSet/eusr:SendingOrReceivingEndUsers"/>) MUST be greater or equal to the number of SendingEndUsers (<xsl:value-of select="eusr:FullSet/eusr:SendingEndUsers"/>)</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(xs:integer(eusr:FullSet/eusr:SendingOrReceivingEndUsers) &gt;= xs:integer(eusr:FullSet/eusr:ReceivingEndUsers))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-21">
                     <xsl:attribute name="test">xs:integer(eusr:FullSet/eusr:SendingOrReceivingEndUsers) &gt;= xs:integer(eusr:FullSet/eusr:ReceivingEndUsers)</xsl:attribute>
                     <svrl:text>[SCH-EUSR-21] The number of SendingOrReceivingEndUsers (<xsl:value-of select="eusr:FullSet/eusr:SendingOrReceivingEndUsers"/>) MUST be greater or equal to the number of ReceivingEndUsers (<xsl:value-of select="eusr:FullSet/eusr:ReceivingEndUsers"/>)</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or eusr:Subset[normalize-space(@type) = 'PerDT-PR'])">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-15">
                     <xsl:attribute name="test">$empty or eusr:Subset[normalize-space(@type) = 'PerDT-PR']</xsl:attribute>
                     <svrl:text>[SCH-EUSR-15] At least one subset per 'Dataset Type ID and Process ID' MUST exist</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (eusr:Subset[normalize-space(@type) = 'PerDT-PR']),                                                         $stdt in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                         $stpr in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'PR']) satisfies                                                     count(eusr:Subset[normalize-space(@type) ='PerDT-PR'][every $dt in (eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                 $pr in (eusr:Key[normalize-space(@metaSchemeID) = 'PR']) satisfies                                                                                                           concat(normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                  normalize-space($pr/@schemeID),'::',normalize-space($pr)) =                                                                                                           concat(normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                  normalize-space($stpr/@schemeID),'::',normalize-space($stpr))]) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-13">
                     <xsl:attribute name="test">every $st in (eusr:Subset[normalize-space(@type) = 'PerDT-PR']),                                                         $stdt in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                         $stpr in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'PR']) satisfies                                                     count(eusr:Subset[normalize-space(@type) ='PerDT-PR'][every $dt in (eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                 $pr in (eusr:Key[normalize-space(@metaSchemeID) = 'PR']) satisfies                                                                                                           concat(normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                  normalize-space($pr/@schemeID),'::',normalize-space($pr)) =                                                                                                           concat(normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                  normalize-space($stpr/@schemeID),'::',normalize-space($stpr))]) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-13] Each combination of 'Dataset Type ID and Process ID' MUST occur only once.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (eusr:Subset[normalize-space(@type) = 'PerDT-PR-EUC']),                                                         $stdt in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                         $stpr in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'PR']),                                                         $stuc in ($st/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                     count(eusr:Subset[normalize-space(@type) ='PerDT-PR-EUC'][every $dt in (eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                    $pr in (eusr:Key[normalize-space(@metaSchemeID) = 'PR']),                                                                                                                    $uc in (eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                                                                              concat(normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                     normalize-space($pr/@schemeID),'::',normalize-space($pr),'::',                                                                                                                     normalize-space($uc)) =                                                                                                              concat(normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                     normalize-space($stpr/@schemeID),'::',normalize-space($stpr),'::',                                                                                                                     normalize-space($stuc))]) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-29">
                     <xsl:attribute name="test">every $st in (eusr:Subset[normalize-space(@type) = 'PerDT-PR-EUC']),                                                         $stdt in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                         $stpr in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'PR']),                                                         $stuc in ($st/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                     count(eusr:Subset[normalize-space(@type) ='PerDT-PR-EUC'][every $dt in (eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                    $pr in (eusr:Key[normalize-space(@metaSchemeID) = 'PR']),                                                                                                                    $uc in (eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                                                                              concat(normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                     normalize-space($pr/@schemeID),'::',normalize-space($pr),'::',                                                                                                                     normalize-space($uc)) =                                                                                                              concat(normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                     normalize-space($stpr/@schemeID),'::',normalize-space($stpr),'::',                                                                                                                     normalize-space($stuc))]) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-29] Each combination of 'Dataset Type ID, Process ID and End User Country' MUST occur only once.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or eusr:Subset[normalize-space(@type) = 'PerDT-EUC'])">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-37">
                     <xsl:attribute name="test">$empty or eusr:Subset[normalize-space(@type) = 'PerDT-EUC']</xsl:attribute>
                     <svrl:text>[SCH-EUSR-37] At least one subset per 'Dataset Type ID and End User Country' MUST exist</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (eusr:Subset[normalize-space(@type) = 'PerDT-EUC']),                                                         $stdt in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                         $steuc in ($st/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                     count(eusr:Subset[normalize-space(@type) ='PerDT-EUC'][every $dt in (eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                  $euc in (eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                                                                            concat(normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                   normalize-space($euc)) =                                                                                                            concat(normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                   normalize-space($steuc))]) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-38">
                     <xsl:attribute name="test">every $st in (eusr:Subset[normalize-space(@type) = 'PerDT-EUC']),                                                         $stdt in ($st/eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                         $steuc in ($st/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                     count(eusr:Subset[normalize-space(@type) ='PerDT-EUC'][every $dt in (eusr:Key[normalize-space(@metaSchemeID) = 'DT']),                                                                                                                  $euc in (eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                                                                            concat(normalize-space($dt/@schemeID),'::',normalize-space($dt),'::',                                                                                                                   normalize-space($euc)) =                                                                                                            concat(normalize-space($stdt/@schemeID),'::',normalize-space($stdt),'::',                                                                                                                   normalize-space($steuc))]) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-38] Each combination of 'Dataset Type ID and End User Country' MUST occur only once.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not($empty or eusr:Subset[normalize-space(@type) = 'PerEUC'])">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-39">
                     <xsl:attribute name="test">$empty or eusr:Subset[normalize-space(@type) = 'PerEUC']</xsl:attribute>
                     <svrl:text>[SCH-EUSR-39] At least one subset per 'End User Country' MUST exist</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (eusr:Subset[normalize-space(@type) = 'PerEUC']),                                                         $steuc in ($st/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                     count(eusr:Subset[normalize-space(@type) ='PerEUC'][every $euc in (eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                                                                         normalize-space($euc) = normalize-space($steuc)]) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-40">
                     <xsl:attribute name="test">every $st in (eusr:Subset[normalize-space(@type) = 'PerEUC']),                                                         $steuc in ($st/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                     count(eusr:Subset[normalize-space(@type) ='PerEUC'][every $euc in (eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']) satisfies                                                                                                         normalize-space($euc) = normalize-space($steuc)]) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-40] Each 'End User Country' MUST occur only once.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Subset[normalize-space(@type) !='PerDT-PR' and                                                                      normalize-space(@type) !='PerDT-PR-EUC' and                                                                     normalize-space(@type) !='PerDT-EUC' and                                                                      normalize-space(@type) !='PerEUC']) = 0)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-14">
                     <xsl:attribute name="test">count(eusr:Subset[normalize-space(@type) !='PerDT-PR' and                                                                      normalize-space(@type) !='PerDT-PR-EUC' and                                                                     normalize-space(@type) !='PerDT-EUC' and                                                                      normalize-space(@type) !='PerEUC']) = 0</xsl:attribute>
                     <svrl:text>[SCH-EUSR-14] Only allowed subset types MUST be used.</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (eusr:Subset) satisfies                                                         xs:integer($st/eusr:SendingOrReceivingEndUsers) &lt;= xs:integer($st/eusr:SendingEndUsers + $st/eusr:ReceivingEndUsers))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-33">
                     <xsl:attribute name="test">every $st in (eusr:Subset) satisfies                                                         xs:integer($st/eusr:SendingOrReceivingEndUsers) &lt;= xs:integer($st/eusr:SendingEndUsers + $st/eusr:ReceivingEndUsers)</xsl:attribute>
                     <svrl:text>[SCH-EUSR-33] The number of each Subset/SendingOrReceivingEndUsers MUST be lower or equal to the sum of the Subset/SendingEndUsers plus Subset/ReceivingEndUsers</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (eusr:Subset) satisfies                                                         xs:integer($st/eusr:SendingOrReceivingEndUsers) &gt;= xs:integer($st/eusr:SendingEndUsers))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-34">
                     <xsl:attribute name="test">every $st in (eusr:Subset) satisfies                                                         xs:integer($st/eusr:SendingOrReceivingEndUsers) &gt;= xs:integer($st/eusr:SendingEndUsers)</xsl:attribute>
                     <svrl:text>[SCH-EUSR-34] The number of each Subset/SendingOrReceivingEndUsers MUST be greater or equal to the number of Subset/SendingEndUsers (<xsl:value-of select="eusr:Subset/eusr:SendingEndUsers"/>)</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (eusr:Subset) satisfies                                                         xs:integer($st/eusr:SendingOrReceivingEndUsers) &gt;= xs:integer($st/eusr:ReceivingEndUsers))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-35">
                     <xsl:attribute name="test">every $st in (eusr:Subset) satisfies                                                         xs:integer($st/eusr:SendingOrReceivingEndUsers) &gt;= xs:integer($st/eusr:ReceivingEndUsers)</xsl:attribute>
                     <svrl:text>[SCH-EUSR-35] The number of each Subset/SendingOrReceivingEndUsers MUST be greater or equal to the number of Subset/ReceivingEndUsers (<xsl:value-of select="eusr:Subset/eusr:ReceivingEndUsers"/>)</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(every $st in (eusr:Subset) satisfies                                                         xs:integer($st/eusr:SendingOrReceivingEndUsers) &gt; 0)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-36">
                     <xsl:attribute name="test">every $st in (eusr:Subset) satisfies                                                         xs:integer($st/eusr:SendingOrReceivingEndUsers) &gt; 0</xsl:attribute>
                     <svrl:text>[SCH-EUSR-36] The number of each Subset/SendingOrReceivingEndUsers MUST be greater then zero, otherwise it MUST be omitted</svrl:text>
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
   <xsl:template match="/eusr:EndUserStatisticsReport/eusr:Header"
                 priority="6"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/eusr:EndUserStatisticsReport/eusr:Header" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Header</xsl:attribute>
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
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Header</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(matches(normalize-space(eusr:ReportPeriod/eusr:StartDate), '^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$'))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-16">
                     <xsl:attribute name="test">matches(normalize-space(eusr:ReportPeriod/eusr:StartDate), '^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$')</xsl:attribute>
                     <svrl:text>[SCH-EUSR-16] The reporting period start date (<xsl:value-of select="normalize-space(eusr:ReportPeriod/eusr:StartDate)"/>) MUST NOT contain timezone information</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(matches(normalize-space(eusr:ReportPeriod/eusr:EndDate), '^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$'))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-17">
                     <xsl:attribute name="test">matches(normalize-space(eusr:ReportPeriod/eusr:EndDate), '^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$')</xsl:attribute>
                     <svrl:text>[SCH-EUSR-17] The reporting period end date (<xsl:value-of select="normalize-space(eusr:ReportPeriod/eusr:EndDate)"/>) MUST NOT contain timezone information</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(eusr:ReportPeriod/eusr:EndDate &gt;= eusr:ReportPeriod/eusr:StartDate)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-18">
                     <xsl:attribute name="test">eusr:ReportPeriod/eusr:EndDate &gt;= eusr:ReportPeriod/eusr:StartDate</xsl:attribute>
                     <svrl:text>[SCH-EUSR-18] The report period start date (<xsl:value-of select="normalize-space(eusr:ReportPeriod/eusr:StartDate)"/>) MUST NOT be after the report period end date (<xsl:value-of select="normalize-space(eusr:ReportPeriod/eusr:EndDate)"/>)</svrl:text>
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
   <xsl:template match="/eusr:EndUserStatisticsReport/eusr:Header/eusr:ReporterID"
                 priority="5"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/eusr:EndUserStatisticsReport/eusr:Header/eusr:ReporterID" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Header/eusr:ReporterID</xsl:attribute>
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
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Header/eusr:ReporterID</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(normalize-space(.) != '')">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-06">
                     <xsl:attribute name="test">normalize-space(.) != ''</xsl:attribute>
                     <svrl:text>[SCH-EUSR-06] The Reporter ID MUST be present</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(not(contains(normalize-space(@schemeID), ' ')) and                                                   contains($cl_spidtype, concat(' ', normalize-space(@schemeID), ' ')))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-07">
                     <xsl:attribute name="test">not(contains(normalize-space(@schemeID), ' ')) and                                                   contains($cl_spidtype, concat(' ', normalize-space(@schemeID), ' '))</xsl:attribute>
                     <svrl:text>[SCH-EUSR-07] The Reporter ID scheme ID (<xsl:value-of select="normalize-space(@schemeID)"/>) MUST be coded according to the code list</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not((@schemeID='CertSubjectCN' and                                                    matches(normalize-space(.), '^P[A-Z]{2}[0-9]{6}$')) or                                                    not(@schemeID='CertSubjectCN'))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-08">
                     <xsl:attribute name="test">(@schemeID='CertSubjectCN' and                                                    matches(normalize-space(.), '^P[A-Z]{2}[0-9]{6}$')) or                                                    not(@schemeID='CertSubjectCN')</xsl:attribute>
                     <svrl:text>[SCH-EUSR-08] The layout of the certificate subject CN (<xsl:value-of select="normalize-space(.)"/>) is not a valid Peppol Seat ID</svrl:text>
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
   <xsl:template match="/eusr:EndUserStatisticsReport/eusr:Subset/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']"
                 priority="4"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/eusr:EndUserStatisticsReport/eusr:Subset/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']</xsl:attribute>
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
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(not(contains(normalize-space(.), ' ')) and                                                    contains($cl_iso3166, concat(' ', normalize-space(.), ' ')))">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-30">
                     <xsl:attribute name="test">not(contains(normalize-space(.), ' ')) and                                                    contains($cl_iso3166, concat(' ', normalize-space(.), ' '))</xsl:attribute>
                     <svrl:text>[SCH-EUSR-30] The country code MUST be coded with ISO code ISO 3166-1 alpha-2. Nevertheless, Greece may use the code 'EL', Kosovo may use the code 'XK' or '1A'.</svrl:text>
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
   <xsl:template match="/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-PR']"
                 priority="3"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:variable name="name" select="'The subset per Dataset Type ID and Process ID'"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-PR']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-PR']</xsl:attribute>
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
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-PR']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(count(eusr:Key) = 2)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-09">
                     <xsl:attribute name="test">count(eusr:Key) = 2</xsl:attribute>
                     <svrl:text>[SCH-EUSR-09] <xsl:value-of select="$name"/> MUST have two Key elements</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-10">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-10] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'DT'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'PR']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-11">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'PR']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-11] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'PR'</svrl:text>
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
   <xsl:template match="/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-PR-EUC']"
                 priority="2"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:variable name="name"
                    select="'The subset per Dataset Type ID, Process ID and End User Country'"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-PR-EUC']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-PR-EUC']</xsl:attribute>
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
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-PR-EUC']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(count(eusr:Key) = 3)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-23">
                     <xsl:attribute name="test">count(eusr:Key) = 3</xsl:attribute>
                     <svrl:text>[SCH-EUSR-23] <xsl:value-of select="$name"/> MUST have three Key elements</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-24">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-24] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'DT'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'PR']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-25">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'PR']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-25] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'PR'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'CC']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-26">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'CC']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-26] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'CC'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'EndUserCountry']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-27">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'EndUserCountry']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-27] <xsl:value-of select="$name"/> MUST have one CC Key element with the scheme ID 'EndUserCountry'</svrl:text>
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
   <xsl:template match="/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-EUC']"
                 priority="1"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:variable name="name"
                    select="'The subset per Dataset Type ID and End User Country'"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-EUC']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-EUC']</xsl:attribute>
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
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerDT-EUC']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(count(eusr:Key) = 2)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-41">
                     <xsl:attribute name="test">count(eusr:Key) = 2</xsl:attribute>
                     <svrl:text>[SCH-EUSR-41] <xsl:value-of select="$name"/> MUST have two Key elements</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-42">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'DT']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-42] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'DT'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'CC']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-43">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'CC']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-43] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'CC'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'EndUserCountry']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-44">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'EndUserCountry']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-44] <xsl:value-of select="$name"/> MUST have one CC Key element with the scheme ID 'EndUserCountry'</svrl:text>
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
   <xsl:template match="/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerEUC']"
                 priority="0"
                 mode="d12e9">
      <xsl:param name="schxslt:patterns-matched" as="xs:string*"/>
      <xsl:variable name="name" select="'The subset per End User Country'"/>
      <xsl:choose>
         <xsl:when test="$schxslt:patterns-matched[. = 'd12e9']">
            <schxslt:rule pattern="d12e9">
               <xsl:comment xmlns:svrl="http://purl.oclc.org/dsdl/svrl">WARNING: Rule for context "/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerEUC']" shadowed by preceding rule</xsl:comment>
               <svrl:suppressed-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerEUC']</xsl:attribute>
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
                  <xsl:attribute name="context">/eusr:EndUserStatisticsReport/eusr:Subset[normalize-space(@type) = 'PerEUC']</xsl:attribute>
               </svrl:fired-rule>
               <xsl:if test="not(count(eusr:Key) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-45">
                     <xsl:attribute name="test">count(eusr:Key) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-45] <xsl:value-of select="$name"/> MUST have one Key element</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'CC']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-46">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'CC']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-46] <xsl:value-of select="$name"/> MUST have one Key element with the meta scheme ID 'CC'</svrl:text>
                  </svrl:failed-assert>
               </xsl:if>
               <xsl:if test="not(count(eusr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'EndUserCountry']) = 1)">
                  <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                                      location="{schxslt:location(.)}"
                                      flag="fatal"
                                      id="SCH-EUSR-47">
                     <xsl:attribute name="test">count(eusr:Key[normalize-space(@metaSchemeID) = 'CC'][normalize-space(@schemeID) = 'EndUserCountry']) = 1</xsl:attribute>
                     <svrl:text>[SCH-EUSR-47] <xsl:value-of select="$name"/> MUST have one CC Key element with the scheme ID 'EndUserCountry'</svrl:text>
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
