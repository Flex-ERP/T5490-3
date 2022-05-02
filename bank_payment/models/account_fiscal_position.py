from odoo import models, fields, api


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    bank_trans_type = fields.Selection([
        ('domestic', 'Domestic transfer'),
        ('international', 'International transfer'),
        ('payment_card', 'Payment card'),
    ], help="Choose option for bank transfer type.\n"
        "Selected option will be used during export data for bank payment.\n"
        "If nothing is selected, Domestic transfer will be used")
