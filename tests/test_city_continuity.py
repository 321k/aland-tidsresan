import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from city_continuity import reconcile


def roof(identity='house', shift=0, width=.0003):
    x, y = 19.94 + shift, 60.10
    return {'id': identity, 'paths': [[[x, y], [x + width, y], [x + width, y + .00015], [x, y + .00015], [x, y]]]}


def snapshot(year, *features):
    return {'year': year, 'features': list(features)}


class ContinuityTest(unittest.TestCase):
    def test_minor_survey_correction_is_stable_but_not_backdated(self):
        a, b = roof(), roof(shift=.00001)
        data = [snapshot(2000), snapshot(2014, a), snapshot(2021, b)]
        reconcile(data)
        self.assertEqual(data[0]['features'], [])
        self.assertEqual(a['paths'], b['paths'])
        self.assertEqual(a['geometryYear'], 2021)

    def test_large_move_and_extension_remain_real_source_changes(self):
        for later in [roof(shift=.0005), roof(width=.0006)]:
            old = roof()
            reconcile([snapshot(2014, old), snapshot(2021, later)])
            self.assertNotEqual(old['paths'], later['paths'])
            self.assertNotIn('geometryYear', old)

    def test_gap_is_bridged_only_between_two_observations(self):
        data = [snapshot(2000), snapshot(2014, roof()), snapshot(2021), snapshot(2025, roof()), snapshot(2026)]
        reconcile(data)
        self.assertEqual(data[0]['features'], [])
        self.assertEqual(data[4]['features'], [])
        self.assertEqual(data[2]['features'][0]['continuity'], {'lastSeenYear': 2014, 'nextSeenYear': 2025})

    def test_replacement_or_changed_identity_does_not_get_a_ghost_duplicate(self):
        data = [snapshot(2014, roof()), snapshot(2021, roof('replacement')), snapshot(2025, roof())]
        reconcile(data)
        self.assertEqual(len(data[1]['features']), 1)
        other = [snapshot(2014, roof()), snapshot(2021), snapshot(2025, roof('new-id'))]
        reconcile(other)
        self.assertEqual(other[1]['features'], [])

    def test_chain_of_small_edits_cannot_absorb_a_large_change(self):
        data = [snapshot(2014, roof()), snapshot(2021, roof(shift=.00003)), snapshot(2025, roof(shift=.00006)), snapshot(2026, roof(shift=.00009))]
        reconcile(data)
        self.assertNotEqual(data[0]['features'][0]['paths'], data[-1]['features'][0]['paths'])


if __name__ == '__main__':
    unittest.main()
