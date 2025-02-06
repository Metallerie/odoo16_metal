from odoo import api, fields, models, _, tools, exceptions
from datetime import datetime
import pytz
import re

class Email(models.Model):
    _name = 'email.record'
    _rec_name = 'subject'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Email Record'

    subject = fields.Char('Subject')
    to = fields.Many2many('res.partner', 'rel_to_email', string="To", ondelete="restrict")
    cc = fields.Many2many('res.partner', 'rel_cc_email', string="Cc", ondelete="restrict")
    sender = fields.Many2one('res.partner', string="From", readonly=True, ondelete="restrict", compute='_get_sender', store=True)
    body = fields.Html(string="Body")
    priority = fields.Selection([('0', 'Low'), ('1', 'Medium'), ('2', 'High'), ('3', 'Very High')], string='Priority',
                                default='0', track_visibility='onchange')
    type = fields.Selection([('draft', 'Draft'), ('outgoing', 'Outgoing'), ('incoming', 'Incoming')], string='Type',
                            default='draft', readonly=True)
    date_time = fields.Datetime(string='Date', default=lambda self: fields.datetime.now(), readonly=True)
    tags = fields.Many2many('email.tags', 'rel_email_tags', string="Tags")
    attachments = fields.Many2many('ir.attachment', 'email_record_attachment_relation', 'res_id', 'attachment_id',
                                   string='Attachments')
    attachment_icon = fields.Boolean(compute="_attachment_icon_compute")
    parent_exists = fields.Boolean('Check Parent')

    # Email will only be visible/accessible to the users added in this field:
    associated_users = fields.Many2many('res.users', 'email_user_relation', default=lambda self: self.env.user,
                                        string='Associated Users', readonly=True)
    message_id = fields.Char('Message ID')

    @api.depends('type')
    def _get_sender(self):
        for rec in self:
            if rec.type and rec.type != 'incoming':
                rec.sender = self.env['res.users'].browse(self._context.get('uid')).partner_id

    @api.model
    def default_get(self, fields):
        res = super(Email, self).default_get(fields)
        if not self.env['email.record'].browse(self.env.context.get('active_ids')):
            res['body'] = "<p><br/></p>" + self.env.user.signature
        res['parent_exists'] = True if self.env['email.record'].browse(self.env.context.get('active_ids')) else False
        return res

    @api.depends('attachments')
    def _attachment_icon_compute(self):
        for rec in self:
            if rec.attachments:
                rec.attachment_icon = True
            else:
                rec.attachment_icon = False

    @api.model
    def create(self, val):
        val['date_time'] = fields.datetime.now()
        res = super(Email, self).create(val)
        return res

    def get_partner_emails(self, partners):
        return str([partner.email for partner in partners]).replace('[', '').replace(']', '').replace("'", "")

    def validate_partner_emails(self, partners):
        for rec in partners:
            if rec.email:
                match = re.match('[^@]+@[^@]+\.[^@]+', rec.email)
                if match == None:
                    raise exceptions.UserError(_("%s has an invalid email address") % rec.name)
            else:
                raise exceptions.UserError(_('%s does not have any email address.') % rec.name)
        return True

    def send_email(self):
        self.validate_partner_emails(self.to)
        self.validate_partner_emails(self.cc)
        template = self.env.ref("rt_mail_plugin.send_email_template").sudo()
        template.attachment_ids = self.attachments
        if not self.subject:
            self.subject = '(No subject)'
        mail_id = template.send_mail(res_id=self.id, force_send=True)
        self.type = 'outgoing'
        self.date_time = fields.datetime.now()
        self.parent_exists = False
        self.log_message_history(message="Email", key=self.env.context.get('key'))

    def reply_popup(self):
        body_text = tools.html_sanitize(self.body)
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        display_date_time = datetime.strftime(
            pytz.utc.localize(self.date_time).astimezone(
                local), "%a, %b %d, %Y at %H:%M")
        arr = self.to if self.type == 'outgoing' else self.sender
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compose Reply',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('rt_mail_plugin.email_form_view').id,
            'res_model': 'email.record',
            'context': {
                'default_subject': 'Re: ' + self.subject,
                'default_to': [rec.id for rec in arr],
                'default_body': '<p><br><br></p>' + self.env.user.signature + '<span style="display:none;">[{!-body_delimiter-!}]</span><br>' + 'On ' + str(
                    display_date_time) + ' ' +
                                self.sender.display_name + ' &lt;' + self.sender.email + '&gt; wrote:<br>' +
                                '<hr style="height:0.01em; background-color:black;">' + str(body_text)
            }
        }

    def forward_popup(self):
        body_text = tools.html_sanitize(self.body)
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        display_date_time = datetime.strftime(
            pytz.utc.localize(self.date_time).astimezone(
                local), "%a, %b %d, %Y at %H:%M")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compose Forward',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('rt_mail_plugin.email_form_view').id,
            'res_model': 'email.record',
            'context': {
                'default_subject': 'Fwd: ' + self.subject,
                'default_attachments': [rec.id for rec in self.attachments],
                'default_body': '<p><br><br></p>' + self.env.user.signature + '<span style="display:none;">[{!-body_delimiter-!}]</span><br>' + '---------- Forwarded message ----------' +
                                '<br>From: <b>' + self.sender.display_name + '</b> &lt;' + self.sender.email + '&gt;' +
                                '<br>Date: ' + str(display_date_time) +
                                '<br>Subject: ' + self.subject +
                                '<br>To: ' + str([rec.name + ' &lt;' + rec.email + '&gt;' for rec in self.to])
                                    .replace('[', '').replace(']', '').replace("'", "") +
                                '<br>Cc: ' + str([rec.name + ' &lt;' + rec.email + '&gt;' for rec in self.cc])
                                    .replace('[', '').replace(']', '').replace("'", "") +
                                '<hr style="height:0.01em; background-color:black;"><br>' + str(body_text)
            }
        }

    def get_emails(self, contacts):
        recipients = []
        if contacts == '':
            return recipients

        contact_list = contacts.split(",")
        for rec in contact_list:
            rec_copy = rec
            if "<" and ">" in rec:
                recipients.append(
                    {'name': rec_copy.split('<')[0].strip(), 'email': rec[rec.index('<') + len('<'):rec.index('>')]})
            else:
                recipients.append({'name': rec_copy.split('@')[0].strip(), 'email': rec})

        return recipients

    def get_contact_ids(self, contact_list):
        new_contacts_created = []
        users = self.env['res.users'].search([])
        for contact in contact_list:
            existing_record = None
            for user in users:
                if user.partner_id.email == contact['email']:
                    existing_record = user.partner_id
            if not existing_record:
                existing_record = self.env['res.partner'].search([('email', '=ilike', contact['email'])], order='id desc',
                                                             limit=1)
            if len(existing_record) > 0:
                new_contacts_created.append(int(existing_record.id))
            else:
                new_record = self.env['res.partner'].create(
                    {'name': str(contact['name']).replace('"', '').replace("'", ""), 'email': contact['email']})
                if new_record.id:
                    new_contacts_created.append(int(new_record.id))

        return new_contacts_created

    def filter_associated_users(self, contact_ids):
        associated_user_contacts = []
        if contact_ids:
            for contact_id in contact_ids:
                all_users = self.env['res.users'].search([])
                for user in all_users:
                    if user.partner_id.id == contact_id:
                        incoming_server = self.env['fetchmail.server'].sudo().search([('user', '=ilike', user.email)])
                        if incoming_server: #only those users will be added in the associated user whose emails are configured and matched with one of the incoming email servers
                            associated_user_contacts.append(user.id)
        return associated_user_contacts

    def message_new(self, msg, custom_values=None):
        to_contact_ids = self.get_contact_ids(self.get_emails(msg.get('to')))
        cc_contact_ids = self.get_contact_ids(self.get_emails(msg.get('cc')))
        from_contact_ids = self.get_contact_ids(self.get_emails(msg.get('from')))
        associated_users = []
        associated_users.extend(self.filter_associated_users(to_contact_ids))
        associated_users.extend(self.filter_associated_users(cc_contact_ids))
        # associated_users.extend(self.filter_associated_users(sender_contact_ids))

        vals = {
            "to": to_contact_ids,
            "cc": cc_contact_ids,
            "sender": from_contact_ids[0],
            'subject': msg.get('subject'),
            "type": 'incoming',
            "date_time": fields.datetime.strptime(msg.get('date'), "%Y-%m-%d %H:%M:%S"),
            'body': tools.html_sanitize(msg.get('body')),
            'associated_users': associated_users,
            'message_id': msg.get('message_id'),
        }
        res = super(Email, self).message_new(msg, custom_values=vals)
        return res

    def _message_post_after_hook(self, message, msg_vals):
        fetched_attachments = self.env['ir.attachment'].search(
            [('res_model', '=', 'email.record'), ('res_id', '=', msg_vals.get('res_id'))])
        if fetched_attachments:
            self.attachments = fetched_attachments
            return super(Email, self)._message_post_after_hook(message, msg_vals)

    def log_message_history(self, message=None, key=None):
        parent_record_id = self.env['email.record'].browse(self.env.context.get('active_ids'))
        record_url = '/web#id=' + str(self._origin.id) + '&model=email.record&view_type=form'
        self.message_post(body=message + " " + key)
        parent_record_id.message_post(
            body=message + ' ' + key + ", <a href='%s'>view record</a>" % record_url) if parent_record_id else None

