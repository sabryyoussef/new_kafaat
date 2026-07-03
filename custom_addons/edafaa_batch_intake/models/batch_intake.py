from odoo import _, api, models
from odoo.exceptions import UserError


class BatchIntake(models.Model):
    _inherit = 'batch.intake'

    def action_process_file(self):
        for batch in self:
            if batch.course_id and not batch.batch_id:
                raise UserError(_(
                    'Schedule Batch is required before processing this intake. '
                    'Please select a batch from OpenEduCat Enrollment.'
                ))
        batches = self
        res = super().action_process_file()
        for batch in batches:
            batch._edafaa_enrich_imported_students_from_file()
        return res

    @api.model
    def _edafaa_extract_profile_from_row(self, record):
        def pick(*keys):
            for key in keys:
                val = record.get(key)
                if val not in (None, ''):
                    return str(val).strip()
            return ''

        phone = pick('phone', 'Phone', 'PHONE', 'mobile', 'Mobile', 'MOBILE')
        street = pick('street', 'Street', 'address', 'Address', 'ADDRESS')
        city = pick('city', 'City', 'CITY')
        id_number = pick(
            'id_number', 'ID Number', 'id', 'ID', 'national_id', 'National ID',
        )
        country_name = pick('country', 'Country', 'COUNTRY')
        country_id = False
        if country_name:
            country = self.env['res.country'].search(
                [('name', 'ilike', country_name)], limit=1,
            )
            country_id = country.id if country else False

        program_name = pick(
            'specialization', 'Specialization', 'program', 'Program', 'major', 'Major',
        )
        specialization_id = False
        if program_name:
            program = self.env['op.program'].search(
                [('name', 'ilike', program_name)], limit=1,
            )
            specialization_id = program.id if program else False

        return {
            'phone': phone,
            'street': street,
            'city': city,
            'id_number': id_number,
            'country_id': country_id,
            'specialization_id': specialization_id,
        }

    def _edafaa_enrich_imported_students_from_file(self):
        self.ensure_one()
        if self.state != 'processed':
            return
        try:
            records = self._parse_file()
        except Exception:
            return
        Student = self.env['op.student']
        for record in records:
            email = record.get('email') or record.get('Email') or record.get('EMAIL') or ''
            name = record.get('name') or record.get('Name') or record.get('NAME') or ''
            profile = self._edafaa_extract_profile_from_row(record)
            if not any(profile.values()):
                continue
            domain = [('batch_intake_id', '=', self.id)]
            if email:
                domain.append(('email', '=', email))
            elif name:
                domain.append(('name', '=', name))
            else:
                continue
            student = Student.search(domain, limit=1)
            if not student:
                continue
            write_vals = {k: v for k, v in profile.items() if v}
            if write_vals:
                write_vals.setdefault('name_arabic', student.name_arabic or student.name)
                write_vals.setdefault('name_english', student.name_english or student.name)
                student.write(write_vals)


class OpStudent(models.Model):
    _inherit = 'op.student'

    def write(self, vals):
        res = super().write(vals)
        if 'batch_intake_id' in vals:
            intake_id = vals['batch_intake_id']
            for student in self:
                partner = student.partner_id
                if partner and partner.batch_intake_id.id != intake_id:
                    partner.write({'batch_intake_id': intake_id})
        return res
