from odoo import api, models


class OpProgram(models.Model):
    _inherit = 'op.program'

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env['ir.sequence']
        for vals in vals_list:
            code = vals.get('code')
            if not code or not str(code).strip():
                vals['code'] = sequence.next_by_code('edafaa.op.program')
        return super().create(vals_list)
