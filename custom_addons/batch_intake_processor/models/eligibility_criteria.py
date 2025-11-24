# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BatchIntakeEligibilityCriteria(models.Model):
    """
    Configurable eligibility criteria for batch intake processing.
    """
    _name = 'batch.intake.eligibility.criteria'
    _description = 'Eligibility Criteria'
    _rec_name = 'name'
    
    name = fields.Char(
        string='Criteria Name',
        required=True,
        default='Default Eligibility Criteria'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    description = fields.Text(
        string='Description',
        help='Describe the eligibility requirements'
    )
    
    # Age Criteria
    min_age = fields.Integer(
        string='Minimum Age',
        default=18,
        help='Minimum age requirement for applicants'
    )
    
    max_age = fields.Integer(
        string='Maximum Age',
        default=0,
        help='Maximum age limit (0 = no limit)'
    )
    
    # Education Criteria
    required_education_level = fields.Char(
        string='Required Education Level',
        help='Required education level (e.g., High School, Bachelor, etc.)'
    )
    
    # GPA Criteria
    min_gpa = fields.Float(
        string='Minimum GPA',
        digits=(3, 2),
        help='Minimum GPA or grade requirement'
    )
    
    # English Level Criteria
    required_english_level = fields.Char(
        string='Required English Level',
        help='Required English proficiency level (e.g., Intermediate, Advanced)'
    )
    
    # Overall Requirements
    required_pass_rate = fields.Float(
        string='Required Pass Rate (%)',
        default=80.0,
        help='Minimum percentage of criteria that must be met'
    )
    
    # Statistics
    batch_count = fields.Integer(
        string='Batches Using This Criteria',
        compute='_compute_batch_count'
    )
    
    @api.depends()
    def _compute_batch_count(self):
        """Count batches using this criteria"""
        for record in self:
            # This is a simplified count - in reality you'd track which batch used which criteria
            record.batch_count = 0
    
    @api.constrains('min_age', 'max_age')
    def _check_age_range(self):
        """Validate age range"""
        for record in self:
            if record.min_age < 0:
                raise ValidationError(_('Minimum age cannot be negative.'))
            if record.max_age > 0 and record.max_age < record.min_age:
                raise ValidationError(_('Maximum age must be greater than minimum age.'))
    
    @api.constrains('min_gpa')
    def _check_gpa(self):
        """Validate GPA"""
        for record in self:
            if record.min_gpa < 0 or record.min_gpa > 100:
                raise ValidationError(_('GPA must be between 0 and 100.'))
    
    @api.constrains('required_pass_rate')
    def _check_pass_rate(self):
        """Validate pass rate"""
        for record in self:
            if record.required_pass_rate < 0 or record.required_pass_rate > 100:
                raise ValidationError(_('Pass rate must be between 0 and 100.'))

