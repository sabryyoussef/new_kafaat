# -*- coding: utf-8 -*-
"""
Historical partner/student batch_intake_id sync utility.

Purpose
-------
Fix legacy TR_K19 rows where ``op.student.batch_intake_id`` was updated during
batch intake processing but ``res.partner.batch_intake_id`` was left stale.

New intake writes are already handled by ``OpStudent.write()`` in
``edafaa_batch_intake.models.batch_intake`` — do not run this script unless
you intentionally need to backfill historical data.

Safety
------
* Dry-run by default (no writes).
* Pass ``--execute`` to apply changes after reviewing the printed list.
* Do not execute on production/staging without explicit client sign-off.

Suggested SQL (documentation only — prefer this script for audit output)::

    UPDATE res_partner p
    SET batch_intake_id = s.batch_intake_id
    FROM op_student s
    WHERE s.partner_id = p.id
      AND s.batch_intake_id IS NOT NULL
      AND (p.batch_intake_id IS NULL OR p.batch_intake_id != s.batch_intake_id);

Usage
-----
From Odoo shell::

    exec(open('/opt/localaddons/edafaa_batch_intake/scripts/sync_student_partner_batch_intake.py').read())
    run_sync(dry_run=True)   # list only
    run_sync(dry_run=False)  # apply after approval

Or with CLI wrapper (see ``if __name__ == '__main__'``).
"""

from __future__ import annotations

import argparse
import logging

_logger = logging.getLogger(__name__)

MISMATCH_QUERY = """
    SELECT
        s.id AS student_id,
        s.name_english AS student_name,
        p.id AS partner_id,
        p.name AS partner_name,
        s.batch_intake_id AS student_intake_id,
        bi_s.name AS student_intake_name,
        p.batch_intake_id AS partner_intake_id,
        bi_p.name AS partner_intake_name
    FROM op_student s
    JOIN res_partner p ON p.id = s.partner_id
    LEFT JOIN batch_intake bi_s ON bi_s.id = s.batch_intake_id
    LEFT JOIN batch_intake bi_p ON bi_p.id = p.batch_intake_id
    WHERE s.batch_intake_id IS NOT NULL
      AND s.partner_id IS NOT NULL
      AND (p.batch_intake_id IS NULL OR p.batch_intake_id != s.batch_intake_id)
    ORDER BY s.id
"""


def find_mismatches(env):
    """Return list of dict rows that need partner sync."""
    env.cr.execute(MISMATCH_QUERY)
    columns = [desc[0] for desc in env.cr.description]
    return [dict(zip(columns, row)) for row in env.cr.fetchall()]


def run_sync(env, dry_run=True):
    """
    Sync partner batch_intake_id from student for historical mismatches only.

    :param env: Odoo Environment (typically from odoo shell).
    :param dry_run: When True, only print affected records; no writes.
    :return: dict with counts and row details.
    """
    rows = find_mismatches(env)
    result = {
        'dry_run': dry_run,
        'found': len(rows),
        'updated': 0,
        'rows': rows,
    }

    if not rows:
        _logger.info('No partner/student batch_intake_id mismatches found.')
        print('No mismatches found.')
        return result

    print(f'Found {len(rows)} mismatch(es):')
    for row in rows:
        print(
            f"  student {row['student_id']} ({row['student_name']}): "
            f"student_intake={row['student_intake_name'] or row['student_intake_id']} "
            f"partner_intake={row['partner_intake_name'] or row['partner_intake_id'] or 'empty'}"
        )

    if dry_run:
        print('Dry-run only — no changes written. Pass dry_run=False to apply.')
        return result

    Student = env['op.student'].sudo()
    for row in rows:
        student = Student.browse(row['student_id'])
        if not student.exists() or not student.batch_intake_id or not student.partner_id:
            continue
        partner = student.partner_id
        if partner.batch_intake_id == student.batch_intake_id:
            continue
        partner.write({'batch_intake_id': student.batch_intake_id.id})
        result['updated'] += 1
        print(
            f"  updated partner {partner.id}: "
            f"{row['partner_intake_name'] or 'empty'} -> {student.batch_intake_id.name}"
        )

    env.cr.commit()
    print(f'Applied {result["updated"]} partner update(s).')
    return result


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Sync res.partner.batch_intake_id from op.student (historical cleanup).',
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Apply writes. Default is dry-run (list only).',
    )
    parser.add_argument('-d', '--database', default='TR_K19', help='Odoo database name.')
    parser.add_argument('-c', '--config', default='/etc/odoo/odoo.conf', help='Odoo config file.')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    import odoo
    from odoo.modules.registry import Registry
    from odoo.tools import config as odoo_config

    odoo_config.parse_config(['-c', args.config, '-d', args.database])
    registry = Registry(args.database)
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        run_sync(env, dry_run=not args.execute)
