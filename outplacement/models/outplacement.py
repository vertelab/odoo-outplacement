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
    employee_id = fields.Many2one('hr.employee', string="Coach")
    department_id = fields.Many2one('hr.department')
    date_begin = fields.Datetime(string="Start Date", required=True)
    date_end = fields.Datetime(string="End Date", required=True)
    color = fields.Integer('Kanban Color Index')
    meeting_remote = fields.Selection(selection=[('no','On Premice'),('yes','Remote')],string='Meeting type')
    
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
    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char(related='partner_id.name')
    booking_ref = fields.Char()
    service_start_date = fields.Date()
    service_end_date = fields.Date()
    department_id = fields.Many2one('hr.department')
    my_department = fields.Boolean(compute='_compute_my_department',
                                   search='_search_my_department')
    my_outplacement = fields.Boolean(compute='_compute_my_outplacement',
                                     search='_search_my_outplacement')
    sprakstod = fields.Char()

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
    def _read_group_employee_id(self, stages, domain, order):
        """ Always display all stages """
        return self['hr.employee'].search([], order=order)

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

    def _compute_my_department(self):
        pass

    def _search_my_department(self, operator, value):
        user_employee = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1)
        res = []
        if user_employee and user_employee.department_id:
            res = self.search([
                ('department_id', '=', user_employee.department_id.id)]).ids
        return [('id', operator, res)]

    def _compute_my_outplacement(self):
        pass

    def _search_my_outplacement(self, operator, value):
        user_employee = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1)
        res = []
        if user_employee and user_employee.department_id:
            res = self.search([
                ('employee_id', '=', user_employee.id)]).ids
        return [('id', operator, res)]

    @api.multi
    def _track_template(self, tracking):
        res = super(Outplacement, self)._track_template(tracking)
        applicant = self[0]
        changes, dummy = tracking[applicant.id]
        if 'stage_id' in changes and applicant.stage_id.template_id:
            res['stage_id'] = (applicant.stage_id.template_id, {
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'notif_layout': 'mail.mail_notification_light'
            })
        return res

    @api.multi
    def _notify_get_reply_to(self, default=None, records=None, company=None, doc_names=None):
        """ Override to set alias of applicants to their job definition if any. """
        aliases = self.mapped('job_id')._notify_get_reply_to(default=default, records=None, company=company, doc_names=None)
        res = {app.id: aliases.get(app.job_id.id) for app in self}
        leftover = self.filtered(lambda rec: not rec.job_id)
        if leftover:
            res.update(super(Outplacement, leftover)._notify_get_reply_to(default=default, records=None, company=company, doc_names=doc_names))
        return res

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(Outplacement, self).message_get_suggested_recipients()
        for applicant in self:
            if applicant.partner_id:
                applicant._message_add_suggested_recipient(recipients, partner=applicant.partner_id, reason=_('Contact'))
            elif applicant.email_from:
                applicant._message_add_suggested_recipient(recipients, email=applicant.email_from, reason=_('Contact Email'))
        return recipients

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        self = self.with_context(default_user_id=False)
        val = msg.get('from').split('<')[0]
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'partner_name': val,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        if custom_values:
            defaults.update(custom_values)
        return super(Outplacement, self).message_new(msg, custom_values=defaults)

    def _message_post_after_hook(self, message, *args, **kwargs):
        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email_from)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email_from', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        return super(Outplacement, self)._message_post_after_hook(message, *args, **kwargs)

class OutplacementStage(models.Model):
    _name = 'outplacement.stage'
    _description = 'Outplacement Stage'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    fold = fields.Boolean(string="Fold")
    template_id = fields.Many2one('mail.template', string="Mail Template")
