# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CourseCategory(models.Model):
    _name = 'gr.course.category'
    _description = 'Course Category'
    _order = 'sequence, name'
    _parent_name = 'parent_id'
    _parent_store = True

    name = fields.Char(string='Category Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    parent_id = fields.Many2one('gr.course.category', string='Parent Category', ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('gr.course.category', 'parent_id', string='Subcategories')
    course_count = fields.Integer(string='Number of Courses', compute='_compute_course_count', store=True)
    icon = fields.Char(string='Icon Class', help='Font Awesome icon class (e.g., fa-laptop, fa-book)')
    color = fields.Integer(string='Color Index', default=0)
    description = fields.Html(string='Description', translate=True)
    active = fields.Boolean(string='Active', default=True)

    @api.depends('parent_id')
    def _compute_course_count(self):
        """Compute the number of courses in this category and subcategories"""
        for category in self:
            # Get all courses in this category and its children
            domain = [('category_id', 'child_of', category.id)]
            category.course_count = self.env['gr.training.program'].search_count(domain)

    def name_get(self):
        """Display full category path in selection fields"""
        result = []
        for record in self:
            if record.parent_id:
                name = f"{record.parent_id.name} / {record.name}"
            else:
                name = record.name
            result.append((record.id, name))
        return result
