import ast
from odoo import models

class CustomPartnerLedgerReportHandler(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'

    def _get_aml_values(self, options, expanded_partner=None, offset=None, limit=None):
        aml_values = super()._get_aml_values(options, expanded_partner)

        currency_table = self.env['res.currency']._get_query_currency_table(options)
        precision = 8  # Set the default precision as needed

        if isinstance(currency_table, str):
            # Modify the currency_table string to a valid dictionary format
            currency_table = ast.literal_eval(f"{{{currency_table}}}")

        if isinstance(currency_table, dict):
            precision = currency_table.get('precision', 8)

        for aml_value in aml_values:
            aml_value['debit'] = round(aml_value['debit'] * currency_table.get('rate', 1), precision)
            aml_value['credit'] = round(aml_value['credit'] * currency_table.get('rate', 1), precision)
            aml_value['balance'] = round(aml_value['balance'] * currency_table.get('rate', 1), precision)

        return aml_values