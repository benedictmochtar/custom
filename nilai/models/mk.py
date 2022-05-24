from odoo import models, fields, api, _
# _ untuk translate

class mk(models.Model):
    _name = 'nilai.mk'
    _description = 'class untuk berlatih tentang mk'
    _rec_name = 'namaMk'
    _order = 'namaMk asc'

    namaMk = fields.Char('Nama MK', size=64, required=True, index=True, readonly=True,states={'draft': [('readonly', False)]})
    kodeMk = fields.Char('Kode MK', size=64, required=True, index=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    sks = fields.Integer('SKS', required=True, index=True, readonly=True,
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