# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models
from jinja2 import Template


class MedicalLeaveExtension(models.Model):
    """Modèle pour les prolongations d'arrêt de travail"""
    _name = 'medical.leave.extension'
    _description = "Prolongation d'arrêt de travail"
    _rec_name = 'patient_id'

    date = fields.Date(
        string='Date',
        default=fields.Date.today(),
        required=True)
    patient_id = fields.Many2one('res.partner', string="Patient", required=False)
    firstname = fields.Char(string="Prénom")
    lastname = fields.Char(string="Nom")
    extension_duration = fields.Integer(string="Durée de prolongation (jours)", required=True)
    extension_start_date = fields.Date(string="Date de début de prolongation", required=True)
    extension_end_date = fields.Date(string="Date de fin de prolongation", compute='_compute_extension_end_date',
                                     store=True)
    content = fields.Html(string="Contenu du rapport")

    @api.onchange('patient_id', 'firstname', 'lastname', 'extension_duration', 'extension_start_date',
                 'extension_end_date', 'date')
    def _compute_content(self):
        for record in self:
            template = self.env['medical.report.template'].search([('report_type', '=', 'extension')], limit=1)
            if template:
                context = record._get_template_context()
                record.content = template.render_template(context)
            else:
                record.content = self.env['medical.report.template'].get_default_content('extension')

    def _get_template_context(self):
        """Prépare le contexte pour le template"""
        patient_name = self.patient_id.name if self.patient_id else f"{self.firstname} {self.lastname}"
        return {
            'user': {'name': 'BOUNEDJAR Reda'},
            'patient': {'name': patient_name},
            'extension_duration': self.extension_duration,
            'extension_start_date': self.extension_start_date.strftime('%d/%m/%Y') if self.extension_start_date else '',
            'extension_end_date': self.extension_end_date.strftime('%d/%m/%Y') if self.extension_end_date else '',
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

    @api.depends('extension_start_date', 'extension_duration')
    def _compute_extension_end_date(self):
        for record in self:
            if record.extension_start_date and record.extension_duration:
                record.extension_end_date = record.extension_start_date + timedelta(days=record.extension_duration - 1)
            else:
                record.extension_end_date = False

    def action_print_extension_certificate(self):
        return self.env.ref('base_hospital_management.action_medical_leave_extension_report').report_action(self)
