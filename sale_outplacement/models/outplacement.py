import base64
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)

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
        })
        return data

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    customer_id = fields.Char(string='Customer number', help="Customer number")
