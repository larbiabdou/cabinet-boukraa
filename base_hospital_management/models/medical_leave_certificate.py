from odoo import api, fields, models


class MedicalLeaveCertificate(models.Model):
    _name = 'medical.leave.certificate'
    _description = "Certificat d'arrêt de travail"
    _rec_name = 'patient_id'

    date = fields.Date(
        string='Date',
        default=fields.Date.today(),
        required=False)
    patient_id = fields.Many2one('res.partner', string="Patient", required=True)
    leave_start_date = fields.Date(string="Date de début", required=False)
    leave_end_date = fields.Date(string="Date de fin", required=False)
    leave_duration = fields.Integer(string="Durée (jours)")
    extended_duration = fields.Integer(string="Durée de prolongation (jours)", required=False)
    date_extention = fields.Date(string="Date de prolongation (jours)", required=False)
    resume_work_date = fields.Date(string="Date de reprise", required=False)
    type = fields.Selection(
        string='Type',
        selection=[('leave', 'Arrêt de travail'),
                   ('extended', 'Prolongation'), ],
        default='leave',
        required=True, )
