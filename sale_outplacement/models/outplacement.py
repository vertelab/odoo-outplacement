# -*- coding: UTF-8 -*-

###############################################################################
#                                                                             #
#    OpenERP, Open Source Management Solution                                 #
#    Copyright (C) 2019 N-Development (<https://n-development.com>).          #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU Affero General Public License as           #
#    published by the Free Software Foundation, either version 3 of the       #
#    License, or (at your option) any later version.                          #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU Affero General Public License for more details.                      #
#                                                                             #
#    You should have received a copy of the GNU Affero General Public License #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #
###############################################################################


import datetime  # Used in test
import random  # Used in test
import string  # Used in test

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    outplacement_id = fields.Many2one(comodel_name='outplacement')


class Outplacement(models.Model):
    _inherit = 'outplacement'

    management_team_id = fields.Many2one(comodel_name='res.partner',
                                         string='Management team')
    skill_id = fields.Many2one('hr.skill')
    participitation_rate = fields.Integer()
    order_start_date = fields.Date()
    order_close_date = fields.Date()
    file_reference_number = fields.Char()
    task_ids = fields.Many2many(comodel_name='project.task', string='Tasks')
    order_id = fields.Many2one(comodel_name='sale.order')
    tasks_count = fields.Integer(compute='_compute_tasks_count')
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Analytic Account",
        copy=False,
        ondelete='set null',
        help="Link this outplacement to an analytic account if you need "
             "financial management. It enables you to connect "
             "outplacements with budgets, planning, cost and revenue "
             "analysis, timesheets.")

    # Temporary solution
    temp_lang = fields.Char(string='Language support requested')

    @api.onchange('employee_id')
    def _employee_activites(self):
        if self.employee_id:
            self.env['mail.activity'].search(
                ['&',
                 ('res_model_id.model', '=', self._name),
                 ('res_id', '=', self.id)]).unlink()
            for activity in self.order_id.mapped('order_line').filtered(
                "product_id.is_suborder").mapped(
                    'product_id.mail_activity_ids'):
                self.env['mail.activity'].create({
                    'res_id': self.id,
                    'res_model_id': self.env.ref(
                        'outplacement.model_outplacement').id,
                    'summary': activity.summary,
                    'user_id': self.employee_id.user_id.id if self.employee_id.user_id else None  # noqa:E501
                })

    def _compute_tasks_count(self):
        for record in self:
            record.tasks_count = len(record.task_ids)

    @api.multi
    def _get_partner(self, data):
        partner = self.env['res.partner'].search([
            '|',
            ('customer_id', '=', data['sokande_id']),
            ('social_sec_nr', '=', data['personnummer'])], limit=1)
        if len(partner) == 0:
            partner = self.env['res.partner'].create({
                'name': data['personnummer'],
                'customer_id': data['sokande_id'],
                'social_sec_nr': data['personnummer'],
            })
        return partner

    @api.multi
    def _get_management_team_id(self, data):
        management_team = self.env['res.partner'].search(
            [('email', '=', data['epost_handlaggargrupp'])], limit=1)

        if not management_team:
            management_team = self.env['res.partner'].create({
                'name': data['epost_handlaggargrupp'],
                'email': data['epost_handlaggargrupp'],
                'phone': data['telefonnummer_handlaggargrupp']
            })
        return management_team.id if management_team else None

    @api.multi
    def _get_department_id(self, data):
        department = self.env['performing.operation'].search(
            [('ka_nr', '=', data.get('utforande_verksamhet_id', ''))],
            limit=1)
        _logger.debug('Department: hr_department %s | %s' % (
            department, data.get('utforande_verksamhet_id')))
        return department.id if department else None

    @api.multi
    def _get_skill(self, data):
        return self.env['hr.skill'].search([
            ('name', '=', data['tjanstekod'])], limit=1)

    @api.model
    def suborder_process_data(self, data):
        _logger.info(data)
        data = super(Outplacement, self).suborder_process_data(data)
        partner = self._get_partner(data)

        skill = self._get_skill(data)
        order_lines = [
            (0, 0, {"product_id": self.env.ref(
                "sale_outplacement.startersattning").id}),
            (0, 0, {"product_id": self.env.ref(
                "sale_outplacement.slutersattning").id}),
        ]
        order = self.env['sale.order'].create({
            'origin': data['genomforande_referens'],
            'name': data['ordernummer'],
            'partner_id': partner.id,
            'order_line': order_lines,
        })
        outplacement = self.env['outplacement'].create({
            'name': data['ordernummer'],
            'performing_operation_id': self._get_department_id(data),
            'booking_ref': data['boknings_id'],
            'partner_id': partner.id,
            'skill_id': skill.id if skill else None,
            'participitation_rate': data['deltagandegrad'],
            'service_start_date': data['startdatum_insats'],
            'service_end_date': data['slutdatum_insats'],
            'order_start_date': data['startdatum_avrop'],
            'order_close_date': data['slutdatum_avrop'],
            'file_reference_number': data['aktnummer_diariet'],
            'management_team_id': self._get_management_team_id(data),
            'order_id': order.id,
        })
        interpreter_need = data.get('tolkbehov')
        lang = self.env['res.interpreter.language'].search(
            [('code', '=', interpreter_need)])
        partner.interpreter_language = lang.id if lang else False
        # Temporary hack until language is fixed in TLR
        if interpreter_need and not lang:
            outplacement.temp_lang = interpreter_need
        order.outplacement_id = outplacement.id
        self.env['project.task'].init_joint_planning(outplacement.id)
        self.env['project.task'].init_joint_planning_stages(outplacement.id)
        return data

    # For test. ToDo: Rename with a test in function name.
    @api.model
    def create_suborder_process_data(self):
        self.suborder_process_data({
            "genomforande_referens": ''.join(
                random.sample(string.digits, k=9)),
            "utforande_verksamhet_id": "10009858",
            "ordernummer": "MEET-" + ''.join(
                random.sample(string.digits, k=3)),
            "tidigare_ordernummer": "MEET-23",
            "boknings_id": ''.join(random.sample(string.digits, k=6)),
            "personnummer": "19701212" + ''.join(
                random.sample(string.digits, k=4)),
            "sokande_id": ''.join(random.sample(string.ascii_lowercase, k=5)) +
                          ''.join(random.sample(string.digits, k=4)),
            "tjanstekod": "KVL",
            "spar_kod": "10",
            "tolkbehov": "",
            "deltagandegrad": 75,
            "bokat_sfi": False,
            "startdatum_insats": '%s' % datetime.date.today(),
            "slutdatum_insats": str(
                datetime.date.today()+datetime.timedelta(days=365)),
            "startdatum_avrop": str(datetime.date.today()),
            "slutdatum_avrop": str(
                datetime.date.today()+datetime.timedelta(days=90)),
            "aktnummer_diariet": "Af-2021/0000 " +
                                 ''.join(random.sample(string.digits, k=4)),
            "telefonnummer_handlaggargrupp": "+46734176359",
            "epost_handlaggargrupp": ''.join(
                random.sample(string.digits, k=4)) + "@test.com"
            })

    @api.model
    def create(self, values):
        """
        Create an analytic account if project allow timesheet and don't
        provide one.
        Note: create it before calling super() to avoid raising the
        ValidationError from _check_allow_timesheet
        """
        if not values.get('analytic_account_id'):
            analytic_account = self.env['account.analytic.account'].create({
                'name': values.get('name', _('Unknown Analytic Account')),
                'company_id': values.get('company_id',
                                         self.env.user.company_id.id),
                'partner_id': values.get('partner_id'),
                'active': True,
            })
            values['analytic_account_id'] = analytic_account.id
        return super(Outplacement, self).create(values)

    @api.multi
    def unlink(self):
        """ Delete the empty related analytic account """
        analytic_accounts_to_delete = self.env['account.analytic.account']
        for outplacement in self:
            if (outplacement.analytic_account_id and not
                    outplacement.analytic_account_id.line_ids):
                analytic_accounts_to_delete |= outplacement.analytic_account_id
        result = super(Outplacement, self).unlink()
        analytic_accounts_to_delete.unlink()
        return result


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_id = fields.Char(string='Customer Number', size=64, trim=True, )
