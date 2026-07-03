from odoo import _, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _edafaa_prepare_student_vals(self):
        """Use partner.id_number only — never vat/ref as national ID."""
        prepare = getattr(super(), '_edafaa_prepare_student_vals', None)
        if not prepare:
            return False
        self.ensure_one()
        partner = self
        id_number = (partner.id_number or '').strip()
        if not id_number:
            return False
        vals = prepare()
        if vals:
            vals['id_number'] = id_number
        return vals
