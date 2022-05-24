from odoo import models, fields, api, _
# _ untuk translate

class mahasiswa(models.Model):
    _name = 'nilai.mahasiswa'
    _description = 'class untuk berlatih tentang mahasiswa'
    _rec_name = 'name'
    _order = 'name asc'

    name = fields.Char('Nama', size=64, required=True, index=True, readonly=True,states={'draft': [('readonly', False)]})
    nrp = fields.Char('NRP', size=64, required=True, index=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    ipk = fields.Float('IPK', required=True, index=True, readonly=True,
                      states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),], 'State', required=True, readonly=True,
                             default='draft')
    status = fields.Selection([('aktif', 'Aktif'),
                             ('tidakaktif', 'Tidak Aktif'),], 'Status', required=True, readonly=True, states={'draft': [('readonly', False)]})
    khs_ids = fields.One2many('nilai.khs', 'name', string='KHS', default=0)
    # voter_id = fields.Many2one('res.users', 'Voted By', readonly=True, ondelete="cascade", default=lambda self: self.env.user)
    # idea_id = fields.Many2one('idea.idea', string='Idea', readonly=True, ondelete="cascade", states={'draft': [('readonly', False)]},  domain="[('state', '=', 'done'),('active','=','True')]")

    def action_confirmed(self):
        self.state = 'confirmed'

    def action_settodraft(self):
        self.state = 'draft'