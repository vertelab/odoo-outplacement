from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo import tools, _
import logging
_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    study_visit_ids = fields.Many2many(comodel_name="outplacement.study_visit")
    obstacle_id = fields.Many2one(comodel_name="outplacement.obstacle")

    obstacle_reason = fields.Selection(related="obstacle_id.reason", readonly=False)
    obstacle_motivation = fields.Text(related="obstacle_id.motivation", readonly=False)

    send_date = fields.Datetime(string="Final report send date")


class OutplacementObstacle(models.Model):
    _name = "outplacement.obstacle"
    
    outplacement_id = fields.One2many(comodel_name="outplacement", inverse_name="obstacle_id")
    reason = fields.Selection([('loan', 'Kan inte ta studielån'), ('sickness', 'På grund utav sjukdom'), ('economy', 'På grund utav ekonomisk situation'), ('other', 'Annat')])
    motivation = fields.Text(string="Motivation")

class OutplacementStudyVisit(models.Model):
    _name = "outplacement.study_visit"

    outplacement_ids = fields.One2many(comodel_name="outplacement")
    name = fields.Char(string="Name")
    visit_type = fields.Char(string="Type")
    reasoning = fields.Text(string="Reasoning")
    