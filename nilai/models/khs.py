from odoo import models, fields, api, _
# _ untuk translate

class khs(models.Model):
    _name = 'nilai.khs'
    _description = 'class untuk berlatih tentang khs'
    _order = 'name asc'

    name = fields.Many2one('nilai.mahasiswa', 'Nama', index=True, readonly=True)
    semester = fields.Selection([('gasal', 'Gasal'),
                             ('genap', 'Genap'),], 'Semester', required=True, readonly=True, states={'draft': [('readonly', False)]})
    tahun = fields.Integer('Tahun', required=True, index=True, readonly=True,
                      states={'draft': [('readonly', False)]})
    ips = fields.Float('IPS', required=True, index=True, readonly=True,
                           states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),], 'State', required=True, readonly=True,
                             default='draft')
    status = fields.Selection([('aktif', 'Aktif'),
                             ('tidakaktif', 'Tidak Aktif'),], 'Status', required=True, readonly=True, states={'draft': [('readonly', False)]})

    # voter_id = fields.Many2one('res.users', 'Voted By', readonly=True, ondelete="cascade", default=lambda self: self.env.user)
    # idea_id = fields.Many2one('idea.idea', string='Idea', readonly=True, ondelete="cascade", states={'draft': [('readonly', False)]},  domain="[('state', '=', 'done'),('active','=','True')]")

    def action_confirmed(self):
        self.state = 'confirmed'

    def action_settodraft(self):
        self.state = 'draft'