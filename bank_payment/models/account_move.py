# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_bank_payment(self):
        '''
        return: wizard bank payment window
        '''
        return {
            'name': 'Bank Payment',
            'res_model': 'bank.payment',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
