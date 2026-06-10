from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestOpProgramEnhancements(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.level = cls.env['op.program.level'].create({'name': 'UAT Level'})
        cls.program = cls.env['op.program'].create({
            'name': 'UAT Training Program',
            'code': 'PRG-UAT-TC',
            'program_level_id': cls.level.id,
            'duration_text': '40 hours',
            'training_language': 'bilingual',
            'max_trainees': 25,
            'program_objectives': '<p>Learn skills</p>',
            'career_outcomes': '<p>Better job</p>',
        })

    def test_default_state_draft(self):
        self.assertEqual(self.program.state, 'draft')

    def test_workflow_transitions(self):
        self.program.action_submit_for_review()
        self.assertEqual(self.program.state, 'review')
        self.program.action_approve()
        self.assertEqual(self.program.state, 'approved')
        self.assertTrue(self.program.approved_by_id)
        self.program.action_publish()
        self.assertEqual(self.program.state, 'published')
        self.program.action_archive_program()
        self.assertEqual(self.program.state, 'archived')
        self.assertFalse(self.program.active)
        self.program.action_reset_to_draft()
        self.assertEqual(self.program.state, 'draft')
        self.assertTrue(self.program.active)

    def test_linked_courses(self):
        course = self.env['op.course'].create({
            'name': 'UAT Linked Course',
            'code': 'CRS-UAT-LINK',
            'program_id': self.program.id,
        })
        self.program.invalidate_recordset(['course_count', 'course_ids'])
        self.assertEqual(self.program.course_count, 1)
        self.assertIn(course, self.program.course_ids)
