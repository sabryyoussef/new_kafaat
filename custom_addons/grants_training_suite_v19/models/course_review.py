# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CourseReview(models.Model):
    _name = 'gr.course.review'
    _description = 'Course Review'
    _order = 'create_date desc'

    course_id = fields.Many2one('gr.training.program', string='Course', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Student', required=True, ondelete='cascade')
    rating = fields.Integer(string='Rating', required=True, default=5)
    comment = fields.Text(string='Review Comment', required=True)
    helpful_count = fields.Integer(string='Helpful Votes', default=0)
    is_verified_purchase = fields.Boolean(string='Verified Purchase', default=False)
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('rating_range', 'CHECK(rating >= 1 AND rating <= 5)', 'Rating must be between 1 and 5'),
        ('unique_review', 'UNIQUE(course_id, partner_id)', 'You have already reviewed this course')
    ]
