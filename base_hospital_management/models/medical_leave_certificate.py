# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models
from jinja2 import Template


class MedicalLeaveCertificate(models.Model):
    """Modèle pour les arrêts de travail initiaux"""
    _name = 'medical.leave.certificate'
    _description = "Certificat d'arrêt de travail"
    _rec_name = 'patient_id'

    date = fields.Date(
        string='Date',
        default=fields.Date.today(),
        required=True)
    patient_id = fields.Many2one('res.partner', string="Patient", required=False,
        context = {
            'form_view_ref': 'base_hospital_management.res_partner_view_form'
        }
    )
    firstname = fields.Char(string="Prénom")
    lastname = fields.Char(string="Nom")
    leave_duration = fields.Integer(string="Durée (jours)", required=True)
    leave_start_date = fields.Date(string="Date de début", required=True)
    leave_end_date = fields.Date(string="Date de fin", compute='_compute_leave_end_date', store=True)
    content = fields.Html(string="Contenu du rapport")
    outpatient_id = fields.Many2one('hospital.outpatient', string='Consultation', ondelete='cascade')

    @api.onchange('patient_id', 'firstname', 'lastname', 'leave_duration', 'leave_start_date', 'leave_end_date', 'date')
    def _compute_content(self):
        for record in self:
            try:
                template = self.env['medical.report.template'].search([('report_type', '=', 'leave')], limit=1)
                if template:
                    context = record._get_template_context()
                    record.content = template.render_template(context)
                else:
                    # Si pas de template, créer le contenu par défaut
                    context = record._get_template_context()
                    template_obj = self.env['medical.report.template']
                    default_content = template_obj.get_default_content('leave')
                    template_temp = Template(default_content)
                    record.content = template_temp.render(context)
            except Exception as e:
                # En cas d'erreur, utiliser un contenu simple
                patient_name = record.patient_id.name if record.patient_id else f"{record.firstname} {record.lastname}"
                record.content = f"<p>Je soussigné, <strong>Dr BOUNEDJAR Reda</strong>, certifie avoir vu et examiné ce jour le patient <strong>{patient_name}</strong></p>"

    def _get_template_context(self):
        """Prépare le contexte pour le template"""
        patient_name = self.patient_id.name if self.patient_id else f"{self.firstname} {self.lastname}"
        return {
            'user': {'name': 'BOUNEDJAR Reda'},
            'patient': {'name': patient_name},
            'leave_duration': self.leave_duration,
            'leave_start_date': self.leave_start_date.strftime('%d/%m/%Y') if self.leave_start_date else '',
            'leave_end_date': self.leave_end_date.strftime('%d/%m/%Y') if self.leave_end_date else '',
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

    @api.depends('leave_start_date', 'leave_duration')
    def _compute_leave_end_date(self):
        for record in self:
            if record.leave_start_date and record.leave_duration:
                record.leave_end_date = record.leave_start_date + timedelta(days=record.leave_duration - 1)
            else:
                record.leave_end_date = False

    def action_print_leave_certificate(self):
        return self.env.ref('base_hospital_management.action_medical_leave_certificate').report_action(self)

