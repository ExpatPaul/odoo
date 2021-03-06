# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from odoo import tools


class ReportEventRegistration(models.Model):
    """Events Analysis"""
    _name = "report.event.registration"
    _order = 'event_date desc'
    _auto = False

    create_date = fields.Datetime('Creation Date', readonly=True)
    event_date = fields.Datetime('Event Date', readonly=True)
    event_id = fields.Many2one('event.event', 'Event', required=True)
    draft_state = fields.Integer(' # No of Draft Registrations')
    cancel_state = fields.Integer(' # No of Cancelled Registrations')
    confirm_state = fields.Integer(' # No of Confirmed Registrations')
    seats_max = fields.Integer('Max Seats')
    nbevent = fields.Integer('Number of Events')
    nbregistration = fields.Integer('Number of Registrations')
    event_type_id = fields.Many2one('event.type', 'Event Type')
    registration_state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Attended'), ('cancel', 'Cancelled')], 'Registration State', readonly=True, required=True)
    event_state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')], 'Event State', readonly=True, required=True)
    user_id = fields.Many2one('res.users', 'Event Responsible', readonly=True)
    name_registration = fields.Char('Participant / Contact Name', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    def _select(self):
        return """
            SELECT
                e.id::varchar || '/' || coalesce(r.id::varchar,'') AS id,
                e.id AS event_id,
                e.user_id AS user_id,
                r.name AS name_registration,
                r.create_date AS create_date,
                e.company_id AS company_id,
                e.date_begin AS event_date,
                count(r.id) AS nbevent,
                count(r.event_id) AS nbregistration,
                CASE WHEN r.state IN ('draft') THEN count(r.event_id) ELSE 0 END AS draft_state,
                CASE WHEN r.state IN ('open','done') THEN count(r.event_id) ELSE 0 END AS confirm_state,
                CASE WHEN r.state IN ('cancel') THEN count(r.event_id) ELSE 0 END AS cancel_state,
                e.event_type_id AS event_type_id,
                e.seats_max AS seats_max,
                e.state AS event_state,
                r.state AS registration_state
            """

    def _from(self):
        return """
            FROM
                event_event e
                LEFT JOIN event_registration r ON (e.id=r.event_id)
            """

    def _group_by(self):
        return """
            GROUP BY
                event_id,
                r.id,
                registration_state,
                event_type_id,
                e.id,
                e.date_begin,
                e.user_id,
                event_state,
                e.company_id,
                e.seats_max,
                name_registration
            """

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            "CREATE or REPLACE VIEW %s as (%s %s %s)" % (
                self._table, self._select(), self._from(), self._group_by(),
            )
        )
