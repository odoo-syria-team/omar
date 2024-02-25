# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import time
from odoo import models, api, _
from odoo.exceptions import UserError


class PartnerViewInherit(models.TransientModel):
    _inherit = 'account.partner.ledger'

    @api.model
    def view_report(self, option):
        r = self.env['account.partner.ledger'].search([('id', '=', option[0])])
        data = {
            'display_account': r.display_account,
            'model': self,
            'journals': r.journal_ids,
            'accounts': r.account_ids,
            'target_move': r.target_move,
            'partners': r.partner_ids,
            'reconciled': r.reconciled,
            'account_type': r.account_type,
            'partner_tags': r.partner_category_ids,
        }

        if r.date_from:
            data.update({
                'date_from': r.date_from,
            })
        if r.date_to:
            data.update({
                'date_to': r.date_to,
            })
        filters = self.get_filter(option)
        records = self._get_report_value(data)
        currency = self._get_currency()
        return {
            'name': "partner Ledger",
            'type': 'ir.actions.client',
            'tag': 'p_l_2',
            'filters': filters,
            'report_lines': records['Partners'],
            'debit_total': records['debit_total'],
            'credit_total': records['credit_total'],
            'debit_balance': records['debit_balance'],
            'currency': currency,
        }

    
    def _get_report_value(self, data):
        docs = data['model']
        display_account = data['display_account']
        init_balance = True
        company_id = self.env.companies.ids
        accounts = self.env['account.account'].search(
            [('account_type', 'in', ('asset_receivable', 'liability_payable')),
             ('company_id', 'in', company_id)])
        if data['account_type']:
            accounts = self.env['account.account'].search(
                [('account_type', 'in',
                  ('asset_receivable', 'liability_payable')),
                 ('company_id', 'in', company_id)])

        partners = self.env['res.partner'].search([])
        if data['partner_tags']:
            partners = self.env['res.partner'].search(
                [('category_id', 'in', data['partner_tags'].ids)])
        if not accounts:
            raise UserError(_("No Accounts Found! Please Add One"))
        partner_res = self._get_partners(partners, accounts, init_balance,
                                         display_account, data)
        debit_total = 0
        debit_total = sum(x['debit'] for x in partner_res)
        credit_total = sum(x['credit'] for x in partner_res)
        # debit_balance = round(debit_total, 2) - round(credit_total, 2)
        debit_balance = debit_total - credit_total
        # print('data', {
        #     'doc_ids': self.ids,
        #     'debit_total': debit_total,
        #     'credit_total': credit_total,
        #     'debit_balance': debit_balance,
        #     'docs': docs,
        #     'time': time,
        #     'Partners': partner_res,
        # })
        return {
            'doc_ids': self.ids,
            'debit_total': debit_total,
            'credit_total': credit_total,
            'debit_balance': debit_balance,
            'docs': docs,
            'time': time,
            'Partners': partner_res,
        }

    def _get_partners(self, partners, accounts, init_balance, display_account,
                      data, asset_receivable=None):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        move_lines = {x: [] for x in partners.ids}
        currency_id = self.env.company.currency_id
        tables, where_clause, where_params = move_line._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        final_filters = " AND ".join(wheres)
        final_filters = final_filters.replace('account_move_line__move_id',
                                              'm').replace(
            'account_move_line', 'l')
        new_final_filter = final_filters
        if data['target_move'] == 'posted':
            new_final_filter += " AND m.state = 'posted'"
        else:
            new_final_filter += " AND m.state in ('draft','posted')"
        if data.get('date_from'):
            new_final_filter += " AND l.date >= '%s'" % data.get('date_from')
        if data.get('date_to'):
            new_final_filter += " AND l.date <= '%s'" % data.get('date_to')

        if data['journals']:
            new_final_filter += ' AND j.id IN %s' % str(
                tuple(data['journals'].ids) + tuple([0]))
        if data.get('accounts'):
            WHERE = "WHERE l.account_id IN %s" % str(
                tuple(data.get('accounts').ids) + tuple([0]))
        else:
            WHERE = "WHERE l.account_id IN %s"

        if data.get('partners'):
            WHERE += ' AND p.id IN %s' % str(
                tuple(data.get('partners').ids) + tuple([0]))

        if data.get('reconciled') == 'unreconciled':
            WHERE += ' AND l.full_reconcile_id is null AND' \
                     ' l.balance != 0 AND acc.reconcile is true'

        if data.get('account_type') == 'asset_receivable':
            WHERE += " AND acc.account_type = 'asset_receivable' "

        elif data.get('account_type') == 'liability_payable':
            WHERE += " AND acc.account_type = 'liability_payable' "

        sql = ('''SELECT l.id AS lid,l.partner_id AS partner_id,
                m.id AS move_id, 
                l.account_id AS account_id, l.date AS ldate, 
                acc.account_type AS account_type,
                j.code AS lcode, l.currency_id, 
                l.amount_currency, l.ref AS lref, l.name AS lname, 
                COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, 
                COALESCE(SUM(l.balance),0) AS balance,
                m.name AS move_name, c.symbol AS currency_code,c.position
                AS currency_position, p.name AS partner_name
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                JOIN account_account acc ON (l.account_id = acc.id)
                ''' + WHERE + new_final_filter +
               ''' GROUP BY l.id, m.id,  
                l.account_id, l.date, j.code, l.currency_id, 
                l.amount_currency, l.ref, l.name, m.name, c.symbol, 
                c.position, p.name, acc.account_type ORDER BY l.date
                '''
               )
        if data.get('accounts'):
            params = tuple(where_params)
        else:
            params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)
        account_list = {x.id: {'name': x.name, 'code': x.code} for x in
                        accounts}
        a=cr.dictfetchall()
        for row in a:
            balance = 0
            if row['partner_id'] in move_lines:
                for line in move_lines.get(row['partner_id']):
                    balance += line['debit'] - line['credit']
                row['balance'] += balance
                row['m_id'] = row['account_id']
                row['account_name'] = account_list[row['account_id']][
                                          'name'] + "(" + \
                                      account_list[row['account_id']][
                                          'code'] + ")"
                move_lines[row.pop('partner_id')].append(row)

        partner_res = []
        for partner in partners:
            company_id = self.env.company
            currency = company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['name'] = partner.name
            res['id'] = partner.id
            res['move_lines'] = move_lines[partner.id]
            for line in res.get('move_lines'):
                # res['debit'] += round(line['debit'], 2)
                # res['credit'] += round(line['credit'], 2)
                # res['balance'] = round(line['balance'], 2)
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                partner_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                partner_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                partner_res.append(res)
        return partner_res
