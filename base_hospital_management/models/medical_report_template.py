# -*- coding: utf-8 -*-
from odoo import api, fields, models
from jinja2 import Template
from datetime import datetime


class MedicalReportTemplate(models.Model):
    """Modèle pour les templates de rapports médicaux"""
    _name = 'medical.report.template'
    _description = "Template de rapport médical"
    _rec_name = 'report_type'

    report_type = fields.Selection([
        ('leave', 'Arrêt de travail'),
        ('extension', 'Prolongation d\'arrêt'),
        ('resumption', 'Reprise de travail'),
        ('referral', 'Lettre d\'orientation'),
        ('certificate', 'Certificat médical'),
    ], string="Type de rapport", required=True)

    content = fields.Html(string="Contenu du template", required=True)

    @api.onchange('report_type')
    def get_default_content(self):
        """Récupère le contenu par défaut selon le type de rapport"""
        templates = {
            'leave': '''
        <p>Je soussigné, <strong>Dr {{ user.name }}</strong>, certifie avoir vu et examiné ce jour 
        {%- if patient.gender == 'female' %} la patiente {%- else %} le patient {%- endif %} 
        <strong>{{ patient.name }}</strong></p>
        <br/>
        <p>Je déclare que son état de santé nécessite un arrêt de travail de <strong>{{ leave_duration }} jours</strong> à compter de ce jour, avec reprise à l'issue (sous réserve d'une réévaluation à l'issue de cette période).</p>
        <br/>
        <p><strong>Période d'arrêt :</strong> du {{ leave_start_date }} au {{ leave_end_date }}</p>
        <br/>
        <p>Ce certificat est délivré pour servir et valoir ce que de droit.</p>
        <br/><br/><br/>
        <p class="text-end">
            <strong>Date :</strong> {{ date }}<br/>
            <strong>Signature :</strong> &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        </p>
            ''',

            'extension': '''
        <p>Je soussigné, <strong>Dr {{ user.name }}</strong>, certifie avoir vu et examiné ce jour 
        {%- if patient.gender == 'female' %} la patiente {%- else %} le patient {%- endif %} 
        <strong>{{ patient.name }}</strong></p>
        <br/>
        <p>Je déclare que son état de santé nécessite une prolongation de son arrêt de travail de <strong>{{ extension_duration }} jours</strong> à compter de ce jour, avec reprise à l'issue (sous réserve d'une réévaluation à l'issue de cette période).</p>
        <br/>
        <p><strong>Période de prolongation :</strong> du {{ extension_start_date }} au {{ extension_end_date }}</p>
        <br/>
        <p>Ce certificat est délivré pour servir et valoir ce que de droit.</p>
        <br/><br/><br/>
        <p class="text-end">
            <strong>Date :</strong> {{ date }}<br/>
            <strong>Signature :</strong> &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        </p>
            ''',

            'resumption': '''
        <p>Je soussigné, <strong>Dr {{ user.name }}</strong>, certifie avoir vu et examiné ce jour 
        {%- if patient.gender == 'female' %} la patiente {%- else %} le patient {%- endif %} 
        <strong>{{ patient.name }}</strong></p>
        <br/>
        <p>Je déclare que son état de santé justifie la reprise du travail à <strong>{{ work_type }}</strong> à compter du <strong>{{ resume_work_date }}</strong>.</p>
        <br/>
        <p>Ce certificat est délivré pour servir et valoir ce que de droit.</p>
        <br/><br/><br/>
        <p class="text-end">
            <strong>Date :</strong> {{ date }}<br/>
            <strong>Signature :</strong> &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        </p>
            ''',

            'referral': '''
        <p>
            <strong>Cher confrère {{ colleague_name }},</strong>
        </p>
        <br/>
        <p>
            Permettez-moi de vous présenter le cas de 
            {%- if patient.gender == 'female' %} ma patiente {%- else %} mon patient {%- endif %}, 
            <strong>{{ patient.name }}</strong>, 
            {%- if patient.gender == 'female' %} âgée {%- else %} âgé {%- endif %} de <strong>{{ age }}</strong> ans, 
            que je vous confie pour {{ referral_reason }}.
        </p>
        <br/>
        <p>
            <strong>
            {%- if patient.gender == 'female' %}Elle{%- else %}Il{%- endif %} s'est 
            {%- if patient.gender == 'female' %}présentée{%- else %}présenté{%- endif %} 
            à notre consultation pour :
            </strong><br/>
            {{ consultation_reason }}
        </p>
        <br/>
        <p>
            <strong>Cliniquement :</strong><br/>
            {{ clinical_findings }}
        </p>
        <br/>
        <p>
            <strong>Diagnostic suspecté :</strong><br/>
            {{ suspected_diagnosis }}
        </p>
        <br/>
        <p>
            Je vous remercie par avance de l'attention que vous porterez à ce dossier.
        </p>
        <br/>
        <p>
            Bien cordialement,
        </p>
        <br/><br/>
        <p class="text-end">
            <strong>Dr {{ user.name }}</strong><br/>
            <strong>Date :</strong> {{ date }}<br/>
            <strong>Signature :</strong> &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        </p>
            ''',

            'certificate': '''
        <p>Je soussigné, <strong>Dr {{ user.name }}</strong>, certifie avoir vu et examiné ce jour 
        {%- if patient.gender == 'female' %} la patiente {%- else %} le patient {%- endif %} 
        <strong>{{ patient.name }}</strong>.</p>
        <br/>
        <p>
        {%- if patient.gender == 'female' %}Elle{%- else %}Il{%- endif %} s'est 
        {%- if patient.gender == 'female' %}présentée{%- else %}présenté{%- endif %} 
        à notre consultation pour <strong>{{ consultation_reason }}</strong>.
        </p>
        <br/>
        <p>L'examen radio clinique est revenu en faveur de <strong>{{ examination_result }}</strong>.</p>
        <br/>
        <p>Ce certificat est délivré pour servir et valoir ce que de droit.</p>
        <br/><br/><br/>
        <p class="text-end">
            <strong>Date :</strong> {{ date }}<br/>
            <strong>Signature :</strong> &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        </p>
            '''
        }
        for record in self:
            record.content = templates.get(record.report_type, '')

    @api.model
    def create_default_templates(self):
        """Créer les templates par défaut"""
        for report_type, label in self._fields['report_type'].selection:
            existing = self.search([('report_type', '=', report_type)])
            if not existing:
                self.create({
                    'report_type': report_type,
                    'content': self.get_default_content(report_type)
                })

    def render_template(self, context):
        """Rendre le template avec le contexte donné"""
        try:
            template = Template(self.content)
            return template.render(context)
        except Exception as e:
            # En cas d'erreur, retourner le contenu par défaut
            return self.get_default_content(context.get('report_type', 'leave'))