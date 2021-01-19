# -*- coding: UTF-8 -*-

from odoo import api, fields, models, tools
from odoo import tools, _
import logging
_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    study_visit_ids = fields.Many2many(comodel_name="outplacement.study_visit")
    
    obstacle_reason = fields.Selection([
        ('loan', 'Kan inte ta studielån'), 
        ('sickness', 'På grund utav sjukdom'), 
        ('economy', 'På grund utav ekonomisk situation'), 
        ('other', 'Annat')
        ])
    obstacle_motivation = fields.Text(string="Motivation")
    
    send_date = fields.Datetime(string="Final report send date")
    report_date = fields.Datetime(string="Reporting date")

    main_goal_id = fields.Many2one(comodel_name="outplacement.goal")
    alternative_goal_id = fields.Many2one(comodel_name="outplacement.goal")

class OutplacementGoal(models.Model):
    _name = "outplacement.goal"

    field_of_work_id = fields.Many2one(comodel_name="res.ssyk", string="Field of work") #return codes for these two
    job_id = fields.Many2one(comodel_name="res.ssyk", string="Job title") #selection should be limited to search ilike field_of_work.code
    job_description = fields.Char(string="Job description")
    motivation = fields.Selection(selection=[
        ('matches interest','Matchar deltagarens intressen'),
        ('matches ability','Arbetsuppgifter matchar förmåga'),
        ('market demand','Efterfrågan på arbetsmarknaden'),
        ('complementing education','Kompletterar nuvarande utbildning'),
        ('complementing experience','kompletterar tidigare erfarenheter'),
        ('other', 'Other')
        ], string="Motivation") 
    free_text = fields.Char(string="Free text") #should only be used if motivation is "other"
    step_ids = fields.Many2many(comodel_name="outplacement.goal.step", string="Step")

class OutplacementGoalStep(models.Model):
    _name = "outplacement.goal.step"

    #step type should be a series of boolean fields, but due to current API behaviour will be a selection field
    step_type = fields.Selection(selection=[('study', 'Studera'),
        ('regular education','Reguljär utbildning'),
        ('fitting complementing efforts','Lämpliga kompletterande insatser'),
        ('other','Other')], string="Type") #needs values
    complementing_effort_type = fields.Selection(string="Complementing effort type", selection=[
        ('study motivating effort','Studiemotiverande insats'),
        ('prepare for work','Rusta inför arbete'),
        ('match to work','Matcha till arbete'),
        ('evaluate ability to work','Utreda arbetsförmågan'),
        ('partake in education/internship/validation','Delta i en arbetsmarknadsutbildning/Praktik/Validering'),
        ('Swedish studies in chosen field','Svenskastudier inom valt område'),
        ('translation of grades','Översättning av betyg'),
        ('evaluation and complementation of foreign education','Bedömning och komplettering av utländsk utbildning'),
        ('other','Other')
        ]) #might be better as a selection field
    complementing_effort_description = fields.Char(string="Complementing effort") #this and the field above should only be visible if fitting complementing efforts is chosen #
    name = fields.Char(string="Name")
    sun_id = fields.Many2one(string="Educaiton Level", comodel_name="res.sun")
    start_date = fields.Datetime(string="Start date")
    end_date = fields.Datetime(string="End date")

class OutplacementStudyVisit(models.Model):
    _name = "outplacement.study_visit"

    name = fields.Char(string="Name")
    visit_type = fields.Char(string="Type") #needs values
    reasoning = fields.Text(string="Reasoning") #should only be used if visit_type is "other" 
    