from odoo import models, fields, api

class PreviousYearMarks(models.Model):
    _name = 'previous.year.marks'
    _description = 'Previous Year Marks'

    student_id = fields.Many2one('res.student', string='Student')
    subject_id = fields.Many2one('subject.subject', string='Subject')
    total_marks = fields.Float(string='Total Marks', required=True)
    exam_marks = fields.Float(string='Obtained Marks in Exam', required=True)
    viva_marks = fields.Float(string='Obtained Marks in Viva', required=True)
    total_obtained_marks = fields.Float(string='Total Obtained Marks', compute='_compute_total_obtained_marks')

    @api.depends('exam_marks','viva_marks')
    def _compute_total_obtained_marks(self):
        for rec in self:
            rec.total_obtained_marks = rec.exam_marks + rec.viva_marks

