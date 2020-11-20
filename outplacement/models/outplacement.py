import base64
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource


class Outplacement(models.Model):
    _name = 'outplacement'
    _description = 'Outplacement'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    @api.model
    def _default_image(self):
        image_path = get_module_resource('outplacement', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    def _default_stage_id(self):
        return self.env['outplacement.stage'].search([('fold', '=', False)], limit=1)

    name = fields.Char(string="Name")
    stage_id = fields.Many2one('outplacement.stage', strin="State",
                            ondelete='restrict', track_visibility='onchange', index=True, copy=False,
                            group_expand='_read_group_stage_ids',
                            default=lambda self: self._default_stage_id()
                            )
    employee_id = fields.Many2one('hr.employee', string="Employee") # Nils: Change?
    date_begin = fields.Datetime(string="Start Date", required=True)
    date_end = fields.Datetime(string="End Date", required=True)
    color = fields.Integer('Kanban Color Index')
    
    # TODO!
    # Nils: Remove Image as we have no image of the jobseeker?
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Photo", default=_default_image, attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")

    # Nils: If image is removed this should be removed as well.
    @api.onchange('employee_id')
    def _employee_image(self):
        if self.employee_id:
            self.image = self.employee_id.image

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Always display all stages """
        return stages.search([], order=order)

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        employee = super(Outplacement, self).create(vals)
        return employee

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        res = super(Outplacement, self).write(vals)
        return res


class OutplacementStage(models.Model):
    _name = 'outplacement.stage'
    _description = 'Outplacement Stage'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    fold = fields.Boolean(string="Fold")
    template_id = fields.Many2one('mail.template', string="Mail Template")
