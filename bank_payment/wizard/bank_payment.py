from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.misc import format_date
from odoo.tools import html2plaintext
from collections import OrderedDict
import base64


class BankPayment(models.TransientModel):
    _name = 'bank.payment'
    _description = 'Get txt file ready for import to bank'

    def error_handler(self, move_name: str, field_name: str) -> None:
        raise UserError(f"""
        Insufficient data!!
        Invoice number: {move_name}
        Missing field: {field_name}
        """)

    ####################################################
    # RULES
    ####################################################

    def _get_value_rule(self, value: str, field_value: str, plus_sign: bool = False) -> str:
        """
        Based on rules return string that matches those rules
        Example:
        param:
            value='name'
            field_value='test'
            rules = {
                'name': {
                    'len': 8,
                    'type': 'txt'
                },
            }
        return: "test    "  # notice spaces and quotations
        """
        rules = {
            'total_lines': {'len': 6, 'type': 'int'},
            'total_amount': {'len': 13, 'type': 'int'},
            'trans_type': {'len': 14, 'type': 'txt'},
            'index': {'len': 4, 'type': 'int'},
            'eksp_date': {'len': 8, 'type': 'int'},
            'amount': {'len': 13, 'type': 'int'},
            'currency': {'len': 3, 'type': 'txt'},
            'from_type': {'len': 1, 'type': 'int'},
            'from_account': {'len': 15, 'type': 'int'},
            'transaction_type': {'len': 1, 'type': 'int'},
            'cust_reg': {'len': 4, 'type': 'int'},
            'cust_acc': {'len': 10, 'type': 'int'},
            'recipient_acc_number': {'len': 34, 'type': 'txt'},
            'swift_number': {'len': 11, 'type': 'txt'},
            'transaction_option': {'len': 1, 'type': 'int'},
            'journal_text': {'len': 35, 'type': 'txt'},
            'transfer_type': {'len': 2, 'type': 'int'},
            'name': {'len': 32, 'type': 'txt'},
            'recipient': {'len': 35, 'type': 'txt'},
            'street': {'len': 32, 'type': 'txt'},
            'street2': {'len': 32, 'type': 'txt'},
            'zip_code': {'len': 4, 'type': 'txt'},
            'city': {'len': 32, 'type': 'txt'},
            'recipient_street': {'len': 35, 'type': 'txt'},
            'recipient_street2': {'len': 35, 'type': 'txt'},
            'recipient_country': {'len': 35, 'type': 'txt'},
            'journal_name': {'len': 35, 'type': 'txt'},
            'notification_text': {'len': 35, 'type': 'txt'},
            'document_reference': {'len': 35, 'type': 'txt'},
            'payment_id': {'len': 19, 'type': 'txt'},
            'card_code': {'len': 2, 'type': 'txt'},
            'blank2': {'len': 2, 'type': 'txt'},
            'blank3': {'len': 3, 'type': 'txt'},
            'blank4': {'len': 4, 'type': 'txt'},
            'blank6': {'len': 6, 'type': 'txt'},
            'blank8': {'len': 8, 'type': 'txt'},
            'blank10': {'len': 10, 'type': 'txt'},
            'blank14': {'len': 14, 'type': 'txt'},
            'blank16': {'len': 16, 'type': 'txt'},
            'blank24': {'len': 24, 'type': 'txt'},
            'blank32': {'len': 32, 'type': 'txt'},
            'blank35': {'len': 35, 'type': 'txt'},
            'blank45': {'len': 45, 'type': 'txt'},
            'blank64': {'len': 64, 'type': 'txt'},
            'blank75': {'len': 75, 'type': 'txt'},
            'blank90': {'len': 90, 'type': 'txt'},
            'blank215': {'len': 215, 'type': 'txt'},
            'blank255': {'len': 255, 'type': 'txt'},
        }
        rule = rules[value]
        if len(field_value) < rule['len']:
            if rule['type'] == 'txt':
                field_value += ' ' * (rule['len'] - len(field_value))
                final_value = f'\"{field_value}\"'

            elif rule['type'] == 'int':
                field_value = '0' * (rule['len'] - len(field_value)) + field_value
                if plus_sign:
                    final_value = f'\"{field_value}+\"'
                else:
                    final_value = f'\"{field_value}\"'

        elif len(field_value) == rule['len']:
            final_value = f'\"{field_value}\"'

        else:
            field_value = field_value[0:rule['len']]  # Cut the value if length is more than requested
            final_value = f'\"{field_value}\"'

        return final_value

    ####################################################
    # VALUES
    ####################################################

    def _get_first_line_values(self) -> dict:
        """
        return constant values for first line
        """
        today = format_date(self.env, fields.Date.to_string(fields.Date.today()), date_format='yyyyMMdd')

        values = {
            'trans_type': self._get_value_rule('trans_type', 'IB000000000000'),
            'creation_date': self._get_value_rule('eksp_date', today),
            'blank1': self._get_value_rule('blank90', ''),
            'blank2': self._get_value_rule('blank255', ''),
            'blank3': self._get_value_rule('blank255', ''),
            'blank4': self._get_value_rule('blank255', '')
        }

        return values

    def _get_last_line_values(self, total_lines: int, total_amount: int) -> dict:
        """
        return constant values for last line
        """
        today = format_date(self.env, fields.Date.to_string(fields.Date.today()), date_format='yyyyMMdd')

        values = {
            'trans_type': self._get_value_rule('trans_type', 'IB999999999999'),
            'creation_date': self._get_value_rule('eksp_date', today),
            'total_lines': self._get_value_rule('total_lines', str(total_lines)),
            'total_amount': self._get_value_rule('total_amount', str(total_amount), plus_sign=True),
            'blank1': self._get_value_rule('blank64', ''),
            'blank2': self._get_value_rule('blank255', ''),
            'blank3': self._get_value_rule('blank255', ''),
            'blank4': self._get_value_rule('blank255', '')
        }

        return values

    def _get_trans_type(self, move_id: models.Model) -> str:
        """
        return transfer type (defined in fiscal position)
        """
        trans_type = {
            'domestic': 'IB030202000006',
            'international': 'IB030204000004',
            'payment_card': 'IB030207000002',
        }
        if move_id.fiscal_position_id:
            if move_id.fiscal_position_id.bank_trans_type:
                return trans_type[move_id.fiscal_position_id.bank_trans_type]

        return trans_type['domestic']

    def _get_from_type(self, move_id: models.Model) -> str:
        """
        return from type (defined in res.partner.bank)
        """
        if move_id.partner_bank_id:
            if move_id.partner_bank_id.from_type:
                return move_id.partner_bank_id.from_type
            else:
                self.error_handler(move_id.name, 'Partner Bank From Type')
        else:
            self.error_handler(move_id.name, 'Recipient Bank')

    def _get_from_account(self, move_id: models.Model) -> str:
        """
        return company account number
        """
        company_partner = move_id.company_id.partner_id
        acc_number = company_partner.bank_ids

        if acc_number:
            if len(acc_number[0].acc_number) == 15:
                return acc_number[0].acc_number
            else:
                self.error_handler(move_id.name, 'Company account number (total length should be 15)')
        else:
            self.error_handler(move_id.name, 'Company account number')

    def _get_partner_acc_number(self, move_id: models.Model) -> str:
        """
        return partner account number
        """
        partner_bank = move_id.partner_bank_id

        if partner_bank:
            acc_number = partner_bank.acc_number
            if len(acc_number) == 14:
                return acc_number
            else:
                self.error_handler(move_id.name, 'Recipient account number (total length should be 14)')
        else:
            self.error_handler(move_id.name, 'Recipient Bank')

    def _get_transaction_option(self, move_id: models.Model) -> str:
        """
        return transaction option (defined in payment terms)
        default: (1, Standard transfer)
        """
        if move_id.invoice_payment_term_id and move_id.invoice_payment_term_id.transaction_option:
            return str(move_id.invoice_payment_term_id.transaction_option)

        return '1'  # Standard transfer

    def _get_payment_reference(self, move_id: models.Model) -> str:
        """
        return journal text (Payment reference)
        """
        if move_id.payment_reference:
            return move_id.payment_reference

        else:
            self.error_handler(move_id.name, 'Payment reference')

    def _get_notification_text(self, move_id: models.Model) -> str:
        """
        Divide narration by paragraph
        return 5 notification text for bank import
        """
        narration_dict = {
            'narration_text1': '',
            'narration_text2': '',
            'narration_text3': '',
            'narration_text4': '',
            'narration_text5': '',
        }

        narration = html2plaintext(move_id.narration)
        if narration:
            narrations = narration.split('\n')
            if len(narrations) > 5:
                self.error_handler(move_id.name, 'Narration (you can have max 5 paragraphs)')

            for i in range(1, len(narrations) + 1):
                if len(narrations[i - 1]) > 35:
                    self.error_handler(
                        move_id.name, f'Narration (every paragraph should be max length of 35). Problematic paragraph: {i}')

                narration_dict[f'narration_text{i}'] = narrations[i - 1]

        else:
            narration_dict['narration_text1'] = move_id.name

        return [value for value in narration_dict.values()]

    def _get_document_reference(self, move_id: models.Model) -> str:
        """
        return document reference (origin or bill reference)
        """
        if move_id.invoice_origin:
            return move_id.invoice_origin

        elif move_id.ref:
            return move_id.ref

        else:
            self.error_handler(move_id.name, 'Bill reference')

    def _get_transfer_type(self, move_id: models.Model) -> str:
        """
        return transfer type
        """
        if move_id.invoice_payment_term_id:
            transfer_type = move_id.invoice_payment_term_id.transfer_type
            if transfer_type:
                return transfer_type

        return '53'  # default value (53, Standard transfer)

    def _get_recipient_acc_number(self, move_id: models.Model) -> str:
        """
        return IBAN and SWIFT
        """
        partner_bank = move_id.partner_bank_id

        if partner_bank:
            acc_number = partner_bank.acc_number
            bank_id = partner_bank.bank_id
            if bank_id:
                swift_code = partner_bank.bank_id.bic
                if swift_code:
                    return acc_number, swift_code
                else:
                    self.error_handler(move_id.name, 'Partner Bank SWIFT/BIC Code')
            else:
                self.error_handler(move_id.name, 'Partner Bank')

        else:
            self.error_handler(move_id.name, 'Recipient Bank')

    def _get_card_code(self, move_id: models.Model) -> str:
        """
        return card code
        """
        if move_id.partner_bank_id:
            if move_id.partner_bank_id.card_code:
                return move_id.partner_bank_id.card_code
            else:
                self.error_handler(move_id.name, 'Card Code (defined in partner bank)')
        else:
            self.error_handler(move_id.name, 'Recipient Bank')

    ####################################################
    # DATA
    ####################################################

    def _generate_data_line(self, **kwargs):
        """
        Generate line for data text.
        Here we implement logic for commas.
        """
        data = ''
        for value in kwargs.values():
            data += value + ','

        data = data[:-1]  # remove last comma

        return data

    def _prepare_bank_payment_data(self, move_ids: models.Model) -> str:
        """
        Prepare data with textual values that will be in bank payment file
        """
        data = ''

        data += self._generate_data_line(**self._get_first_line_values()) + '\n'

        total_amount = 0
        total_lines = 0
        for move in move_ids:
            if move.state != 'posted':
                self.error_handler(move.name, 'Status. Bill must be posted')

            total_lines += 1
            # MONETARY FIELDS
            trans_type = self._get_value_rule('trans_type', self._get_trans_type(move))
            index = self._get_value_rule('index', '0001')  # constant value
            eksp_date = format_date(self.env, fields.Date.to_string(move.invoice_date_due), date_format='yyyyMMdd')
            eksp_date = self._get_value_rule('eksp_date', eksp_date)
            amount = int(move.amount_total * 100)
            total_amount += amount
            amount = self._get_value_rule('amount', str(amount), True)
            currency = self._get_value_rule('currency', move.currency_id.name)
            from_type = self._get_value_rule('from_type', self._get_from_type(move))
            from_account = self._get_value_rule('from_account', self._get_from_account(move))
            transaction_type = self._get_value_rule('transaction_type', '2')  # constant value
            transaction_option = self._get_value_rule('from_type', self._get_transaction_option(move))
            journal_text = self._get_value_rule('journal_text', self._get_payment_reference(move))
            transfer_type = self._get_value_rule('transfer_type', self._get_transfer_type(move))
            recipient_acc_number, swift_number = self._get_recipient_acc_number(move)
            recipient_acc_number = self._get_value_rule('recipient_acc_number', recipient_acc_number)
            swift_number = self._get_value_rule('swift_number', swift_number)
            payment_id = self._get_value_rule('payment_id', self._get_payment_reference(move))

            # NON-MONETARY FIELDS
            partner_id = move.partner_id
            name = partner_id.name or ''
            partner_name = self._get_value_rule('name', name)
            recipient = self._get_value_rule('recipient', name)
            street = partner_id.street or ''
            partner_street = self._get_value_rule('street', street)
            recipient_street = self._get_value_rule('recipient_street', street)
            street2 = partner_id.street2 or ''
            partner_street2 = self._get_value_rule('street2', street2)
            recipient_street2 = self._get_value_rule('recipient_street2', street2)
            recipient_country = partner_id.country_id.name or ''
            recipient_country = self._get_value_rule('recipient_country', recipient_country)
            zip_code = partner_id.zip or ''
            partner_zip_code = self._get_value_rule('zip_code', zip_code)
            city = partner_id.city or ''
            partner_city = self._get_value_rule('city', city)
            journal_name = self._get_value_rule('journal_name', move.journal_id.name)

            # GROUP OF FIELDS WHERE ONE OF THEM HAS TO BE FIELD
            narration_text1, narration_text2, narration_text3, narration_text4, narration_text5 = self._get_notification_text(move)  # noqa
            notification_text1 = self._get_value_rule('notification_text', narration_text1)
            notification_text2 = self._get_value_rule('notification_text', narration_text2)
            notification_text3 = self._get_value_rule('notification_text', narration_text3)
            notification_text4 = self._get_value_rule('notification_text', narration_text4)
            notification_text5 = self._get_value_rule('notification_text', narration_text5)
            document_reference = self._get_value_rule('document_reference', self._get_document_reference(move))

            # BLANK VALUES
            blank2 = self._get_value_rule('blank2', '')
            blank3 = self._get_value_rule('blank3', '')
            blank4 = self._get_value_rule('blank4', '')
            blank6 = self._get_value_rule('blank6', '')
            blank8 = self._get_value_rule('blank8', '')
            blank10 = self._get_value_rule('blank10', '')
            blank14 = self._get_value_rule('blank14', '')
            blank16 = self._get_value_rule('blank16', '')
            blank24 = self._get_value_rule('blank24', '')
            blank32 = self._get_value_rule('blank32', '')
            blank35 = self._get_value_rule('blank35', '')
            blank45 = self._get_value_rule('blank45', '')
            blank75 = self._get_value_rule('blank75', '')
            blank215 = self._get_value_rule('blank215', '')

            data_values = OrderedDict()
            if self._get_trans_type(move) == 'IB030202000006':  # domestic
                partner_acc_number = self._get_partner_acc_number(move)
                cust_reg = self._get_value_rule('cust_reg', partner_acc_number[:4])
                cust_acc = self._get_value_rule('cust_acc', partner_acc_number[4:])

                data_values = OrderedDict({
                    "trans_type": trans_type,
                    "index": index,
                    "eksp_date": eksp_date,
                    "amount": amount,
                    "currency": currency,
                    "from_type": from_type,
                    "from_account": from_account,
                    "transaction_type": transaction_type,
                    "cust_reg": cust_reg,
                    "cust_acc": cust_acc,
                    "transaction_option": transaction_option,
                    "journal_text": journal_text,
                    "name": partner_name,
                    "street": partner_street,
                    "street2": partner_street2,
                    "zip_code": partner_zip_code,
                    "city": partner_city,
                    "own_journal_number": move.name,
                    'notification_text1': notification_text1,
                    'notification_text2': notification_text2,
                    'notification_text3': notification_text3,
                    'notification_text4': notification_text4,
                    'notification_text5': notification_text5,
                    "blank1": blank35,
                    "document_reference": document_reference,
                    "blank2": blank35,
                    "blank3": blank35,
                    "blank4": blank35,
                    "blank5": blank3,
                    "blank6": blank35,
                    "blank7": blank35,
                    "blank8": blank35,
                    "blank9": blank35,
                    "blank10": blank6,
                    "blank11": blank14
                })
            elif self._get_trans_type(move) == 'IB030204000004':  # international
                data_values = OrderedDict({
                    "trans_type": trans_type,
                    "index": index,
                    "eksp_date": eksp_date,
                    "amount": amount,
                    "from_type": from_type,
                    "from_account": from_account,
                    "currency": currency,
                    "transfer_currency": currency,
                    "transfer_type": transfer_type,
                    "payment_text1": document_reference,
                    "payment_text2": blank35,
                    "payment_text3": blank35,
                    "payment_text4": blank35,
                    "recipient": recipient,
                    "recipient_street": recipient_street,
                    "recipient_street2": recipient_street2,
                    "recipient_country": recipient_country,
                    "recipient_acc_number": recipient_acc_number,
                    "swift_number": swift_number,
                    "blank1": blank45,
                    "blank2": blank75,
                    "blank3": blank75,
                    "blank4": blank24,
                    "blank5": blank215
                })
            elif self._get_trans_type(move) == 'IB030207000002':  # payment_card
                card_code = self._get_value_rule('card_code', self._get_card_code(move)
                                                 )  # Specific for Payment card only

                data_values = OrderedDict({
                    "trans_type": trans_type,
                    "index": index,
                    "eksp_date": eksp_date,
                    "amount": amount,
                    "from_type": from_type,
                    "from_account": from_account,
                    "card_code": card_code,
                    "payment_id": payment_id,
                    "blank1": blank4,
                    "blank2": blank10,
                    "blank3": blank8,
                    "recipient_name": partner_name,
                    "blank4": blank32,
                    "journal_nr": document_reference,
                    "blank5": blank35,
                    "blank6": blank35,
                    "blank7": blank35,
                    "blank8": blank35,
                    "blank9": blank35,
                    "blank10": blank35,
                    "blank11": blank35,
                    "blank12": blank35,
                    "blank13": blank35,
                    "blank14": blank35,
                    "blank15": blank35,
                    "blank16": blank16,
                    "blank17": blank215,
                })
            else:
                raise UserError(f"""
                Something went wrong. Contact your administrator!
                Invoice number: {move.name}
                """)

            data += self._generate_data_line(**data_values) + '\n'

        data += self._generate_data_line(**self._get_last_line_values(total_lines, total_amount))

        return data

    def action_download_bank_payment(self):
        """
        return: download bank payment file
        """
        ctx = self.env.context
        move_ids = self.env['account.move'].browse(ctx.get('active_ids'))
        datas = base64.b64encode(bytes(self._prepare_bank_payment_data(move_ids), 'utf-8'))
        attachment_id = self.env['ir.attachment'].create({
            'name': 'bank_payment.txt',
            'datas': datas,
            'mimetype': 'text/plain',
        })

        return {
            'type': 'ir.actions.act_url',
            'name': 'Bank Payment',
            'url': f'/web/content/{attachment_id.id}?download=true'
        }
