"""Offline checks for automated profile writes and untrusted lookup responses."""
import base64
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sync_discord_profiles as syncer

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==')
USER_ID = "518251720128856084"
AVATAR_URL = f"https://cdn.discordapp.com/avatars/{USER_ID}/{'a'*32}.png?size=256"
BANNER_URL = f"https://cdn.discordapp.com/banners/{USER_ID}/{'b'*32}.png?size=1024"


class ProfileSyncTests(unittest.TestCase):
    def setUp(self):
        temporary_root = Path(__file__).resolve().parents[1] / '.preview'
        temporary_root.mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(prefix='discord-tests-',dir=temporary_root)
        if not Path(self.directory.name).resolve().is_relative_to(temporary_root.resolve()):
            raise ValueError('Test cleanup must remain inside the workspace preview directory')
        self.addCleanup(self.directory.cleanup)
        self.profile = Path(self.directory.name) / "profile"
        self.profile.mkdir()
        self.person = {"name":"Editorial name", "role":"Developer / Owner", "secondary_role":"Owner de Master IT Support", "slug":"oscar", "discord_id":USER_ID, "avatar":"team/oscar.png"}
        (self.profile / "profile.json").write_text(json.dumps({"developers":[self.person]},indent=2)+"\n",encoding="utf-8")

    def result(self, username="oscar_dev", banner=False, global_name="OscarDev"):
        user = {"id":USER_ID,"username":username,"global_name":global_name}
        return user, AVATAR_URL, PNG, BANNER_URL if banner else None, PNG if banner else None

    def run_sync(self, day, result):
        with patch.object(syncer, "lookup", return_value=result), redirect_stdout(io.StringIO()):
            return syncer.sync(day,self.profile)

    def files(self):
        return {p.relative_to(self.profile).as_posix():p.read_bytes() for p in self.profile.rglob('*') if p.is_file()}

    def test_updates_public_identity_banner_and_keeps_editorial_roles(self):
        self.assertTrue(self.run_sync("2026-10-12",self.result(banner=True)))
        person=json.loads((self.profile/'profile.json').read_text())['developers'][0]
        self.assertEqual(person['name'],'Editorial name')
        self.assertEqual(person['role'],'Developer / Owner')
        self.assertEqual(person['secondary_role'],'Owner de Master IT Support')
        self.assertEqual(person['discord_display_name'],'OscarDev')
        self.assertEqual((self.profile/'assets/team/oscar-banner.png').read_bytes(),PNG)

    def test_unchanged_profile_next_day_does_not_produce_a_commit(self):
        self.run_sync("2026-10-12",self.result())
        before=self.files()
        self.assertFalse(self.run_sync("2026-10-13",self.result()))
        self.assertEqual(before,self.files())

    def test_later_lookup_failure_preserves_every_previous_file(self):
        config=json.loads((self.profile/'profile.json').read_text())
        config['developers'].append({**self.person,'name':'Second','slug':'second','discord_id':'193858356052623360','avatar':'team/second.png'})
        (self.profile/'profile.json').write_text(json.dumps(config))
        self.run_sync("2026-10-12",self.result())
        before=self.files()
        with patch.object(syncer,'lookup',side_effect=[self.result(username='changed'),ValueError('Service failed')]):
            with self.assertRaises(ValueError):
                syncer.sync("2026-10-13",self.profile)
        self.assertEqual(before,self.files())

    def test_removed_banner_restores_the_neutral_background(self):
        self.run_sync("2026-10-12",self.result(banner=True))
        self.assertTrue(self.run_sync("2026-10-13",self.result(banner=False)))
        self.assertFalse((self.profile/'assets/team/oscar-banner.png').exists())
        person=json.loads((self.profile/'profile.json').read_text())['developers'][0]
        self.assertIsNone(person['discord_banner'])

    def test_global_name_falls_back_to_username(self):
        self.run_sync("2026-10-12",self.result(global_name=None))
        person=json.loads((self.profile/'profile.json').read_text())['developers'][0]
        self.assertEqual(person['discord_display_name'],'oscar_dev')

    def test_lookup_rejects_wrong_user_and_non_discord_avatar(self):
        for user_id,avatar_url in [('193858356052623360',AVATAR_URL),(USER_ID,'https://example.com/avatar.png')]:
            payload={'user':{'id':user_id,'username':'oscar_dev','global_name':'OscarDev'},'avatar':{'png':{'256':avatar_url}}}
            with patch.object(syncer,'download',return_value=json.dumps(payload).encode()) as fetch:
                with self.assertRaises(ValueError):
                    syncer.lookup(self.person)
                self.assertEqual(fetch.call_count,1)

    def test_invalid_banner_and_truncated_png_are_rejected(self):
        payload={'user':{'id':USER_ID,'username':'oscar_dev','banner':'../../bad'},'avatar':{'png':{'256':AVATAR_URL}}}
        with patch.object(syncer,'download',side_effect=[json.dumps(payload).encode(),PNG]):
            with self.assertRaises(ValueError):
                syncer.lookup(self.person)
        with self.assertRaises(ValueError):
            syncer.check_png(PNG[:-8])


if __name__ == '__main__':
    unittest.main()
