# -*- coding: utf-8 -*-
from odoo import api, fields, models
from jinja2 import Template


class MedicalCertificate(models.Model):
    """Modèle pour les Certificat médical"""
    _name = 'medical.certificate'
    _description = "Certificat médical"
    _rec_name = 'patient_id'

    date = fields.Date(
        string='Date',
        default=fields.Date.today(),
        required=True)
    patient_id = fields.Many2one('res.partner', string="Patient", required=False)
    firstname = fields.Char(string="Prénom")
    lastname = fields.Char(string="Nom")
    consultation_reason = fields.Text(string="Motif de consultation", required=True)
    examination_result = fields.Text(string="Résultat de l'examen radio-clinique", required=True)
    content = fields.Html(string="Contenu du rapport")

    @api.onchange('patient_id', 'firstname', 'lastname', 'consultation_reason', 'examination_result', 'date')
    def _compute_content(self):
        for record in self:
            try:
                template = self.env['medical.report.template'].search([('report_type', '=', 'certificate')], limit=1)
                if template:
                    context = record._get_template_context()
                    record.content = template.render_template(context)
                else:
                    context = record._get_template_context()
                    template_obj = self.env['medical.report.template']
                    default_content = template_obj.get_default_content('certificate')
                    template_temp = Template(default_content)
                    record.content = template_temp.render(context)
            except Exception as e:
                patient_name = record.patient_id.name if record.patient_id else f"{record.firstname} {record.lastname}"
                record.content = f"<p>Je soussigné, <strong>Dr BOUNEDJAR Reda</strong>, certifie avoir vu et examiné ce jour le patient <strong>{patient_name}</strong></p>"

    def _get_template_context(self):
        """Prépare le contexte pour le template"""
        patient_name = self.patient_id.name if self.patient_id else f"{self.firstname} {self.lastname}"
        return {
            'user': {'name': 'BOUNEDJAR Reda'},
            'patient': {'name': patient_name},
            'consultation_reason': self.consultation_reason or '',
            'examination_result': self.examination_result or '',
            'date': self.date.strftime('%d/%m/%Y') if self.date else '',
        }

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            self.firstname = self.patient_id.firstname if hasattr(self.patient_id, 'firstname') else ''
            self.lastname = self.patient_id.lastname if hasattr(self.patient_id, 'lastname') else ''
        else:
            self.firstname = ''
            self.lastname = ''

    def action_print_medical_certificate(self):
        return self.env.ref('base_hospital_management.action_medical_certificate_report').report_action(self)