from odoo import api, fields, models, tools
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

    report_date = fields.Datetime(string="Reporting date")
    status = fields.Selection(string="status", selection=[('10', 'Approved'), ('20', 'Not approved'), ('30', 'In-Progress'), ('40', 'Rejected'), ('50', 'Cancelled'), ('60', 'Sent')])
    late = fields.Boolean(string="Sent late")
    interruption = fields.Boolean(string="Interrupted")
    incomplete = fields.Boolean(string="Incomplete")

    main_goal_id = fields.Many2one(comodel_name="outplacement.goal")
    alternative_goal_id = fields.Many2one(comodel_name="outplacement.goal")

class OutplacementGoal(models.Model):
    _name = "outplacement.goal"

    field_of_work_id = fields.Many2one(comodel_name="res.ssyk", string="Field of work") #return codes for these two
    job_id = fields.Many2one(comodel_name="res.ssyk", string="Job title") #selection should be limited to search ilike field_of_work.code
    job_description = fields.Char(string="Job description")
    motivation = fields.Selection(selection=[('other', 'Other')], string="Motivation") #needs values
    free_text = fields.Text(string="Free text") #should only be used if motivation is "other"
    step_ids = fields.Many2many(comodel_name="outplacement.goal.step", string="Step")

class OutplacementGoalStep(models.Model):
    _name = "outplacement.goal.step"

    step_type = fields.Selection(selection=[('placeholder', 'placeholder')], string="Type") #needs values
    completing_effort_id = fields.Many2one(string="Completing effort", comodel_name="outplacement.goal.step.completing_effort") #might be better as a selection field
    name = fields.Char(string="Name")
    level = fields.Char(string="Level") #selection field maybe?
    start_date = fields.Datetime(string="Start date")
    end_date = fields.Datetime(string="End date")

class OutplacementGoalStepCompletingEffort(models.Model): #effort should probably be replaced with a more fitting word
    _name = "outplacement.goal.step.completing_effort" 

    effort_type = fields.Char(string="Effort type") #selection field?


class OutplacementObstacle(models.Model):
    _name = "outplacement.obstacle"
    
    reason = fields.Selection([('loan', 'Kan inte ta studielån'), ('sickness', 'På grund utav sjukdom'), ('economy', 'På grund utav ekonomisk situation'), ('other', 'Annat')])
    motivation = fields.Text(string="Motivation")

class OutplacementStudyVisit(models.Model):
    _name = "outplacement.study_visit"

    name = fields.Char(string="Name")
    visit_type = fields.Selection(string="Type", selection=[('other', 'Other')]) #needs values
    reasoning = fields.Text(string="Reasoning") #should only be used if visit_type is "other" 
    