# -*- coding: utf-8 -*-
from odoo import api, fields, models
from jinja2 import Template


class MedicalReferralLetter(models.Model):
    """Modèle pour les lettres d'orientation"""
    _name = 'medical.referral.letter'
    _description = "Lettre d'orientation"
    _rec_name = 'patient_id'

    date = fields.Date(
        string='Date',
        default=fields.Date.today(),
        required=True)
    patient_id = fields.Many2one('res.partner', string="Patient", required=False)
    firstname = fields.Char(string="Prénom")
    lastname = fields.Char(string="Nom")
    age = fields.Integer(string="Âge")
    referral_reason = fields.Text(string="Motif d'orientation", required=True)
    consultation_reason = fields.Text(string="Motif de consultation")
    clinical_findings = fields.Text(string="Examen clinique")
    suspected_diagnosis = fields.Text(string="Diagnostic suspecté")
    colleague_name = fields.Char(string="Nom du confrère destinataire")
    content = fields.Html(string="Contenu du rapport")
    outpatient_id = fields.Many2one('hospital.outpatient', string='Consultation', ondelete='cascade')

    @api.onchange('patient_id', 'firstname', 'lastname', 'age', 'referral_reason', 'consultation_reason',
                 'clinical_findings', 'suspected_diagnosis', 'colleague_name', 'date')
    def _compute_content(self):
        for record in self:
            template = self.env['medical.report.template'].search([('report_type', '=', 'referral')], limit=1)
            if template:
                context = record._get_template_context()
                record.content = template.render_template(context)

    def _get_template_context(self):
        """Prépare le contexte pour le template"""
        patient_name = self.patient_id.name if self.patient_id else f"{self.firstname} {self.lastname}"
        age = self.patient_id.age if self.patient_id and hasattr(self.patient_id, 'age') else self.age
        return {
            'user': {'name': 'BOUNEDJAR Reda'},
            'patient': {'name': patient_name},
            'age': age,
            'colleague_name': self.colleague_name or '',
            'referral_reason': self.referral_reason or '',
            'consultation_reason': self.consultation_reason or '',
            'clinical_findings': self.clinical_findings or '',
            'suspected_diagnosis': self.suspected_diagnosis or '',
            'date': self.date.strftime('%d/%m/%Y') if self.date else '',
        }

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            self.firstname = self.patient_id.firstname if hasattr(self.patient_id, 'firstname') else ''
            self.lastname = self.patient_id.lastname if hasattr(self.patient_id, 'lastname') else ''
            self.age = self.patient_id.age if hasattr(self.patient_id, 'age') else 0
        else:
            self.firstname = ''
            self.lastname = ''
            self.age = 0

    def action_print_referral_letter(self):
        return self.env.ref('base_hospital_management.action_medical_referral_letter_report').report_action(self)