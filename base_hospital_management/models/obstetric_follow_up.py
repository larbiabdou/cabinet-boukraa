from odoo import api, fields, models


class ObstetricFollowUp(models.Model):
    _name = 'obstetric.follow.up'
    _description = 'Obstetric Follow-up'
    _rec_name = 'patient_id'

    patient_id = fields.Many2one(
        comodel_name='res.partner',
        string='Patient',
        required=False)

    date_1st_trimester = fields.Date(
        string='Date',
        required=False)

    g_1 = fields.Char(
        string='G',
        required=False)
    p_1 = fields.Char(
        string='P',
        required=False)
    c_1 = fields.Char(
        string='C',
        required=False)
    a_1 = fields.Char(
        string='A',
        required=False)
    ddr = fields.Date(
        string='DDR',
        required=False)
    dpr = fields.Date(
        string='DPA',
        required=False)
    sac_gestationnel = fields.Selection(
        string='Sac gestationnel',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
        
    ac = fields.Selection(
        string='AC',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )

    vv = fields.Selection(
        string='VV',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )

    lcc_1 = fields.Float(
        string='LCC',
        required=False)

    cn = fields.Selection(
        string='CN',
        selection=[('fine', 'Fine'),
                   ('épaisse', 'Epaisse'), ],
        required=False)
    pole_cephalique = fields.Selection(
        string='Pole cephalique',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    membre_4 = fields.Selection(
        string='4 membres + 3 segments',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    trophoblaste = fields.Selection(
        string='Trophoblaste',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    maf = fields.Selection(
        string='MAF',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    conclusion_1 = fields.Text(
        string="Conclusion",
        sanitize_style=True,
        required=False)

    date_2nd_trimester = fields.Date(
        string='Date',
        required=False)
    grossesse_2 = fields.Char(
        string='Grossesse',
        required=False)

    ac_2 = fields.Char(
        string='AC',
        required=False)
    maf_2 = fields.Char(
        string='MAF',
        required=False)
    bip_2 = fields.Char(
        string='BIP',
        required=False)
    femur_2 = fields.Char(
        string='FEMEUR',
        required=False)
    poids_2 = fields.Float(
        string='Poids',
        required=False)
    face_2 = fields.Selection(
        string='Face',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    nez_bouche_2 = fields.Selection(
        string='Nez-Bouche',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    estomac_2 = fields.Selection(
        string='Estomac',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    rachis_2 = fields.Selection(
        string='Rachis',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )

    liquide_amni_2 = fields.Selection(
        string='Liquide amniotique',
        selection=[('normale', 'Normale'),
                   ('oligoamnios', 'Oligoamnios'), ('hydramnios', 'Hydramnios') ],
        required=False)

    placenta_2 = fields.Selection(
        string='Placenta',
        selection=[('antérieur', 'Antérieur'),
                   ('postérieur', 'Postérieur'), ('fundique', 'Fundique'), ('bas_inséré', 'Bas inséré')],
        required=False)

    hearth_2 = fields.Selection(
        string='Coeur et vx',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False)
    membres_2 = fields.Selection(
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        string='Membres', 
        required=False)

    reins_2 = fields.Selection(
        string='Reins et vessie',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False)
    presentation_2 = fields.Html(
        string="Presentation",
        required=False)
    conclusion_2 = fields.Html(
        string="Conclusion",
        sanitize_style=True,
        required=False)

    date_3nd_trimester = fields.Date(
        string='Date',
        required=False)
    grossesse_3 = fields.Char(
        string='Grossesse',
        required=False)

    ac_3 = fields.Char(
        string='AC',
        required=False)
    maf_3 = fields.Char(
        string='MAF',
        required=False)
    bip_3 = fields.Char(
        string='BIP',
        required=False)
    femur_3 = fields.Char(
        string='FEMEUR',
        required=False)
    poids_3 = fields.Float(
        string='Poids',
        required=False)
    face_3 = fields.Selection(
        string='Face',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    nez_bouche_3 = fields.Selection(
        string='Nez-Bouche',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    estomac_3 = fields.Selection(
        string='Estomac',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )
    rachis_3 = fields.Selection(
        string='Rachis',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False, )

    liquide_amni_3 = fields.Selection(
        string='Liquide amniotique',
        selection=[('normale', 'Normale'),
                   ('oligoamnios', 'Oligoamnios'), ('hydramnios', 'Hydramnios')],
        required=False)

    placenta_3 = fields.Selection(
        string='Placenta',
        selection=[('antérieur', 'Antérieur'),
                   ('postérieur', 'Postérieur'), ('fundique', 'Fundique'), ('bas_inséré', 'Bas inséré')],
        required=False)

    hearth_3 = fields.Selection(
        string='Coeur et vx',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False)
    membres_3 = fields.Selection(
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        string='Membres',
        required=False)

    reins_3 = fields.Selection(
        string='Reins et vessie',
        selection=[('vu', 'Vu'),
                   ('non_vue', 'Non vue'), ],
        required=False)
    presentation_3 = fields.Html(
        string="Presentation",
        required=False)
    conclusion_3 = fields.Html(
        string="Conclusion",
        sanitize_style=True,
        required=False)

    state = fields.Selection(
        string='State',
        selection=[('current', 'En cours'),
                   ('ended', 'Terminé'), ],
        default="current",
        required=False, )


