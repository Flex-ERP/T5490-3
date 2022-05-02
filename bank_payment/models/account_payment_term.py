from odoo import models, fields, api


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    transaction_option = fields.Selection([
        ('1', 'Standard transfer'),
        ('2', 'Same-day transfer'),
        ('3', 'Immediate transfer'),
    ], help="Choose option for bank transaction option.\n"
        "Selected option will be used during export data for bank payment.\n"
        "If nothing is selected, Standard transfer will be used")
    transfer_type = fields.Selection([
        ('21', 'Foreign check'),
        ('53', 'Standard transfer'),
        ('57', 'Express delivery'),
    ], help="Choose option for bank transaction option.\n"
        "Selected option will be used during export data for bank payment.\n"
        "If nothing is selected, Standard transfer will be used")
