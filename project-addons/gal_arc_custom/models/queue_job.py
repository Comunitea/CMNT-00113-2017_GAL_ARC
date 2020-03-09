# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, exceptions, _
from odoo.osv import expression
from datetime import timedelta


class QueueJob(models.Model):

    _inherit = 'queue.job'

    @api.model
    def requeue_stuck_jobs(self, enqueued_delta=5, started_delta=0):
        """Fix jobs that are in a bad states
        :param in_queue_delta: lookup time in minutes for jobs
                                that are in enqueued state
        :param started_delta: lookup time in minutes for jobs
                                that are in enqueued state,
                                0 means that it is not checked
        """
        self._get_stuck_jobs_to_requeue(
            enqueued_delta=enqueued_delta,
            started_delta=started_delta
        ).requeue()
        return True

    @api.model
    def _get_stuck_jobs_domain(self, queue_dl, started_dl):
        domain = []
        now = fields.datetime.now()
        if queue_dl:
            queue_dl = now - timedelta(minutes=queue_dl)
            domain.append([
                '&',
                ('date_enqueued', '<=', fields.Datetime.to_string(queue_dl)),
                ('state', '=', 'enqueued'),
            ])
        if started_dl:
            started_dl = now - timedelta(minutes=started_dl)
            domain.append([
                '&',
                ('date_started', '<=', fields.Datetime.to_string(started_dl)),
                ('state', '=', 'started'),
            ])
        if not domain:
            raise exceptions.ValidationError(
                _("If both parameters are 0, ALL jobs will be requeued!")
            )
        return expression.OR(domain)

    @api.model
    def _get_stuck_jobs_to_requeue(self, enqueued_delta, started_delta):
        job_model = self.env['queue.job']
        stuck_jobs = job_model.search(self._get_stuck_jobs_domain(
            enqueued_delta,
            started_delta,
        ))
        return stuck_jobs
