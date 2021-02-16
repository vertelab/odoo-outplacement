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
