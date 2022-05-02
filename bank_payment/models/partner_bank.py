from odoo import models, fields, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    from_type = fields.Selection([
        ('1', 'Financial Account'),
        ('2', 'Bank Account'),
    ], help="Choose option for bank from type.\n"
        "Selected option will be used during export data for bank payment.\n"
        "If nothing is selected, error will be raised")
    card_code = fields.Selection([
        ('01', '01'),
        ('04', '04'),
        ('15', '15'),
        ('71', '71'),
        ('73', '73'),
        ('75', '75'),
    ], help="Choose option for card code.\n"
        "Selected option will be used during export data for bank payment in case it's payment card .\n"
        "If nothing is selected, error will be raised")
