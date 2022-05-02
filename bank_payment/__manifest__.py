# -*- coding: utf-8 -*-
{
    'name': "Bank Payment",

    'summary': """
        Generate file for bank import""",

    'description': """
    """,

    'author': "FlexERP Aps",
    'website': "http://www.flexerp.dk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/bank_payment_view.xml',
        'views/account_move_views.xml',
        'views/view_account_position_form.xml',
        'views/view_partner_bank.xml',
        'views/account_payment_term.xml',
    ],
}
