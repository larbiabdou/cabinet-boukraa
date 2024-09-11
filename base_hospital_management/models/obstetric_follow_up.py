from odoo import api, fields, models


class ObstetricFollowUp(models.Model):
    _name = 'obstetric.follow.up'
    _description = 'Obstetric Follow-up'

    patient_id = fields.Many2one(
        comodel_name='res.partner',
        string='Patient_id',
        required=False)

    date_1st_trimester = fields.Date(
        string='Date',
        required=False)

    gp_1 = fields.Char(
        string='GP',
        required=False)
    ddr = fields.Date(
        string='DDR',
        required=False)
    dpr = fields.Date(
        string='DPR',
        required=False)
    ac = fields.Boolean(
        string='AC',
        required=False)
    vv = fields.Boolean(
        string='VV',
        required=False)
    lcc = fields.Boolean(
        string='LCC',
        required=False)
    cn = fields.Boolean(
        string='CN',
        required=False)
    pole_cephalique = fields.Boolean(
        string='Pole céphalique',
        required=False)
    membre_4 = fields.Boolean(
        string='4 membres + 3 segments',
        required=False)
    trophoblaste = fields.Boolean(
        string='Trophoblaste',
        required=False)
    maf = fields.Boolean(
        string='MAF',
        required=False)
    conclusion_1 = fields.Text(
        string="Conclusion",
        sanitize_style=True,
        required=False)

    date_2nd_trimester = fields.Date(
        string='Date',
        required=False)
    conclusion_2 = fields.Text(
        string="Conclusion",
        sanitize_style=True,
        required=False)

    date_3rd_trimester = fields.Date(
        string='Date',
        required=False)
    conclusion_3 = fields.Text(
        string="Conclusion",
        sanitize_style=True,
        required=False)

    state = fields.Selection(
        string='State',
        selection=[('current', 'En cours'),
                   ('ended', 'Terminé'), ],
        required=False, )


