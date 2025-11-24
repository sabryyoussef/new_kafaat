# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class BatchIntakeApplicant(models.Model):
    """
    Individual applicant record from batch intake.
    Stores applicant data and eligibility assessment.
    """
    _name = 'batch.intake.applicant'
    _description = 'Batch Intake Applicant'
    _order = 'create_date desc'
    
    batch_id = fields.Many2one(
        'batch.intake',
        string='Batch',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    # Applicant Information
    name = fields.Char(
        string='Full Name',
        required=True
    )
    
    email = fields.Char(
        string='Email'
    )
    
    phone = fields.Char(
        string='Phone'
    )
    
    age = fields.Integer(
        string='Age'
    )
    
    nationality = fields.Char(
        string='Nationality'
    )
    
    education_level = fields.Char(
        string='Education Level'
    )
    
    gpa = fields.Float(
        string='GPA / Grade'
    )
    
    english_level = fields.Char(
        string='English Level'
    )
    
    # Eligibility Assessment
    eligibility_status = fields.Selection([
        ('pending', 'Pending Review'),
        ('eligible', 'Eligible'),
        ('not_eligible', 'Not Eligible'),
        ('error', 'Data Error')
    ], string='Eligibility Status', default='pending', required=True)
    
    validation_notes = fields.Text(
        string='Validation Notes',
        help='Detailed notes about eligibility validation'
    )
    
    eligibility_score = fields.Float(
        string='Eligibility Score',
        help='Calculated eligibility score based on criteria'
    )
    
    # Criteria Results
    age_check = fields.Boolean(
        string='Age Requirement Met',
        default=False
    )
    
    education_check = fields.Boolean(
        string='Education Requirement Met',
        default=False
    )
    
    gpa_check = fields.Boolean(
        string='GPA Requirement Met',
        default=False
    )
    
    english_check = fields.Boolean(
        string='English Requirement Met',
        default=False
    )
    
    def check_eligibility(self, criteria=None):
        """
        Check eligibility based on criteria.
        If no criteria provided, use default rules.
        """
        self.ensure_one()
        
        if not criteria:
            criteria = self.env['batch.intake.eligibility.criteria'].search([], limit=1)
        
        validation_notes = []
        checks_passed = 0
        total_checks = 0
        
        # Age Check
        if criteria and criteria.min_age:
            total_checks += 1
            if self.age and self.age >= criteria.min_age:
                self.age_check = True
                checks_passed += 1
                validation_notes.append(f'✓ Age ({self.age}) meets minimum requirement ({criteria.min_age})')
            else:
                self.age_check = False
                validation_notes.append(f'✗ Age ({self.age or "N/A"}) below minimum ({criteria.min_age})')
        
        if criteria and criteria.max_age:
            if self.age and self.age <= criteria.max_age:
                validation_notes.append(f'✓ Age ({self.age}) within maximum limit ({criteria.max_age})')
            else:
                self.age_check = False
                validation_notes.append(f'✗ Age ({self.age or "N/A"}) exceeds maximum ({criteria.max_age})')
        
        # Education Check
        if criteria and criteria.required_education_level:
            total_checks += 1
            if self.education_level and criteria.required_education_level.lower() in self.education_level.lower():
                self.education_check = True
                checks_passed += 1
                validation_notes.append(f'✓ Education level ({self.education_level}) meets requirement')
            else:
                self.education_check = False
                validation_notes.append(f'✗ Education level ({self.education_level or "N/A"}) does not meet requirement ({criteria.required_education_level})')
        
        # GPA Check
        if criteria and criteria.min_gpa:
            total_checks += 1
            if self.gpa and self.gpa >= criteria.min_gpa:
                self.gpa_check = True
                checks_passed += 1
                validation_notes.append(f'✓ GPA ({self.gpa}) meets minimum ({criteria.min_gpa})')
            else:
                self.gpa_check = False
                validation_notes.append(f'✗ GPA ({self.gpa or "N/A"}) below minimum ({criteria.min_gpa})')
        
        # English Level Check
        if criteria and criteria.required_english_level:
            total_checks += 1
            if self.english_level and criteria.required_english_level.lower() in self.english_level.lower():
                self.english_check = True
                checks_passed += 1
                validation_notes.append(f'✓ English level ({self.english_level}) meets requirement')
            else:
                self.english_check = False
                validation_notes.append(f'✗ English level ({self.english_level or "N/A"}) does not meet requirement ({criteria.required_english_level})')
        
        # Calculate score and determine eligibility
        if total_checks > 0:
            self.eligibility_score = (checks_passed / total_checks) * 100
            
            # Determine eligibility based on score
            required_pass_rate = criteria.required_pass_rate if criteria else 80.0
            if self.eligibility_score >= required_pass_rate:
                self.eligibility_status = 'eligible'
                validation_notes.insert(0, f'✓✓✓ ELIGIBLE - Score: {self.eligibility_score:.1f}% (Required: {required_pass_rate}%)')
            else:
                self.eligibility_status = 'not_eligible'
                validation_notes.insert(0, f'✗✗✗ NOT ELIGIBLE - Score: {self.eligibility_score:.1f}% (Required: {required_pass_rate}%)')
        else:
            self.eligibility_status = 'pending'
            validation_notes.insert(0, 'No eligibility criteria configured')
        
        self.validation_notes = '\n'.join(validation_notes)
        
        _logger.info(f'Eligibility check for {self.name}: {self.eligibility_status} ({self.eligibility_score:.1f}%)')
    
    def action_mark_eligible(self):
        """Manually mark as eligible"""
        for record in self:
            record.write({
                'eligibility_status': 'eligible',
                'validation_notes': (record.validation_notes or '') + '\n\n[Manual Override] Marked as eligible by ' + self.env.user.name
            })
    
    def action_mark_not_eligible(self):
        """Manually mark as not eligible"""
        for record in self:
            record.write({
                'eligibility_status': 'not_eligible',
                'validation_notes': (record.validation_notes or '') + '\n\n[Manual Override] Marked as not eligible by ' + self.env.user.name
            })
    
    def action_recheck_eligibility(self):
        """Re-run eligibility check"""
        for record in self:
            record.check_eligibility()

