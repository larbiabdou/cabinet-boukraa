from odoo import models, fields, api
from datetime import date

class MedicalHealthCertificate(models.Model):
    _name = 'medical.health.certificate'
    _description = 'Certificat Médical de Bonne Santé et PNEUMO-PHTYSIO'
    _rec_name = 'patient_id'

    patient_id = fields.Many2one('res.partner', string="Patient")
    firstname = fields.Char(
        string='Prénom',
        required=False)

    lastname = fields.Char(
        string='Nom',
        required=False)
    patient_age = fields.Integer(string="Âge")
    patient_address = fields.Char(string="Adresse")
    date = fields.Date(string="Date", default=fields.Date.context_today)
    outpatient_id = fields.Many2one('hospital.outpatient', string='Consultation', ondelete='cascade')

    def action_print_health_certificate(self):
        return self.env.ref('base_hospital_management.action_medical_health_certificate_report').report_action(self)


    @api.onchange('patient_id')
    def _compute_patient_age(self):
        for record in self:
            if record.patient_id:
                record.patient_address = record.patient_id.street
                record.patient_age = record.patient_id.age
                record.firstname = record.patient_id.firstname
                record.lastname = record.patient_id.lastname
