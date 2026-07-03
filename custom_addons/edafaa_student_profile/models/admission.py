from odoo import fields, models


class OpAdmission(models.Model):
    _inherit = 'op.admission'

    id_number = fields.Char(string='ID Number', size=64)
    nationality = fields.Many2one('res.country', string='Nationality')
    specialization_id = fields.Many2one('op.program', string='Specialization')

    def get_student_vals(self):
        self.ensure_one()
        details = super().get_student_vals()
        phone = self.phone or self.mobile or ''
        details.update({
            'name_arabic': self.name,
            'name_english': self.name,
            'id_number': self.id_number or False,
            'phone': phone,
            'street': self.street or False,
            'street2': self.street2 or False,
            'city': self.city or False,
            'zip': self.zip or False,
            'state_id': self.state_id.id if self.state_id else False,
            'country_id': self.country_id.id if self.country_id else False,
            'nationality': self.nationality.id if self.nationality else False,
            'specialization_id': self.specialization_id.id if self.specialization_id else False,
        })
        return details
