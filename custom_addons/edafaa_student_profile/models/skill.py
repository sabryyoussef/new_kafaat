from odoo import fields, models


class EdafaaSkill(models.Model):
    _name = 'edafaa.skill'
    _description = 'Training Skill'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    description = fields.Text()
    active = fields.Boolean(default=True)
