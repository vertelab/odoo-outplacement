import base64
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource


class ProjectTask(models.Model):
    _inherit = 'project.task'

    outplacement_id = fields.Many2one(comodel_name='outplacement', String='Outplacement', index=True,default=lambda self: self.env.context.get('default_project_id'))
    activity_id = fields.Many2one('res.joint_planning', 'Activity')
    joint_planing_type = fields.Selection([
        ('kvl', 'KVL'),
        ('preplaning', 'Preplaning'),
        ('endraport', 'Endraport'),
    ], 'JP_Type')
    task_type = fields.Selection(selection=[('mandatory', 'Mandatory'),
                                            ('optional', 'Optional'), ],
                                 string='Task Type', )
    
    @api.model
    def init_joint_planning(self,outplacement_id):
        for task in self.env['res.joint_planning'].search([],order='sequence'):
            self.env['project.task'].create({
                'outplacement_id': outplacement_id,
                'joint_planning_type': 'preplanning',
                'task_type': task.task_type,
                'activity_id': task.id,
                'name': task.name,
            })
            
    @api.onchange('outplacement.id')
    def _onchange_outplacement(self):
        if self.outplacement_id:
            if not self.parent_id and self.project_id.partner_id:
                self.partner_id = self.project_id.partner_id
            if self.project_id not in self.stage_id.project_ids:
                self.stage_id = self.stage_find(self.project_id.id, [('fold', '=', False)])
        else:
            self.stage_id = False
