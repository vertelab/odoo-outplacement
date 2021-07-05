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
        string = "Interpreter Type",
        readonly=False)
    interpreter_remote_type = fields.Many2one(
        related='partner_id.interpreter_type',
        string='Interpreter Remote Type',
        readonly=False)
    total_activity = fields.Integer(compute='compute_total_activity')

    def remove_booking_confirmed_repetative_log(self):
        msg_obj = self.env['mail.message']
        for record in self:
            tasks = self.env['project.task'].search([('outplacement_id', '=', record.id)])
            for task in tasks:
                messages = msg_obj.search([('res_id', '=', task.id), ('model', '=', 'project.task'),
                                           ('body', 'ilike', 'Tolkbokning är bekräftad')])
                if len(messages) > 1:
                    messages = messages[1:]
                    for msg in messages:
                        msg.unlink()

    def compute_total_activity(self):
        task_obj = self.env['project.task']
        activity_obj = self.env['mail.activity']
        for outplacement in self:
            tasks = task_obj.search([('outplacement_id', '=', outplacement.id)])
            activities = []
            if tasks:
                activities = activity_obj.search([('res_id', 'in', tasks.ids),
                                                  ('res_model', '=', 'project.task'), '|',
                                                  ('active', '=', True), ('active', '=', False)]).ids
            outplacement.total_activity = len(activities)

    def open_outplacement_activity(self):
        self.ensure_one()
        tasks = self.env['project.task'].search([('outplacement_id', '=', self.id)])
        activities = []
        if tasks:
            activities = self.env['mail.activity'].search([('res_id', 'in', tasks.ids),
                                                           ('res_model', '=', 'project.task'), '|',
                                                           ('active', '=', True), ('active', '=', False)]).ids
        action = self.env.ref('outplacement_order_interpreter.interpreter_activity_action').read([])[0]
        action['domain'] = [('id', 'in', activities), '|', ('active', '=', True), ('active', '=', False)]
        return action
