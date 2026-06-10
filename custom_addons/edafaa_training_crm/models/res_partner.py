from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    birth_date = fields.Date(string='Birth Date')
    id_number = fields.Char(string='ID Number', size=64)

    op_student_id = fields.Many2one(
        'op.student',
        string='Student Record',
        compute='_compute_op_student_id',
        store=False,
    )

    @api.depends('is_student')
    def _compute_op_student_id(self):
        Student = self.env['op.student']
        for partner in self:
            partner.op_student_id = Student.search(
                [('partner_id', '=', partner.id)], limit=1,
            )

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        if not self.env.context.get('edafaa_skip_student_sync'):
            partners._edafaa_sync_student_from_partner()
        return partners

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get('edafaa_skip_student_sync'):
            return res
        if 'is_student' in vals or any(
            key in vals for key in (*self._edafaa_student_source_fields(), 'id_number')
        ):
            self._edafaa_sync_student_from_partner()
        return res

    @api.model
    def _edafaa_student_source_fields(self):
        return {
            'name', 'email', 'phone', 'street', 'city', 'country_id',
            'birth_date', 'id_number', 'vat', 'ref',
        }

    def _edafaa_sync_student_from_partner(self):
        """Create op.student when partner is flagged as student and profile is sufficient."""
        if self.env.context.get('edafaa_skip_student_sync'):
            return
        for partner in self.filtered('is_student'):
            if partner.op_student_id:
                continue
            student_vals = partner._edafaa_prepare_student_vals()
            if not student_vals:
                continue
            self.env['op.student'].with_context(
                edafaa_skip_student_sync=True,
            ).create(student_vals)

    def _edafaa_prepare_student_vals(self):
        self.ensure_one()
        partner = self
        name = (partner.name or '').strip()
        email = (partner.email or '').strip()
        phone = (partner.phone or '').strip()
        street = (partner.street or '').strip()
        city = (partner.city or '').strip()
        id_number = (partner.id_number or partner.vat or partner.ref or '').strip()
        birth_date = partner.birth_date

        missing = []
        if not name:
            missing.append(_('Name'))
        if not email:
            missing.append(_('Email'))
        if not phone:
            missing.append(_('Phone'))
        if not street:
            missing.append(_('Street'))
        if not city:
            missing.append(_('City'))
        if not partner.country_id:
            missing.append(_('Country'))
        if not birth_date:
            missing.append(_('Birth Date'))
        if not id_number:
            missing.append(_('ID Number'))

        if missing:
            return False

        return {
            'partner_id': partner.id,
            'name_english': name,
            'name_arabic': name,
            'email': email,
            'phone': phone,
            'street': street,
            'city': city,
            'country_id': partner.country_id.id,
            'birth_date': birth_date,
            'id_number': id_number,
            'gender': 'm',
        }

    def action_open_student_record(self):
        self.ensure_one()
        student = self.op_student_id
        if not student:
            raise UserError(_(
                'No student record exists for this contact. '
                'Mark as student and ensure required profile data '
                '(email, phone, address, birth date, ID) is filled.'
            ))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Student'),
            'res_model': 'op.student',
            'view_mode': 'form',
            'res_id': student.id,
        }
