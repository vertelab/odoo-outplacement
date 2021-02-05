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

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    outplacement_id = fields.Many2one(comodel_name='outplacement')


class Outplacement(models.Model):
    _inherit = 'outplacement'

    management_team_id = fields.Many2one(comodel_name='res.users',
                                         string='Management team')
    skill_id = fields.Many2one('hr.skill')
    participitation_rate = fields.Integer()
    order_start_date = fields.Date()
    order_close_date = fields.Date()
    file_reference_number = fields.Char()
    task_ids = fields.Many2many(comodel_name='project.task', string='Tasks')
    order_id = fields.Many2one(comodel_name='sale.order')
    tasks_count = fields.Integer(compute='_compute_tasks_count')

    @api.onchange('employee_id')
    def _employee_activites(self):
        if self.employee_id:
            self.env['mail.activity'].search(
                ['&',
                 ('res_model_id.model', '=', self._name),
                 ('res_id', '=', self.id)]).unlink()
            for activity in self.order_id.mapped('order_lines').filtered(
                "product_id.is_suborder").mapped(
                    'product_id.mail_activites'):
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
    def _get_partner_id(self, data):
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
        return partner.id if partner else None

    @api.multi
    def _get_management_team_id(self, data):
        management_team = self.env['res.users'].search(
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
        data = super(Outplacement, self).suborder_process_data(data)
        partner_id = self._get_partner_id(data)

        skill = self._get_skill(data)
        order = self.env['sale.order'].create({
            'origin': data['genomforande_referens'],
            'name': data['ordernummer'],
            'partner_id': partner_id,
        })
        product = self.env.ref('sale_outplacement.product_suborder')
        self.env['sale.order.line'].create({
            'product_id': product.id,
            'order_id': order.id,
        })
        outplacement = self.env['outplacement'].create({
            'name': data['ordernummer'],
            'performing_operation_id': self._get_department_id(data),
            'booking_ref': data['boknings_id'],
            'partner_id': partner_id,
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
            "sprakstod": "Tyska",
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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_id = fields.Char(string='Customer Number', size=64, trim=True, )
