from odoo import api, fields, models


class OpProgram(models.Model):
    _inherit = 'op.program'

    skill_ids = fields.Many2many(
        'edafaa.skill',
        'edafaa_program_skill_rel',
        'program_id',
        'skill_id',
        string='Skills',
    )

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env['ir.sequence']
        for vals in vals_list:
            code = vals.get('code')
            if not code or not str(code).strip():
                vals['code'] = sequence.next_by_code('edafaa.op.program')
        return super().create(vals_list)
