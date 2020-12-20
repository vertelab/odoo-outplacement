# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


import logging
_logger = logging.getLogger(__name__)

class Outplacement(models.Model):
    _inherit = 'outplacement'

    management_team_id = fields.Many2one('res.partner')
    # ~ skill_id = fields.Many2one('hr.skill')
    participitation_rate = fields.Integer()
    order_close_date = fields.Date()
    file_reference_number = fields.Char()
    task_ids = fields.Many2many('project.task', string='Tasks')
    order_id = fields.Many2one('sale.order')
    tasks_count = fields.Integer(compute='_compute_tasks_count')

    @api.onchange('employee_id')
    def _employee_activites(self):
        if self.employee_id:
            self.env['mail.activity'].search(
                ['&', 
                 ('res_model_id.model', '=', self._name), 
                 ('res_id', '=', self.id)]).unlink()
            for activity in self.order_id.mapped('order_lines').filtered(lambda l: l.product_id.is_suborder == True).mapped('product_id.mail_activites'):
                self.env['mail.activity'].create({
                    'res_id': self.id,
                    'res_model_id': self.env.ref('outplacement.model_outplacement').id,
                    'summary': activity.summary,
                    # ~ 'date':    fields.Datetime.to_string(fields.Datetime.from_string(values['date_from']) + timedelta(minutes = abs(minutes))),
                    'user_id': self.employee_id.user_id.id if self.employee_id.user_id else None
                })



    def _compute_tasks_count(self):
        for record in self:
            record.tasks_count = len(record.task_ids)

    @api.multi
    def _get_partner_id(self, data):
        partner=self.env['res.partner'].search(['|',
                ('customer_id', '=', data['sokande_id']),
                ('company_registry', '=', data['personnummer'])],limit=1)
        if len(partner) == 0:
            partner = self.env['res.partner'].create({
                'name': data['personnummer'],
                'customer_id': data['sokande_id'],
            })
        return partner.id if partner else None

    @api.multi
    def _get_management_team_id(self, data):
        ResPartner = self.env['res.partner']
        partner = ResPartner.search([
            ('phone', '=', data['telefonnummer_handlaggargrupp'])
        ])
        if not partner:
            ResPartner.create({
                'name': data['epost_handlaggargrupp'],
                'email': data['epost_handlaggargrupp'],
                'phone': data['telefonnummer_handlaggargrupp'],
            })
        return partner.id if partner else None

    @api.multi
    def _get_department_id(self, data):
        department = self.env['hr.department'].search(
            [('ka_ref', '=', data.get('utforande_verksamhet_id',''))],
            limit=1)
        _logger.debug('Department: hr_department %s | %s' % (department,data.get('utforande_verksamhet_id')))
        return department.id if department else None

    @api.multi
    def _get_skill(self, data):
        return self.env['hr.skill'].search([
            ('name', '=', data['tjanstekod'])
        ], limit=1)

    @api.model
    def suborder_process_data(self, data):
        _logger.warn('Nisse: %s suborder_process_data outplacement' % data)
        data = super(Outplacement,self).suborder_process_data(data)
        partner_id = self._get_partner_id(data)

        # ~ skill = self._get_skill(data)
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
        _logger.warn('Nisse: outplacement %s' % order)
        outplacement = self.env['outplacement'].create({
            'name': data['ordernummer'],
            'department_id': self._get_department_id(data),
            'booking_ref': data['boknings_id'],
            'partner_id': partner_id,
            'partner_id': 8,
            # ~ 'skill_id': skill and skill.id or False,
            'participitation_rate': data['deltagandegrad'],
            'service_start_date': data['startdatum_insats'],
            'service_end_date': data['slutdatum_insats'],
            'date_begin': data['startdatum_insats'],
            'date_end': data['slutdatum_insats'],
            'order_close_date': data['slutdatum_avrop'],
            'file_reference_number': data['aktnummer_diariet'],
            'management_team_id': self._get_management_team_id(data),
            'order_id': order.id,
        })
        self.env['project.task'].init_joint_planning(outplacement.id)
        self.env['project.task'].init_joint_planning_stages(outplacement.id)
        _logger.warn('Nisse: outplacement %s' % dir(outplacement))
        return data


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_id = fields.Char(string='Cuhatomer Number', size=64, trim=True, )
    
