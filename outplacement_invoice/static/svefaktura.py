# flake8: noqa
"""
XML-data for use in testing.
"""
SVEFAKTURA = """
<Invoice xmlns:cac=\"urn:sfti:CommonAggregateComponents:1:0\" xmlns:cbc=\"urn:oasis:names:tc:ubl:CommonBasicComponents:1:0\" xmlns=\"urn:sfti:documents:BasicInvoice:1:0\">
    <ID>9100220</ID>
    <cbc:IssueDate>2020-02-11</cbc:IssueDate>
    <InvoiceTypeCode>380</InvoiceTypeCode>
    <InvoiceCurrencyCode>SEK</InvoiceCurrencyCode>
    <LineItemCountNumeric>1</LineItemCountNumeric>
    <cac:BuyerParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cac:ID>2021002114</cac:ID>
            </cac:PartyIdentification>
                <cac:PartyName>
                    <cbc:Name>Arbetsförmedlingen Skanningcentral</cbc:Name>
                </cac:PartyName>
                <cac:Address>
                    <cbc:Postbox>Skanningcentral</cbc:Postbox>
                    <cbc:CityName>KRISTINEHAMN</cbc:CityName>
                    <cbc:PostalZone>68185</cbc:PostalZone>
                </cac:Address>
                <cac:PartyTaxScheme>
                    <cac:CompanyID>2021002114</cac:CompanyID>
                    <cac:TaxScheme>
                        <cac:ID>SWT</cac:ID>
                    </cac:TaxScheme>
                </cac:PartyTaxScheme>
        </cac:Party>
    </cac:BuyerParty>
    <cac:SellerParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cac:ID>5565600854</cac:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>Se Eqv</cbc:Name>
            </cac:PartyName>
            <cac:Address>
                <cbc:StreetName>Norgegatan 1</cbc:StreetName>
                <cbc:CityName>Kista</cbc:CityName>
                <cbc:PostalZone>16432</cbc:PostalZone>
            </cac:Address>
            <cac:PartyTaxScheme>
                <cac:CompanyID>SE556560085401</cac:CompanyID>
                <cac:RegistrationAddress/>
                <cac:TaxScheme>
                    <cac:ID>VAT</cac:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyTaxScheme>
                <cbc:RegistrationName>Järva Tolk &amp; Översättningsservice AB
                </cbc:RegistrationName>
                <cac:CompanyID>556560-0854</cac:CompanyID>
                <cbc:ExemptionReason>Godkänd för F-skatt</cbc:ExemptionReason>
                <cac:RegistrationAddress/>
                <cac:TaxScheme>
                    <cac:ID>SWT</cac:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:Contact>
                <cbc:Name>Ser</cbc:Name>
                <cbc:Telephone>08</cbc:Telephone>
                <cbc:Telefax>084</cbc:Telefax>
                <cbc:ElectronicMail>mail@mail.se</cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:SellerParty>
    <cac:Delivery>
        <cac:DeliveryAddress>
            <cbc:StreetName>Hälsingegatan 38</cbc:StreetName>
            <cbc:Department>Arbetsförmedlingen HK</cbc:Department>
            <cbc:CityName>STOCKHOLM</cbc:CityName>
            <cbc:PostalZone>11343</cbc:PostalZone>
        </cac:DeliveryAddress>
    </cac:Delivery>
    <cac:PaymentMeans>
        <cac:PaymentMeansTypeCode>1</cac:PaymentMeansTypeCode>
        <cbc:DuePaymentDate>2020-03-15</cbc:DuePaymentDate>
        <cac:PayeeFinancialAccount>
            <cac:ID>1250000000052871023751</cac:ID>
            <cac:FinancialInstitutionBranch>
                <cac:FinancialInstitution>
                    <cac:ID>ESSESESS</cac:ID>
                </cac:FinancialInstitution>
            </cac:FinancialInstitutionBranch>
        </cac:PayeeFinancialAccount>
    </cac:PaymentMeans>
    <cac:PaymentMeans>
        <cac:PaymentMeansTypeCode>1</cac:PaymentMeansTypeCode>
        <cbc:DuePaymentDate>2020-03-15</cbc:DuePaymentDate>
        <cac:PayeeFinancialAccount>
            <cac:ID>7990559</cac:ID>
            <cac:FinancialInstitutionBranch>
                <cac:FinancialInstitution>
                    <cac:ID>BGABSESS</cac:ID>
                </cac:FinancialInstitution>
            </cac:FinancialInstitutionBranch>
            <cac:PaymentInstructionID>5377270</cac:PaymentInstructionID>
        </cac:PayeeFinancialAccount>
    </cac:PaymentMeans>
    <cac:PaymentTerms>
        <cbc:Note>30 dagar</cbc:Note>
        <cbc:PenaltySurchargePercent>10</cbc:PenaltySurchargePercent>
    </cac:PaymentTerms>
    <cac:TaxTotal>
        <cbc:TotalTaxAmount amountCurrencyID=\"SEK\">12.50
        </cbc:TotalTaxAmount>
        <cac:TaxSubTotal>
            <cbc:TaxableAmount amountCurrencyID=\"SEK\">50.00
            </cbc:TaxableAmount>\
            <cbc:TaxAmount amountCurrencyID=\"SEK\">12.50</cbc:TaxAmount>
            <cac:TaxCategory>
            <cac:ID>S</cac:ID>
            <cbc:Percent>25</cbc:Percent>
            <cac:TaxScheme>
                <cac:ID>VAT</cac:ID>
            </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubTotal>
    </cac:TaxTotal>
    <cac:LegalTotal>
        <cbc:LineExtensionTotalAmount amountCurrencyID=\"SEK\">50.00</cbc:LineExtensionTotalAmount>
        <cbc:TaxExclusiveTotalAmount amountCurrencyID=\"SEK\">50.00</cbc:TaxExclusiveTotalAmount>
        <cbc:TaxInclusiveTotalAmount amountCurrencyID=\"SEK\">62.50</cbc:TaxInclusiveTotalAmount>
        <cac:RoundOffAmount amountCurrencyID=\"SEK\">0
        </cac:RoundOffAmount>
    </cac:LegalTotal>
    <cac:InvoiceLine>
        <cac:ID>0</cac:ID>
        <cbc:InvoicedQuantity quantityUnitCode=\"st\">1.00
        </cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount amountCurrencyID=\"SEK\">50.00</cbc:LineExtensionAmount>
        <cac:OrderLineReference>
            <cac:OrderReference>
                <cac:BuyersID>3215</cac:BuyersID>
            </cac:OrderReference>
        </cac:OrderLineReference>
        <cac:Item>
            <cbc:Description>Förmedlingsavgift Godkänd Platstolk
            </cbc:Description>
            <cac:SellersItemIdentification>
                <cac:ID>51</cac:ID>
            </cac:SellersItemIdentification>
            <cac:TaxCategory>
                <cac:ID>S</cac:ID>
                <cbc:Percent>25</cbc:Percent>
                <cac:TaxScheme>
                    <cac:ID>VAT</cac:ID>
                </cac:TaxScheme>
            </cac:TaxCategory>
            <cac:BasePrice>
                <cbc:PriceAmount amountCurrencyID=\"SEK\">50.00
                </cbc:PriceAmount>
            </cac:BasePrice>
        </cac:Item>
    </cac:InvoiceLine>
    <RequisitionistDocumentReference>
        <cac:ID>LT05Kst: 30374</cac:ID>
    </RequisitionistDocumentReference>
</Invoice>
"""