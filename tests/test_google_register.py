import json
import os
import unittest
from unittest.mock import patch
import test_commitments
import commitments

class GoogleRegisterTest(unittest.TestCase):
    setUp = test_commitments.CommitmentsTest.setUp
    tearDown = test_commitments.CommitmentsTest.tearDown
    def row(self):
        return ['APL-007', 'Aster', 'Delete recordings', '2026-10-06', '', 'open',
                'aster-order-form.md', 'Amendment 1', '0', 'Confirmation']

    def test_sheet_is_review_source(self):
        with patch.dict(os.environ, LEGAL_GOOGLE_TOKEN='test'), patch.object(commitments, 'google', return_value=json.dumps({'values': [self.row()]}).encode()):
            result = commitments.execute('review_commitments', {})
        self.assertEqual(result['register_kind'], 'google_sheets_api')
        self.assertEqual(result["customer_count"], 1)
        self.assertEqual([r['id'] for r in result['commitments']], ['APL-007'])

    def test_write_readback(self):
        row, calls = self.row(), []
        def api(url, method='GET', payload=None):
            calls.append(method)
            if method == 'POST':
                row[4], row[8] = 'Khizar', '1'
                return b'{}'
            return json.dumps({'values': [row]}).encode()
        with patch.dict(os.environ, LEGAL_GOOGLE_TOKEN='test'), patch.object(commitments, 'google', side_effect=api):
            result = commitments.execute('assign_owner', {'commitment_id': 'APL-007', 'owner': 'Khizar', 'expected_revision': 0})
        self.assertEqual(result['sheet_sync'], 'google_sheets_api_verified')
        self.assertEqual(calls[-2:], ['POST', 'GET'])
        self.assertEqual(result['previous_owner'], '')
        self.assertEqual(result['new_owner'], 'Khizar')
        self.assertIn('owner changed from unassigned to Khizar', result['slack_reply'])
        self.assertIn('Verified in Google Sheets at revision 1', result['slack_reply'])
        self.assertIn('/edit#gid=0&range=A2%3AJ2', result['commitment']['sheet_url'])
        self.assertIn(result['commitment']['sheet_url'], result['slack_reply'])

    def test_receipt_preserves_previous_owner_and_custom_tab_link(self):
        row = self.row()
        row[4] = 'Anthony'
        def api(url, method='GET', payload=None):
            if method == 'POST':
                row[4], row[8] = 'Khizar', '1'
                return b'{}'
            return json.dumps({'values': [row]}).encode()
        with patch.dict(os.environ, LEGAL_GOOGLE_TOKEN='test'), patch.dict(commitments.INDEX, spreadsheet_gid=12345), patch.object(commitments, 'google', side_effect=api):
            result = commitments.execute('assign_owner', {'commitment_id': 'APL-007', 'owner': 'Khizar', 'expected_revision': 0})
        self.assertEqual(result['previous_owner'], 'Anthony')
        self.assertIn('from Anthony to Khizar', result['slack_reply'])
        self.assertIn('#gid=12345&range=A2%3AJ2', result['slack_reply'])

    def test_failed_verification_leaves_local_state_untouched(self):
        def api(url, method='GET', payload=None):
            return b'{}' if method == 'POST' else json.dumps({'values': [self.row()]}).encode()
        with patch.dict(os.environ, LEGAL_GOOGLE_TOKEN='test'), patch.object(commitments, 'google', side_effect=api):
            with self.assertRaisesRegex(RuntimeError, 'could not be verified'):
                commitments.execute('assign_owner', {'commitment_id': 'APL-007', 'owner': 'Khizar', 'expected_revision': 0})
        self.assertFalse(commitments.STATE.exists())

    def test_duplicates_fail(self):
        with patch.dict(os.environ, LEGAL_GOOGLE_TOKEN='test'), patch.object(commitments, 'google', return_value=json.dumps({'values': [self.row()] * 2}).encode()):
            with self.assertRaisesRegex(RuntimeError, 'duplicate'):
                commitments.execute('review_commitments', {})

    def test_token_file_is_reread_and_invalid_file_fails(self):
        path = commitments.STATE.parent / 'token.json'
        os.environ['LEGAL_GOOGLE_TOKEN_FILE'] = str(path)
        path.write_text('{"access_token":"first"}')
        self.assertEqual(commitments.google_token(), 'first')
        path.write_text('{"access_token":"second"}')
        self.assertEqual(commitments.google_token(), 'second')
        path.write_text('{"refresh_token":"unsupported"}')
        with self.assertRaisesRegex(RuntimeError, 'access token'):
            commitments.google_token()

    def test_sheet_range_has_no_hundred_row_cutoff(self):
        from urllib.parse import unquote
        observed = []
        def api(url, method='GET', payload=None):
            observed.append(unquote(url))
            values = []
            for number in range(120):
                row = self.row()
                row[0] = f'APL-{number:03}'
                values.append(row)
            return json.dumps({'values': values}).encode()
        with patch.dict(os.environ, LEGAL_GOOGLE_TOKEN='test'), patch.dict(
                commitments.INDEX, spreadsheet_tab="Counsel's review"), patch.object(commitments, 'google', side_effect=api):
            result = commitments.execute('review_commitments', {})
        self.assertEqual(result['count'], 120)
        self.assertTrue(observed[0].endswith("'Counsel''s review'!A2:J"))
