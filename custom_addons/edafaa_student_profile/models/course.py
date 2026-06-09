from odoo import api, fields, models


class OpCourse(models.Model):
    _inherit = 'op.course'

    skill_ids = fields.Many2many(
        'edafaa.skill',
        'edafaa_course_skill_rel',
        'course_id',
        'skill_id',
        string='Skills',
    )

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env['ir.sequence']
        for vals in vals_list:
            code = vals.get('code')
            if not code or not str(code).strip():
                vals['code'] = sequence.next_by_code('edafaa.op.course')
        return super().create(vals_list)
