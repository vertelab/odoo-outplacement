# coding: utf-8

import logging

# noinspection PyProtectedMember
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from xmlrpc.client import ServerProxy

_logger = logging.getLogger(__name__)

try:
    import odoorpc
except ImportError:
    _logger.info("outplacement_crmsync needs odoorpc. pip install odoorpc")
    raise


class crm_server(object):
    def __init__(self, env):

        self.server_url = (
            env["ir.config_parameter"]
            .sudo()
            .get_param("outplacement_crmsync.server_url", "http[s]://<domain>")
        )
        self.server_port = (
            env["ir.config_parameter"]
            .sudo()
            .get_param("outplacement_crmsync.server_port", "8069")
        )
        self.server_db = (
            env["ir.config_parameter"]
            .sudo()
            .get_param("outplacement_crmsync.server_db", "database")
        )
        self.server_login = (
            env["ir.config_parameter"]
            .sudo()
            .get_param("outplacement_crmsync.server_login", "userid")
        )
        self.server_pw = (
            env["ir.config_parameter"]
            .sudo()
            .get_param("outplacement_crmsync.server_pw", "password")
        )

        self.url_common = f"{self.server_url}:{self.server_port}/xmlrpc/2/common"

        try:
            self.common = ServerProxy(self.url_common)
            self.uid = self.common.authenticate(
                self.server_db, self.server_login, self.server_pw, {}
            )
        except Exception as e:
            raise UserError(f"Login {e}")

        self.url_model = f"{self.server_url}:{self.server_port}/xmlrpc/2/object"
        try:
            self.model = ServerProxy(self.url_model)
        except Exception as e:
            raise UserError(f"Model {e} ")

    def execute(self, model, command, param):
        return self.model.execute_kw(
            self.server_db, self.uid, self.server_pw, model, command, param
        )


class crm_serverII(object):
    def __init__(self, env):
        # self.server_url =  env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_url','http[s]://%s')
        self.server_host = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_host', '<domain>')
        self.server_protocol = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_protocol',
                                                                           'jsonrpc+ssl')
        self.server_port = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_port', '8069')
        self.server_db = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_db', 'database')
        self.server_login = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_login', 'userid')
        self.server_pw = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_pw', 'password')

        try:
            self.common = odoorpc.ODOO(host=self.server_host, protocol=self.server_protocol, port=self.server_port)
            # self.common = odoorpc.ODOO(host="http://172.16.42.112",port=8069)
            # self.common = odoorpc.ODOO(host="172.16.42.112",port='8069')
            _logger.debug("crm_serverII INIT")
            self.common.login(db=self.server_db, login=self.server_login, password=self.server_pw)
            # self.common.login(db="odoocrm", login="admin", password="admin")
            _logger.debug("crm_serverII LOGIN")

        except Exception as e:
            raise UserError(f"Login {e}")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ToDo: Fix this!
    # Temporary fix to update jobseeker category. Should be removed before 2021-SEPT-01
    def update_jobseeker_data(self):
        job_categ_obj = self.env['res.partner.skat']
        for partner in self:
            try:
                xmlrpc = crm_serverII(self.env)
                rec = xmlrpc.common.env['res.partner'].partnersyncCrm2DafaSSN(
                    partner.social_sec_nr)
                if rec:
                    cat_id = rec.get('partner', {}).get('jobseeker_category_id')
                    if cat_id:
                        jobseeker_category = job_categ_obj.search(
                            [('name', '=', cat_id[1])], limit=1)
                        if jobseeker_category:
                            partner.sudo().jobseeker_category_id = jobseeker_category.id
                        else:
                            categ_code = rec.get('jobseeker_category_code', '')
                            category = job_categ_obj.sudo().create(
                                {'name': cat_id[1],
                                 'code': categ_code})
                            partner.sudo().jobseeker_category_id = category.id
            except Exception as e:
                _logger.error("Something went wrong when updating the"
                              f" Jobseeker category from CRM! {e}")
                raise UserError(str(e))


class Outplacement(models.Model):
    _inherit = "outplacement"

    @api.multi
    def get_jobseeker_fields(self):
        return ["name", "street", "comment"]

    @api.one
    def check_connection(self):
        _logger.warning("CRMSYNC: testing connection..")
        xmlrpc = crm_serverII(self.env)
        _logger.warning("CRMSYNC xmlrpc object initialized")
        test = xmlrpc.common.env['res.partner'].browse(1)
        _logger.warning(f"CRMSYNC test: {test}")
        if test.id == 1:
            raise UserError("Connection established!")

    @api.one
    def get_jobseeker_dataV(self):
        FIELDS = [
            "title",
            "ref",
            "lang",
            "vat",
            "comment",
            "active",
            "supplier",
            "employee",
            "function",
            "type",
            "street",
            "street2",
            "zip",
            "city",
            "email",
            "phone",
            "mobile",
            "is_company",
            "color",
            "company_name",
            "firstname",
            "lastname",
            "name",
            # "education_level",
            # "foreign_education",
            # "foreign_education_approved",
            "cv",
            "cv_file_name",
            "references",
            "references_file_name",
            "has_car",
            "email_formatted",
            "company_type",
            "contact_address",
            "age",
            "jobseeker_category_id"
        ]
        email_to = self.env['ir.config_parameter'].sudo().get_param('system_parameter_to_send_api_error')
        model_obj = self.env['ir.model.data']
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        try:
            xmlrpc = crm_serverII(self.env)
            rec = xmlrpc.common.env['res.partner'].partnersyncCrm2DafaSSN(
                self.partner_social_sec_nr)
            _logger.debug(rec)
            if rec:
                self.partner_id.write({f: rec['partner'][f] if f != 'jobseeker_category_id' else '' for f in FIELDS})
                # education_ids
                self.partner_id.education_ids = [(6, 0, [])]
                cat_id = rec.get('partner', {}).get('jobseeker_category_id')
                if cat_id:
                    jobeeker_category = self.env['res.partner.skat'].search(
                        [('name', '=', cat_id[1])], limit=1)
                    if jobeeker_category:
                        self.partner_id.jobseeker_category_id = jobeeker_category.id
                    else:
                        categ_code = rec.get('jobseeker_category_code', '')
                        category = self.env['res.partner.skat'].sudo().create(
                            {'name': cat_id[1],
                             'code': categ_code})
                        self.partner_id.jobseeker_category_id = category.id
                for code, level, foreign, approved in rec['education_ids']:
                    self.partner_id.education_ids = [(0, 0, {
                        'sun_id': self.env['res.sun'].search(
                            [('code', '=', code)], limit=1)[0].id,
                        'education_level_id':
                            self.env['res.partner.education.education_level'].search([('name', '=', level)],
                                                                                     limit=1)[0].id,
                        'foreign_education': foreign,
                        'foreign_education_approved': approved
                    })]

                # drivers_license_ids
                self.partner_id.drivers_license_ids = [
                    (6, 0, [e.id for e in self.env['res.drivers_license'].search(
                        [('name', 'in', rec['drivers_license_ids'])])])]
                # job_ids
                self.partner_id.job_ids = [(6, 0, [])]
                for ssyk_code, exp_length, exp, edu, sun_code, edu_lvl, edu_f, edu_fa in rec['job_ids']:  # noqa: E501
                    ssyk_id = self.env['res.ssyk'].search(
                        [('code', '=', ssyk_code)], limit=1)[0]
                    _logger.debug(f'ssyk code: {ssyk_code} '
                                  f'ssyk id: {ssyk_id} '
                                  f'exp lenght: {exp_length} '
                                  f'exp: {exp}, edu: {edu}')
                    values = {
                        'partner_id': self.id,
                        'ssyk_id': ssyk_id,
                        'experience_length': exp_length,
                        'education': edu,
                        'experience': exp
                    }
                    sun_id = self.env['res.sun'].search(
                        [('code', '=', sun_code)], limit=1)[0]
                    edu_level = \
                        self.env['res.partner.education.education_level'].search(
                            [('name', '=', edu_lvl)], limit=1)[0]
                    education_id = self.env['res.partner.education'].search(
                        [('partner_id', '=', self.partner_id.id),
                         ('sun_id', '=', sun_id.id),
                         ('education_level_id', '=', edu_level.id),
                         ('foreign_education', '=', edu_f),
                         ('foreign_education_approved', '=', edu_fa)],
                        limit=1)[0]
                    _logger.debug(f'sun code: {sun_code}, sun_id: {sun_id}, '
                                  f'edu_lvl: {edu_lvl}, edu_level: {edu_level}, '
                                  f'edu_f: {edu_f}, edu_fa: {edu_fa}, '
                                  f'education_id: {education_id}')
                    values['education_id'] = education_id.id
                    self.partner_id.job_ids = [(0, 0, values)]
            else:
                raise UserError("Partner not found in CRM")
        except Exception as e:
            _logger.error(f"Something went wrong when Getting Jobseeker from CRM. {e}")
            if email_to:
                menu_id = model_obj.get_object_reference('outplacement', 'menu_outplacement')[1]
                action_id = model_obj.get_object_reference('outplacement', 'outplacement_action')[1]
                url = base_url + "/web?#id=" + str(
                    self.id) + "&view_type=form&model=outplacement&menu_id=" + str(
                    menu_id) + "&action=" + str(action_id)
                template = self.env.ref(
                    'outplacement_crmsync.email_temp_to_report_error_on_get_jobseeker_from_crm')
                mail = template.with_context(email_to=email_to, url=url,
                                             error_msg=str(e)).send_mail(self.id, force_send=True)
                mail = self.env['mail.mail'].browse(mail)
                mail.mail_message_id.body = (_('There was an error when getting Jobseeker from CRM.'))

            # ~ self.partner_id.job_ids = [0,0,(self.env['res.ssyk'].search([('code','=',code)],limit=1)[0],
            # ~ self.env['res.partner.education_level'].search([('name','=',level)],limit=1)[0],
            # ~ length,approved,experience)]

        # ~ self.partner_id.job_ids = [0,0,(self.env['res.ssyk'].search([('code','=','5')],limit=1)[0],
        # ~ self.env['res.partner.education_level'].search([('name','=','5')],limit=1)[0],3,True,True)]

    @api.one
    def get_af_management_team(self):
        """
        Test update management team
        """

        xmlrpc = crm_serverII(self.env)

        partner = xmlrpc.common.env["res.partner"].browse(
            xmlrpc.common.env["res.users"].search(
                [("email", "=", self.management_team_id.email)], limit=1
            )
        )
        # ~ xmlrpc.common.env['res.partner'].search([('id','=',26)],limit=1))
        if self.management_team_id._name == "hr.employee":
            self.management_team_id.write(
                {
                    "first_name": partner.first_name,
                    "last_name": partner.last_name,
                    "work_phone": partner.phone,
                    "work_email": partner.email,
                }
            )
        else:
            self.management_team_id.write(
                {
                    "first_name": partner.first_name,
                    "last_name": partner.last_name,
                    "street": partner.street,
                    "street2": partner.street2,
                    "zip": partner.zip,
                    "city": partner.city,
                    "phone": partner.phone,
                    "email": partner.email,
                }
            )
