from unittest import TestCase, skip

import db
import test.dummy_data as dd
import random

class TestPersistentGanbot(TestCase):

    def setUp(self):
        print("test")
        self.pers = db.openTestPeristent()

    def test_storeCharacter(self):

        for char in [dd.mysta,dd.danny,dd.dareko,dd.jonus]:

            self.pers.storeCharacter(db.Character(**char))

            restored = self.pers.fetch_character_by_name(char['name'])

            self.assertEquals(char['name'], restored.name)
            self.assertEquals(char['attack'], restored.attack)
            self.assertEquals(char['defence'], restored.defence)
            self.assertEquals(char['speed'], restored.speed)
            self.assertEquals(char['magic'], restored.magic)
            self.assertEquals(char['health'], restored.health)

    def test_fetch_characters_for_user(self):
        for char in dd.allChars:
            self.pers.storeCharacter(db.Character(**char))

        chars = self.pers.fetch_characters_for_user(dd.user_alice.id)

        self.assertEquals(set(c.name for c in chars),
                          set(char['name'] for char in dd.allChars if char['player'] == dd.user_alice.id))

    def test_fetch_character_by_name(self):
        for char in dd.allChars:
            self.pers.storeCharacter(db.Character(**char))

        for char in dd.allChars:
            c = self.pers.fetch_character_by_name(char['name'])
            self.assertEquals(c.name, char['name'])

        self.assertIsNone(self.pers.fetch_character_by_name('Mosta'))

    def test_fetch_all_characters_by_name_like(self):
        for char in dd.allChars:
            self.pers.storeCharacter(db.Character(**char))

        self.assertEqual(set(c['name'] for c in [dd.mysta, dd.maasta]),
                         set(c.name for c in self.pers.fetch_all_characters_by_name_like('M%sta')))

    def test_search_character(self):

        for char in dd.allChars:
            self.pers.storeCharacter(db.Character(**char))

        self.assertEqual(set(c['name'] for c in [dd.mysta, dd.maasta]),
                         set(c.name for c in (self.pers.search_character('nasta')[:2])))

    @skip("Battles not quite implemented yet.")
    def test_storeBattle(self):
        self.fail()
