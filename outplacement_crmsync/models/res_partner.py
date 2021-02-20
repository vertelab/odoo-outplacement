# coding: utf-8

from xmlrpc.client import ServerProxy
from odoo import api, fields, models
from odoo.exceptions import Warning
import odoorpc
import pprint

import logging

_logger = logging.getLogger(__name__)


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
            raise Warning("Login %s" % e)

        self.url_model = f"{self.server_url}:{self.server_port}/xmlrpc/2/object"
        try:
            self.model = ServerProxy(self.url_model)
        except Exception as e:
            raise Warning("Model %s " % e)

    def execute(self, model, command, param):
        return self.model.execute_kw(
            self.server_db, self.uid, self.server_pw, model, command, param
        )


class crm_serverII(object):
    def __init__(self, env):
        # self.server_url =  env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_url','http[s]://%s')
        self.server_host =  env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_host','<domain>')
        self.server_protocol =  env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_protocol','jsonrpc+ssl')
        self.server_port = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_port','8069')
        self.server_db =   env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_db','database')
        self.server_login = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_login','userid')
        self.server_pw =   env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_pw','password')

        try:
            self.common = odoorpc.ODOO(host=self.server_host,protocol=self.server_protocol,port=self.server_port)
            # self.common = odoorpc.ODOO(host="http://172.16.42.112",port=8069)
            # self.common = odoorpc.ODOO(host="172.16.42.112",port='8069')
            _logger.warn("DAER crm_serverII INIT")
            self.common.login(db=self.server_db,login=self.server_login,password=self.server_pw)
            # self.common.login(db="odoocrm", login="admin", password="admin")
            _logger.warn("DAER crm_serverII LOGIN")

        except Exception as e:
            raise Warning("Login %s" % e)


class Outplacement(models.Model):
    _inherit = "outplacement"

    @api.multi
    def get_jobseeker_fields(self):
        return ["name", "street", "comment"]

    @api.one
    def check_connection(self):

        _logger.warn("CRMSYNC: testing connection..")
        xmlrpc = crm_serverII(self.env)
        _logger.warn("CRMSYNC xmlrpc object initialized")
        test = xmlrpc.common.env['res.partner'].browse(1)
        _logger.warn("CRMSYNC test: %s" % test)
        if test.id == 1:
            raise Warning("Connection established!")

    @api.one
    def get_jobseeker_dataII(self):

        xmlrpc = crm_serverII(self.env)

        partner = xmlrpc.common.env["res.partner"].browse(
            xmlrpc.common.env["res.partner"].search(
                [("social_sec_nr", "=", self.social_sec_nr)], limit=1
            )
        )
        # ~ xmlrpc.common.env['res.partner'].search([('id','=',26)],limit=1))

        self.write(
            {
                "name": partner.name,
                "street": partner.street,
                "street2": partner.street2,
                "zip": partner.zip,
                "city": partner.city,
                "phone": partner.phone,
                "email": partner.email,
                #
                # outplacement_education
                #
                "education_ids": [
                    (
                        6,
                        0,
                        [
                            e.id
                            for e in self.env["res.partner.education"].search(
                                [
                                    (
                                        "sun_id",
                                        "in",
                                        partner.education_ids.mapped("sun_id"),
                                    )
                                ]
                            )
                        ],
                    )
                ],
                "cv": partner.cv,
                "cv_file_name": partner.cv_file_name,
                "references": partner.references,
                "references_file_name": partner.references_file_name,
                "has_drivers_license": partner.has_drivers_license,
                "drivers_license_ids": [
                    (
                        6,
                        0,
                        [
                            e.id
                            for e in self.env["res.drivers_license"].search(
                                [
                                    (
                                        "name",
                                        "in",
                                        partner.drivers_license_ids.mapped("name"),
                                    )
                                ]
                            )
                        ],
                    )
                ],
                "has_car": partner.has_car,
                # ~ # jobs
                "job_ids": [
                    (
                        6,
                        0,
                        [
                            e.id
                            for e in self.env["res.jobs"].search(
                                [("name", "in", partner.job_ids.mapped("name"))]
                            )
                        ],
                    )
                ],
                # skills
                # ~ skills = fields.Many2many('hr.skill', string="Skill")
                # ~ skill_id = fields.Char(string="Skill", related="skills.complete_name")
                # ~ other_experiences = fields.Many2many(comodel_name='outplacement.other_experiences', string="Other Experience")
                # ~ strengths = fields.Many2many(comodel_name='outplacement.strengths', string="Strengths")
                # ~ interests = fields.Many2many(comodel_name='outplacement.interests', string="Interests")
                # ~ partner_skill_ids = fields.One2many(
                # ~ string='Skills',
                # ~ comodel_name='hr.employee.skill',
                # ~ inverse_name='partner_id',
                # ~ )
            }
        )

    @api.one
    def get_jobseeker_dataIII(self):
        """
        Test utan komplexa data
        """

        xmlrpc = crm_serverII(self.env)

        partner = xmlrpc.common.env["res.partner"].browse(
            xmlrpc.common.env["res.partner"].search(
                [("social_sec_nr", "=", self.social_sec_nr)], limit=1
            )
        )
        # ~ xmlrpc.common.env['res.partner'].search([('id','=',26)],limit=1))

        self.write(
            {
                "name": partner.name,
                "street": partner.street,
                "street2": partner.street2,
                "zip": partner.zip,
                "city": partner.city,
                "phone": partner.phone,
                "email": partner.email,
            }
        )

    @api.one
    def get_jobseeker_dataIV(self):
        """
        Test mot demo-data / utan partner_ssn
        """

        xmlrpc = crm_serverII(self.env)

        partner = xmlrpc.common.env["res.partner"].browse(
            xmlrpc.common.env["res.partner"].search([("id", "=", 26)], limit=1)
        )
        # ~ xmlrpc.common.env['res.partner'].search([('id','=',26)],limit=1))

        self.write(
            {
                "name": partner.name,
                "street": partner.street,
                "street2": partner.street2,
                "zip": partner.zip,
                "city": partner.city,
                "phone": partner.phone,
                "email": partner.email,
            }
        )

    @api.one
    def get_jobseeker_dataV(self):
        FIELDS = [
            "title",
            "ref",
            "lang",
            "vat",
            "comment",
            "active",
            "customer",
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
            "additional_info",
            "education_level",
            "foreign_education",
            "foreign_education_approved",
            "cv",
            "cv_file_name",
            "references",
            "references_file_name",
            "has_car",
            "email_formatted",
            "company_type",
            "contact_address",
            "age",
        ]
        xmlrpc = crm_serverII(self.env)
        rec = xmlrpc.common.env['res.partner'].partnersyncCrm2DafaSSN(self.partner_social_sec_nr)
        if res:
            self.partner_id.write({f:rec['partner'][f] for f in FIELDS})
            # education_ids
            self.partner_id.education_ids = [(6,0,[])]
            for code,level,foreign,approved in rec['education_ids']:
                self.partner_id.education_ids = [(0,0,{
                    'sun_id': self.env['res.sun'].search([('code','=',code)],limit=1)[0].id,
                    'education_level_id': self.env['res.partner.education.education_level'].search([('name','=',level)],limit=1)[0].id,
                    'foreign_education': foreign,
                    'foreign_education_approved': approved
                    })]

            # drivers_license_ids
            self.partner_id.drivers_license_ids = [(6,0,[e.id for e in self.env['res.drivers_license'].search([('name','in',rec['drivers_license_ids'])])])]
            # job_ids
            self.partner_id.job_ids = [(6,0,[])]
            for ssyk_code,exp_length,exp,edu,sun_code,edu_lvl,edu_f,edu_fa in rec['job_ids']:
                _logger.warn('ssyk code %s %s,exp lenght %s,exp %s,edu %s' % (
                        ssyk_code,self.env['res.ssyk'].search([('code','=',ssyk_code)],limit=1)[0],
                        exp_length, exp, edu))
                values = {
                        'partner_id': self.id,
                        'ssyk_id' : self.env['res.ssyk'].search([('code','=',code)],limit=1)[0],
                        'experience_length': exp_length,
                        'education': edu,
                        'experience': exp
                    }
                sun_id = self.env['res.sun'].search([('code', '=', sun_code)], limit=1)[0]
                edu_level = self.env['res.partner.education.eduation_level'].search([('name', '=',edu_lvl)], limit=1)[0]
                education_id = self.env['res.partner.education'].search([('partner_id','=',self.partner_id.id),
                                                                        ('sun_id','=',sun_id.id),
                                                                        ('education_level_id','=',edu_level.id),
                                                                        ('foreign_education','=',edu_f),
                                                                        ('foreign_education_approved','=',edu_fa)], limit=1)[0]
                _logger.warn('sun code %s %s, edu level %s %s, edu_f %s, edu_fa %s, education %s' % (
                        sun_code,sun_id, edu_lvl, edu_level, edu_f, edu_fa, education_id))
                values['education_id'] = education_id.id
                self.partner_id.job_ids = [(0,0, values)]
            else:
                raise Warning("Partner not found in CRM")
            
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


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.one
    def get_jobseeker_data(self):

        xmlrpc = crm_server(self.env)
