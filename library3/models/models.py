from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
from datetime import datetime as dt


class Library(models.Model):
    _name = 'library.books'

    _description = 'UTS'

    name = fields.Char(string="ISBN", required=False)
    # author = fields.Char(string="Author", required=False)
    # editor = fields.Char(string="Editor", required=False)
    year = fields.Char(string="Year of Edition", required=False)
    book_name = fields.Char(string="Book Title", required=False)
    # summary= fields.Text()
    stock_of_books = fields.Integer(string="Number of Books")

    instructor_id = fields.Many2one('res.partner', string="Instructor",
                                    domain=['|', ('instructor', '=', True),
                                            ('category_id.name', 'ilike', "Teacher")])

    librarian_id = fields.Many2one('library.librarian', string="Library Admin", index=True)
    about_ids = fields.Many2many('library.about', ondelete="cascade", string="About", required=True)

    taken_books = fields.Float(string="Available", compute='_taken_books')
    available = fields.Integer(string="Stock", required=False)

    # taken_books = fields.Float(string="Taken Books", compute='_taken_books')
    # rentals_ids = fields.Many2one('library.rentals', ondelete='cascade')
    # stock_change = fields.Integer(compute='_stock_change', store=True)

    # @api.depends("rentals_ids", "rentals_ids.end_date", "rentals_ids.return_date")
    # def _stock_change(self):
    #     for lib in self:
    #         for rec in lib.rentals_ids.filtered(lambda s: s.state == 'returned' or s.state == 'borrowed'):
    #             if rec.state == 'returned':
    #                 rec.stock += 1
    #
    #             elif rec.state == 'borrowed':
    #                 rec.stock -= 1



    @api.depends('available')
    def _taken_books(self):
        for r in self:
            if not r.available:
                r.taken_books = 0.0
            else:
                r.taken_books = 100.0 * len(r.name) / r.available



    @api.onchange('available')
    def _verfy_books(self):
        if self.available < 0:
            return {
                'warning': {
                    'title': "Incorrect valaue",
                    'message': "The number of available books may not be negative"
                }
            }
        if self.available < len(self):
            return {
                'warning': {
                    'title': "Book Error",
                    'message': "Increase or remove excess books"
                }
            }


    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Library, self).copy(default)

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the books should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]


class Rental(models.Model):
    _name = 'library.rentals'
    # _inherit = 'library.books'
    _description = "Book Rentals"
    # _inherits = {'library.books': 'librarian_id'}

    # name = fields.Many2one('library.members', ondelete="cascade", string="Borrower's Name", required=False)
    name = fields.Many2one('library.members', ondelete="cascade", string="Borrower's Name")
    lib_info = fields.Char(string="Library ID", required=False)
    start_date = fields.Date('Start Date', default=fields.Date.context_today, readonly=True,
                       states={'draft': [('readonly', False)]})
    end_date = fields.Date("End Date", readonly=True,
                           states={'draft': [('readonly', False)]})
    return_date = fields.Date("Return Date", readonly=True,
                              states={'returned': [('readonly', False)]})

    active = fields.Boolean(default=True)
    days_difference = fields.Integer(compute='_days_difference', store=True)
    # total_days = fields.Integer(related="days_difference.total_days")
    cost = fields.Float(readonly=True, default=1000)
    fine = fields.Float(store=True, default=0, compute="_fine", readonly=True)


    state = fields.Selection(
        [('draft', 'Draft'),  # draft--> key, secara technical yang disimpan di dbase, Draft: value yang dilihat user
         ('borrowed', 'Borrowed'),
         ('returned', 'Returned'),
         ('payed', 'Payed')], 'State', required=True, readonly=True,  # krn required, sebaiknya dikasi default
        default='draft')

    available_change = fields.Integer(compute='_available_change', store=True)

    @api.depends("book_ids", "end_date", "return_date", "book_ids.available")
    def _available_change(self):
         for rec in self.filtered(lambda s: s.state == 'returned' or s.state == 'borrowed'):
            if rec.state == 'returned':
                rec.book_ids.available += 1

            elif rec.state == 'borrowed':
                 rec.book_ids.available -= 1

    @api.depends("start_date", "end_date", "return_date")
    def _days_difference(self):
        if self.end_date and self.return_date:
            for rec in self:
                rec.days_difference = int((rec.return_date - rec.end_date).days)

    @api.depends("start_date", "end_date", "return_date")
    def _fine(self):
        for rec in self:
            rec.fine = rec.days_difference * 1000

    librarian_id = fields.Many2one('library.librarian', string="Library on Duty", index=True)
    book_ids = fields.Many2many('library.books', ondelete="cascade", string="Records", required=True)

    @api.depends('book_ids.available')
    # def _taken_books(self):
    #     for r in self:
    #         if not r in self:
    #             r.taken_books = 0.0
    #         else:
    #             r.taken_books = 100.0 * len(r.name) / r.stock

    @api.onchange('available')
    def _verfy_books(self):
        if self.book_ids.available < 0:
            return {
                'warning': {
                    'title': "Incorrect valaue",
                    'message': "The number of available books may not be negative"
                }
            }
        if self.book_ids.available < len(self):
            return {
                'warning': {
                    'title': "Book Error",
                    'message': "Increase or remove excess books"
                }
            }



    def action_returned(self):
        self.state = 'returned'



    def action_payed(self):
        self.state = 'payed'

    def action_borrowed(self):
        self.state = 'borrowed'


    def action_settodraft(self):
        self.state = 'draft'

    @api.depends('book_ids', 'book_ids.available', 'book_ids.stock_of_books')


    @api.depends('available', 'book_ids')
    def _taken_books(self):
	    for r in self:
		    if not r in self:
			    r.taken_books = 0.0
		    else:
			    r.taken_books = 100 * len(r.book_ids)/r.api

    def action_borrowed(self):
        self.state = 'borrowed'
        if self.name == 'new' or not self.name:
            seq = self.env['ir.sequence'].search([("code", "=", "library.rentals")])
            if not seq:
                raise UserError(_("library.rentals sequence not found, please create library.rentals sequence"))
            self.name = seq.next_by_id(sequence_date=self.date)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence'].search([("code", "=", "library.rentals")])
        if not seq:
            raise UserError(_("library.rentals sequence not found, please create library.rentals sequence"))
        for val in vals_list:
            val['name'] = seq.next_by_id(sequence_date=val['date'])

        return super(Rental, self).create(vals_list)


class About(models.Model):
    _name = 'library.about'
    _description = "Authors Editors"

    author = fields.Char(string="Author/s", required=False)
    # author=fields.Char(string="Author/s", required=False)
    editor = fields.Char(string="Editor/s", required=False)
    summary = fields.Text()

# isbn_id = fields.Many2one('library.books.isbn', ondelete="cascade", string="ISBN", required=False)
# member_id = fields.Many2one('library.members', ondelete="cascade", string="Borrower's Name", required=False)
# taken_books = fields.Float(string="Taken Books", compute="_taken_books")




#
class Librarian(models.Model):
    _name = "library.librarian"
    _description = "Library Librarian"

    name = fields.Char(string="First Name", required=True)
    lname = fields.Char(string="Last Name", required=False)
    phone = fields.Char(string="Phone", required=False)
    email = fields.Char(string="Email", required=False)
    lib_info = fields.Char(string="Librarian ID", required=False)
    address = fields.Text(string="Address", required=False)


class Member(models.Model):
    _name = "library.members"
    _description = "Library Member"

    name = fields.Char(string="First Name", required=False)
    lname = fields.Char(string="Last Name", required=False)
    phone = fields.Char(string="Phone", required=False)
    email = fields.Char(string="Email", required=False)
    visit_info = fields.Char(string="Library ID", required=False)
    address = fields.Text(string="Address", required=False)
    rentals_ids = fields.Many2one('library.rentals', index=True)
    cost = fields.Float(readonly=True, default=1000)
    total = fields.Float(store=True, compute="_total")




