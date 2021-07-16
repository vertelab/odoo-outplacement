from lxml import etree

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        """
        :param view_id: Active view ID
        :param view_type: Active view type
        :param toolbar:
        :param submenu:
        :return: This function will disable CUD operations for active
        user if user has dafa accounting read access and will disable
        all the button from form view except preview button.
        """

        res = super(AccountInvoice, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if self.env.user.has_group('base_user_groups_dafa.group_dafa_admin_accounting_read'):
            if view_type == 'form':
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//header"):
                    for item in node.getiterator('button'):
                        if item.attrib.get('string') != "Preview":
                            node.remove(item)
                for node in doc.xpath("//form"):
                    node.set('create', 'false')
                    node.set('forcecreate', 'false')
                    node.set('edit', 'false')
                    node.set('forceedit', 'false')
                    node.set('delete', 'false')
                res['arch'] = etree.tostring(doc, encoding='unicode')
                return res
            if view_type == 'tree':
                tree_doc = etree.XML(res['arch'])
                for node in tree_doc.xpath("//tree"):
                    node.set('create', 'false')
                    node.set('edit', 'false')
                    node.set('delete', 'false')
                res['arch'] = etree.tostring(tree_doc, encoding='unicode')
                return res

        return res
