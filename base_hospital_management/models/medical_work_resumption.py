from odoo import api, fields, models


class MedicalWorkResumption(models.Model):
    """Modèle pour les certificats de reprise de travail"""
    _name = 'medical.work.resumption'
    _description = "Certificat de reprise de travail"
    _rec_name = 'patient_id'

    date = fields.Date(
        string='Date',
        default=fields.Date.today(),
        required=True)
    patient_id = fields.Many2one('res.partner', string="Patient", required=False)
    firstname = fields.Char(string="Prénom")
    lastname = fields.Char(string="Nom")
    resume_work_date = fields.Date(string="Date de reprise", required=True)
    work_type = fields.Selection([
        ('full_time', 'Temps complet'),
        ('part_time', 'Temps partiel'),
    ], string="Type de reprise", default='full_time', required=True)
    content = fields.Html(string="Contenu du rapport")
    outpatient_id = fields.Many2one('hospital.outpatient', string='Consultation', ondelete='cascade')

    @api.onchange('patient_id', 'firstname', 'lastname', 'resume_work_date', 'work_type', 'date')
    def _compute_content(self):
        for record in self:
            template = self.env['medical.report.template'].search([('report_type', '=', 'resumption')], limit=1)
            if template:
                context = record._get_template_context()
                record.content = template.render_template(context)
            else:
                record.content = self.env['medical.report.template'].get_default_content('resumption')

    def _get_template_context(self):
        """Prépare le contexte pour le template"""
        patient_name = self.patient_id.name if self.patient_id else f"{self.firstname} {self.lastname}"
        work_type_display = 'temps complet' if self.work_type == 'full_time' else 'temps partiel'
        return {
            'user': {'name': 'BOUNEDJAR Reda'},
            'patient': {'name': patient_name},
            'resume_work_date': self.resume_work_date.strftime('%d/%m/%Y') if self.resume_work_date else '',
            'work_type': work_type_display,
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

    def action_print_resumption_certificate(self):
        return self.env.ref('base_hospital_management.action_medical_work_resumption_report').report_action(self)