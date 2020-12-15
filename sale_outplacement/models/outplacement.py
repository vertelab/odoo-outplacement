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

class Outplacement(models.Model):
    _inherit = 'outplacement'

    departement_id = fields.Many2one('hr.department')
    booking_ref = fields.Char()
    partner_id = fields.Many2one('res.partner')
    management_team_id = fields.Many2one('res.partner')
    # ~ skill_id = fields.Many2one('hr.skill')
    participitation_rate = fields.Integer()
    service_start_date = fields.Date()
    service_end_date = fields.Date()
    order_close_date = fields.Date()
    file_reference_number = fields.Char()
    task_ids = fields.Many2many('project.task', string='Tasks')
    order_id = fields.Many2one('sale.order')
    tasks_count = fields.Integer(compute='_compute_tasks_count')

    def _compute_tasks_count(self):
        for record in self:
            record.tasks_count = len(record.task_ids)

    @api.multi
    def _get_partner(self, data):
        partner = ResPartner = self.env['res.partner']
        try:
            partner = ResPartner.search([
                ('customer_id', '=', data['sokande_id'])], limit=1)
        except Exception:
            pass
        if not partner:
            try:
                partner = ResPartner.search([
                    ('social_sec_nr_age', '=', data['personnummer'])], limit=1)
            except Exception:
                pass
        if not partner:
            partner = ResPartner.create({
                'name': data['personnummer'],
                'customer_id': data['sokande_id'],
            })
        return partner

    @api.multi
    def _get_management_team(self, data):
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
        return partner

    @api.multi
    def _get_department(self, data):
        return self.env['hr.department'].search([
            ('ka_ref', '=', data['utforande_verksamhet_id'])
        ], limit=1)

    @api.multi
    def _get_skill(self, data):
        return self.env['hr.skill'].search([
            ('name', '=', data['tjanstekod'])
        ], limit=1)

    @api.model
    def suborder_process_data(self, data):
        _logger.warn('Nisse: %s suborder_process_data outplacement' % data)
        data = super(Outplacement,self).suborder_process_data(data)
        _logger.warn('Nisse: suborder_process_data outplacement after super')
        partner = self._get_partner(data)
        management_team = self._get_management_team(data)
        department = self._get_department(data)
        # ~ skill = self._get_skill(data)
        order = self.env['sale.order'].create({
            'origin': data['genomforande_referens'],
            'name': data['ordernummer'],
            'partner_id': partner.id,
        })
        product = self.env.ref('sale_outplacement.product_suborder')
        task_ids = self.env['res.joint_planning'].search([])
        self.env['sale.order.line'].create({
            'product_id': product.id,
            'order_id': order.id,
        })
        self.env['outplacement'].create({
            'name': data['ordernummer'],
            'departement_id': department and department.id or False,
            'booking_ref': data['boknings_id'],
            'partner_id': partner.id,
            # ~ 'skill_id': skill and skill.id or False,
            'participitation_rate': data['deltagandegrad'],
            'service_start_date': data['startdatum_insats'],
            'service_end_date': data['slutdatum_insats'],
            'date_begin': data['startdatum_insats'],
            'date_end': data['slutdatum_insats'],
            'order_close_date': data['slutdatum_avrop'],
            'file_reference_number': data['aktnummer_diariet'],
            'management_team_id': management_team.id,
            'order_id': order.id,
            'task_ids': [(6, 0, task_ids)],
        })
        MailActivity = self.env['mail.activity']
        if product.is_suborder:
            for activity in product.mail_activity_ids:
                MailActivity.create({
                    'res_id': self.id,
                    'res_model': self._name,
                    'activity_type_id': activity.activity_type_id,
                    'date_deadline': fields.Date.today() + relativedelta(days=activity.due_days),
                    'summary': activity.summary,
                    'user_id': self.employee_id.user_id
                })
        return data

    def action_project_task(self):
        return {
            'name': _('Product Task'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.task',
        }
