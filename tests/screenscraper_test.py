#!/usr/bin/python -B
# -*- coding: utf-8 -*-
#
# Test AKL ScreenScraper asset scraper.
# This testing file is intended for scraper development and file dumping.
#

# --- Python standard library ---
from __future__ import unicode_literals
import os
import unittest
import unittest.mock
from unittest.mock import patch, MagicMock
import logging

logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG)
logger = logging.getLogger(__name__)

from resources.lib.scraper import ScreenScraper
from akl.utils import kodi, io
from akl.api import ROMObj
from akl import constants

# --- Test data -----------------------------------------------------------------------------------
games = {
    # Console games
    'metroid'                : ('Metroid', 'Metroid.zip', 'Nintendo SNES'),
    'mworld'                 : ('Super Mario World', 'Super Mario World.zip', 'Nintendo SNES'),
    'sonic_megaDrive'        : ('Sonic the Hedgehog', 'Sonic the Hedgehog (USA, Europe).zip', 'Sega Mega Drive'),
    'sonic_genesis'          : ('Sonic the Hedgehog', 'Sonic the Hedgehog (USA, Europe).zip', 'Sega Genesis'),
    'chakan'                 : ('Chakan', 'Chakan (USA, Europe).zip', 'Sega MegaDrive'),
    'ff7'                    : ('Final Fantasy VII', 'Final Fantasy VII (USA) (Disc 1).iso', 'Sony PlayStation'),
    'console_wrong_title'    : ('Console invalid game', 'mjhyewqr.zip', 'Sega MegaDrive'),
    'console_wrong_platform' : ('Sonic the Hedgehog', 'Sonic the Hedgehog (USA, Europe).zip', 'mjhyewqr'),

    # MAME games
    'atetris'             : ('Tetris (set 1)', 'atetris.zip', 'MAME'),
    'mslug'               : ('Metal Slug - Super Vehicle-001', 'mslug.zip', 'MAME'),
    'dino'                : ('Cadillacs and Dinosaurs (World 930201)', 'dino.zip', 'MAME'),
    'MAME_wrong_title'    : ('MAME invalid game', 'mjhyewqr.zip', 'MAME'),
    'MAME_wrong_platform' : ('Tetris (set 1)', 'atetris.zip', 'mjhyewqr'),
}


# --- ScreenScraper ---
scraper_screenscraper_ssid = os.getenv('SCREENSCRAPER_SSID')
scraper_screenscraper_sspass = os.getenv('SCREENSCRAPER_PASS')
scraper_screenscraper_AKL_softname = 'AKL_0.9.8'
scraper_screenscraper_region = 0 # Default World
scraper_screenscraper_language = 0 # Default English

def get_setting(key:str):
    if key == 'scraper_cache_dir': return Test_screenscraper.TEST_OUTPUT_DIR
    if key == 'scraper_screenscraper_sspass': return scraper_screenscraper_sspass 
    if key == 'scraper_screenscraper_ssid': return scraper_screenscraper_ssid 
    if key == 'scraper_screenscraper_AKL_softname': return scraper_screenscraper_AKL_softname 
    return ''

def get_setting_int(key:str):
    if key == 'scraper_screenscraper_region': return scraper_screenscraper_region
    if key == 'scraper_screenscraper_language': return scraper_screenscraper_language 
    return 0
class Test_screenscraper(unittest.TestCase):
    
    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_ASSETS_DIR = ''
    TEST_OUTPUT_DIR = ''
    
    @classmethod
    def setUpClass(cls):        
        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))
        cls.TEST_OUTPUT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'output/'))
                
        print('ROOT DIR: {}'.format(cls.ROOT_DIR))
        print('TEST DIR: {}'.format(cls.TEST_DIR))
        print('TEST ASSETS DIR: {}'.format(cls.TEST_ASSETS_DIR))
        print('TEST OUTPUT DIR: {}'.format(cls.TEST_OUTPUT_DIR))
        print('---------------------------------------------------------------------------')
        
        if not os.path.exists(cls.TEST_OUTPUT_DIR):
            os.makedirs(cls.TEST_OUTPUT_DIR)
    
    @unittest.skip('You must have an account key to use this test')
    @patch('resources.lib.scraper.settings.getSettingAsInt', autospec=True, side_effect=get_setting_int)
    @patch('resources.lib.scraper.settings.getSetting', autospec=True, side_effect=get_setting)
    def test_screenscraper_metadata(self, settings_mock, settingsint_mock): 
        
        # --- main ---------------------------------------------------------------------------------------
        print('*** Fetching candidate game list ********************************************************')
        # --- Create scraper object ---
        scraper_obj = ScreenScraper()
        scraper_obj.set_verbose_mode(False)
        scraper_obj.set_debug_file_dump(True, self.TEST_OUTPUT_DIR)
        scraper_obj.set_debug_checksums(True,
            '414FA339', '9db5682a4d778ca2cb79580bdb67083f',
            '48c98f7e5a6e736d790ab740dfc3f51a61abe2b5', 123456)
        status_dic = kodi.new_status_dic('Scraper test was OK')

        # --- Choose data for testing ---
        # search_term, rombase, platform = common.games['metroid']
        # search_term, rombase, platform = common.games['mworld']
        #search_term, rombase, platform = common.games['sonic_megaDrive']
        search_term, rombase, platform = games['sonic_genesis'] # Aliased platform
        # search_term, rombase, platform = common.games['chakan']
        # search_term, rombase, platform = common.games['console_wrong_title']
        # search_term, rombase, platform = common.games['console_wrong_platform']

        # --- Debug call to test API function jeuRecherche.php ---
        # scraper_obj.debug_game_search(*common.games['ff7'], status_dic = status_dic)

        # --- Get candidates, print them and set first candidate ---
        rom_FN = io.FileName(rombase)
        rom = ROMObj({
            'platform': platform,
            'scanned_data': { 'file': rombase, 'identifier': rom_FN.getBaseNoExt() }
        })
            
        if scraper_obj.check_candidates_cache(rom.get_identifier(), platform):
            print('>>>> Game "{}" "{}" in disk cache.'.format(rom.get_identifier(), platform))
        else:
            print('>>>> Game "{}" "{}" not in disk cache.'.format(rom.get_identifier(), platform))
        candidate_list = scraper_obj.get_candidates(search_term, rom, platform, status_dic)
        # pprint.pprint(candidate_list)
        self.assertTrue(status_dic['status'], 'Status error "{}"'.format(status_dic['msg']))
        self.assertIsNotNone(candidate_list, 'Error/exception in get_candidates()')
        self.assertNotEquals(len(candidate_list), 0, 'No candidates found.')
        
        for candidate in candidate_list:
            print(candidate)
            
        scraper_obj.set_candidate(rom.get_identifier(), platform, candidate_list[0])

        # --- Print metadata of first candidate ----------------------------------------------------------
        print('*** Fetching game metadata **************************************************************')
        metadata = scraper_obj.get_metadata(status_dic)
        # pprint.pprint(metadata)
        print(metadata)
        scraper_obj.flush_disk_cache()

    @unittest.skip('You must have an account key to use this test')
    @patch('resources.lib.scraper.settings.getSettingAsInt', autospec=True, side_effect=get_setting_int)
    @patch('resources.lib.scraper.settings.getSetting', autospec=True, side_effect=get_setting)
    def test_screenscraper_assets(self, settings_mock, settingsint_mock): 
        
        if not os.path.exists(self.TEST_OUTPUT_DIR):
            os.makedirs(self.TEST_OUTPUT_DIR)
        
        # --- main ---------------------------------------------------------------------------------------
        print('*** Fetching candidate game list ********************************************************')
        
        # --- Create scraper object ---
        scraper_obj = ScreenScraper()
        scraper_obj.set_verbose_mode(False)
        scraper_obj.set_debug_file_dump(True, self.TEST_OUTPUT_DIR)
        scraper_obj.set_debug_checksums(True, '414FA339', '9db5682a4d778ca2cb79580bdb67083f',
            '48c98f7e5a6e736d790ab740dfc3f51a61abe2b5', 123456)
        status_dic = kodi.new_status_dic('Scraper test was OK')

        # --- Choose data for testing ---
        # search_term, rombase, platform = common.games['metroid']
        # search_term, rombase, platform = common.games['mworld']
        #search_term, rombase, platform = common.games['sonic_megaDrive']
        search_term, rombase, platform = games['sonic_genesis'] # Aliased platform
        # search_term, rombase, platform = common.games['chakan']
        # search_term, rombase, platform = common.games['console_wrong_title']
        # search_term, rombase, platform = common.games['console_wrong_platform']

        # --- Get candidates, print them and set first candidate ---
        rom_FN = io.FileName(rombase)
        rom = ROMObj({
            'platform': platform,
            'scanned_data': { 'file': rombase, 'identifier': rom_FN.getBaseNoExt() }
        })
        
        if scraper_obj.check_candidates_cache(rom.get_identifier(), platform):
            print('>>>> Game "{}" "{}" in disk cache.'.format(rom.get_identifier(), platform))
        else:
            print('>>>> Game "{}" "{}" not in disk cache.'.format(rom.get_identifier(), platform))
        candidate_list = scraper_obj.get_candidates(search_term, rom, platform, status_dic)
        # pprint.pprint(candidate_list)
        self.assertTrue(status_dic['status'], 'Status error "{}"'.format(status_dic['msg']))
        self.assertIsNotNone(candidate_list, 'Error/exception in get_candidates()')
        self.assertNotEquals(len(candidate_list), 0, 'No candidates found.')
        
        for candidate in candidate_list:
            print(candidate)
            
        scraper_obj.set_candidate(rom.get_identifier(), platform, candidate_list[0])

        # --- Print list of assets found -----------------------------------------------------------------
        print('*** Fetching game assets ****************************************************************')
        # --- Get specific assets ---
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_FANART_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_BANNER_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_CLEARLOGO_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_TITLE_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_SNAP_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_BOXFRONT_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_BOXBACK_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_3DBOX_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_CARTRIDGE_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_MAP_ID, status_dic))
        scraper_obj.flush_disk_cache()

    def print_game_assets(self, assets):
        for asset in assets:
            print(asset)