# -*- coding: utf-8 -*-

import logging
import traceback
import json
from odoo import api, models, fields, tools, _

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

    LANGUAGE_CODES = (
        ("ab", "Abkhazian"),
        ("aa", "Afar"),
        ("af", "Afrikaans"),
        ("ak", "Akan"),
        ("sq", "Albanian"),
        ("am", "Amharic"),
        ("ar", "Arabic"),
        ("an", "Aragonese"),
        ("hy", "Armenian"),
        ("as", "Assamese"),
        ("av", "Avaric"),
        ("ae", "Avestan"),
        ("ay", "Aymara"),
        ("az", "Azerbaijani"),
        ("bm", "Bambara"),
        ("ba", "Bashkir"),
        ("eu", "Basque"),
        ("be", "Belarusian"),
        ("bn", "Bengali"),
        ("bh", "Bihari languages"),
        ("bi", "Bislama"),
        ("bs", "Bosnian"),
        ("br", "Breton"),
        ("bg", "Bulgarian"),
        ("my", "Burmese"),
        ("ca", "Catalan, Valencian"),
        ("ch", "Chamorro"),
        ("ce", "Chechen"),
        ("ny", "Chichewa, Chewa, Nyanja"),
        ("zh", "Chinese"),
        ("cv", "Chuvash"),
        ("kw", "Cornish"),
        ("co", "Corsican"),
        ("cr", "Cree"),
        ("hr", "Croatian"),
        ("cs", "Czech"),
        ("da", "Danish"),
        ("dv", "Divehi, Dhivehi, Maldivian"),
        ("nl", "Dutch, Flemish"),
        ("dz", "Dzongkha"),
        ("en", "English"),
        ("eo", "Esperanto"),
        ("et", "Estonian"),
        ("ee", "Ewe"),
        ("fo", "Faroese"),
        ("fj", "Fijian"),
        ("fi", "Finnish"),
        ("fr", "French"),
        ("ff", "Fulah"),
        ("gl", "Galician"),
        ("ka", "Georgian"),
        ("de", "German"),
        ("el", "Greek, Modern (1453–)"),
        ("gn", "Guarani"),
        ("gu", "Gujarati"),
        ("ht", "Haitian, Haitian Creole"),
        ("ha", "Hausa"),
        ("he", "Hebrew"),
        ("hz", "Herero"),
        ("hi", "Hindi"),
        ("ho", "Hiri Motu"),
        ("hu", "Hungarian"),
        ("ia", "Interlingua (International Auxiliary Language Association)"),
        ("id", "Indonesian"),
        ("ie", "Interlingue, Occidental"),
        ("ga", "Irish"),
        ("ig", "Igbo"),
        ("ik", "Inupiaq"),
        ("io", "Ido"),
        ("is", "Icelandic"),
        ("it", "Italian"),
        ("iu", "Inuktitut"),
        ("ja", "Japanese"),
        ("jv", "Javanese"),
        ("kl", "Kalaallisut, Greenlandic"),
        ("kn", "Kannada"),
        ("kr", "Kanuri"),
        ("ks", "Kashmiri"),
        ("kk", "Kazakh"),
        ("km", "Central Khmer"),
        ("ki", "Kikuyu, Gikuyu"),
        ("rw", "Kinyarwanda"),
        ("ky", "Kirghiz, Kyrgyz"),
        ("kv", "Komi"),
        ("kg", "Kongo"),
        ("ko", "Korean"),
        ("ku", "Kurdish"),
        ("kj", "Kuanyama, Kwanyama"),
        ("la", "Latin"),
        ("lb", "Luxembourgish, Letzeburgesch"),
        ("lg", "Ganda"),
        ("li", "Limburgan, Limburger, Limburgish"),
        ("ln", "Lingala"),
        ("lo", "Lao"),
        ("lt", "Lithuanian"),
        ("lu", "Luba-Katanga"),
        ("lv", "Latvian"),
        ("gv", "Manx"),
        ("mk", "Macedonian"),
        ("mg", "Malagasy"),
        ("ms", "Malay"),
        ("ml", "Malayalam"),
        ("mt", "Maltese"),
        ("mi", "Maori"),
        ("mr", "Marathi"),
        ("mh", "Marshallese"),
        ("mn", "Mongolian"),
        ("na", "Nauru"),
        ("nv", "Navajo, Navaho"),
        ("nd", "North Ndebele"),
        ("ne", "Nepali"),
        ("ng", "Ndonga"),
        ("nb", "Norwegian Bokmål"),
        ("nn", "Norwegian Nynorsk"),
        ("no", "Norwegian"),
        ("ii", "Sichuan Yi, Nuosu"),
        ("nr", "South Ndebele"),
        ("oc", "Occitan"),
        ("oj", "Ojibwa"),
        ("cu", "Church Slavic, Old Slavonic, Church Slavonic, Old Bulgarian, Old Church Slavonic"),
        ("om", "Oromo"),
        ("or", "Oriya"),
        ("os", "Ossetian, Ossetic"),
        ("pa", "Punjabi, Panjabi"),
        ("pi", "Pali"),
        ("fa", "Persian"),
        ("pl", "Polish"),
        ("ps", "Pashto, Pushto"),
        ("pt", "Portuguese"),
        ("qu", "Quechua"),
        ("rm", "Romansh"),
        ("rn", "Rundi"),
        ("ro", "Romanian, Moldavian, Moldovan"),
        ("ru", "Russian"),
        ("sa", "Sanskrit"),
        ("sc", "Sardinian"),
        ("sd", "Sindhi"),
        ("se", "Northern Sami"),
        ("sm", "Samoan"),
        ("sg", "Sango"),
        ("sr", "Serbian"),
        ("gd", "Gaelic, Scottish Gaelic"),
        ("sn", "Shona"),
        ("si", "Sinhala, Sinhalese"),
        ("sk", "Slovak"),
        ("sl", "Slovenian"),
        ("so", "Somali"),
        ("st", "Southern Sotho"),
        ("es", "Spanish, Castilian"),
        ("su", "Sundanese"),
        ("sw", "Swahili"),
        ("ss", "Swati"),
        ("sv", "Swedish"),
        ("ta", "Tamil"),
        ("te", "Telugu"),
        ("tg", "Tajik"),
        ("th", "Thai"),
        ("ti", "Tigrinya"),
        ("bo", "Tibetan"),
        ("tk", "Turkmen"),
        ("tl", "Tagalog"),
        ("tn", "Tswana"),
        ("to", "Tonga (Tonga Islands)"),
        ("tr", "Turkish"),
        ("ts", "Tsonga"),
        ("tt", "Tatar"),
        ("tw", "Twi"),
        ("ty", "Tahitian"),
        ("ug", "Uighur, Uyghur"),
        ("uk", "Ukrainian"),
        ("ur", "Urdu"),
        ("uz", "Uzbek"),
        ("ve", "Venda"),
        ("vi", "Vietnamese"),
        ("vo", "Volapük"),
        ("wa", "Walloon"),
        ("cy", "Welsh"),
        ("wo", "Wolof"),
        ("fy", "Western Frisian"),
        ("xh", "Xhosa"),
        ("yi", "Yiddish"),
        ("yo", "Yoruba"),
        ("za", "Zhuang, Chuang"),
        ("zu", "Zulu"),
        )

    interpreter_language = fields.Selection(
        selection=LANGUAGE_CODES,
        string="Interpreter Language")
    interpreter_gender_preference = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('no_preference', 'no preference'),
    ], string="Gender Preference")
    location_type = fields.Selection([
        ('on_premise', 'On premise'),
        ('telephone', 'Telephone'),
    ], string='Location')
    time_start = fields.Datetime('Start Time')
    time_end = fields.Datetime('End Time')
    phone = fields.Char()
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    interpeter_booking_ref = fields.Char('Booking Reference')
    Interpreteter_booking_status = fields.Char('Booking Status')
    department_id = fields.Many2one('hr.department', 'Department')

    @api.multi
    def action_create_calendar_event(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        action['context'] = {
            'default_activity_type_id': self.activity_type_id.id,
            'default_res_id': self.env.context.get('default_res_id'),
            'default_res_model': self.env.context.get('default_res_model'),
            'default_name': self.summary or self.res_name,
            'default_description': self.note and tools.html2plaintext(
                self.note).strip() or '',
            'default_activity_ids': [(6, 0, self.ids)],
            'initial_date': self.date_deadline,
        }
        return action

    @api.model
    def create(self, vals):
        record = super(MailActivity, self).create(vals)
        order_interpreter = self.env.ref(
            'outplacement_order_interpretor.order_interpreter').id
        if record.activity_type_id.id == order_interpreter:
            try:
                resp = self.env[
                    'ipf.interpreter.client'].post_tolkbokningar(record)
            except Exception as e:
                _logger.error(e)
                _logger.error(traceback.format_exc())
                resp = None
            if resp:
                try:
                    record.processing_response(resp)
                except Exception as e:
                    _logger.error(e)
                    _logger.error(traceback.format_exc())
        return record

    @api.model
    def processing_response(self, response):
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            self.booking_ref = data.get('tolkbokningId')
            
    @api.model
    def cron_order_interpretator(self):
        pass
