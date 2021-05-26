import logging

from odoo import models, api, fields  # noqa:F401

_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = "outplacement"

    interpreter_language = fields.Many2one(
        related="partner_id.interpreter_language",
        readonly=False)
    interpreter_gender_preference = fields.Many2one(
        related="partner_id.interpreter_gender_preference",
        readonly=False)
    interpreter_type = fields.Many2one(
        related='partner_id.interpreter_type',
        readonly=False)
    interpreter_remote_type = fields.Many2one(
        related='partner_id.interpreter_type',
        readonly=False)

    def remove_booking_confirmed_repetative_log(self):
        msg_obj = self.env['mail.message']
        for record in self:
            tasks = self.env['project.task'].search([('outplacement_id', '=', record.id)])
            for task in tasks:
                messages = msg_obj.search([('res_id','=',task.id),('model', '=', 'project.task'),
                                ('body', 'ilike', 'Tolkbokning är bekräftad')])
                if len(messages) > 1:
                    messages = messages[1:]
                    for msg in messages:
                        msg.unlink()