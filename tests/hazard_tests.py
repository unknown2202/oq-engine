# -*- coding: utf-8 -*-

import json
import logging
import time
import unittest

from opengem import hazard
from opengem import kvs
from opengem.hazard import tasks
from tests.jobber_unittest import wait_for_celery_tasks
from tests.memcached_unittest import ONE_CURVE_MODEL

MEAN_GROUND_INTENSITY='{"site":"+35.0000 +35.0000", "intensity": 1.9249e+00, \
                        "site":"+35.0500 +35.0000", "intensity": 1.9623e+00, \
                        "site":"+35.1000 +35.0000", "intensity": 2.0320e+00, \
                        "site":"+35.1500 +35.0000", "intensity": 2.0594e+00}'

TASK_JOBID_SIMPLE = ["JOB1", "JOB2", "JOB3", "JOB4"]


class HazardEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.memcache_client = kvs.get_client(binary=False)
        self.memcache_client.flush_all()

    def tearDown(self):
        pass

    def test_basic_generate_erf_keeps_order(self):
        results = []
        for job_id in TASK_JOBID_SIMPLE:
            results.append(tasks.generate_erf.delay(job_id))

        self.assertEqual(TASK_JOBID_SIMPLE,
                         [result.get() for result in results])

    def test_generate_erf_returns_erf_via_memcached(self):
        results = []
        result_keys = []
        expected_values = {}

        for job_id in TASK_JOBID_SIMPLE:
            erf_key = kvs.generate_product_key(job_id, hazard.ERF_KEY_TOKEN)

            # Build the expected values
            expected_values[erf_key] = json.JSONEncoder().encode([job_id])

            # Get our result keys
            result_keys.append(erf_key)

            # Spawn our tasks.
            results.append(tasks.generate_erf.apply_async(args=[job_id]))

        wait_for_celery_tasks(results)

        result_values = self.memcache_client.get_multi(result_keys)

        self.assertEqual(result_values, expected_values)

    def test_compute_hazard_curve_all_sites(self):
        results = []
        block_id = 8801
        for job_id in TASK_JOBID_SIMPLE:
            self._prepopulate_sites_for_block(job_id, block_id)
            results.append(tasks.compute_hazard_curve.apply_async(
                args=[job_id, block_id]))

        wait_for_celery_tasks(results)

        for result in results:
            for res in result.get():
                self.assertEqual(res, ONE_CURVE_MODEL)

    def test_compute_mgm_intensity(self):
        results = []
        block_id = 8801
        site = "Testville,TestLand"
    
        mgm_intensity = json.JSONDecoder().decode(MEAN_GROUND_INTENSITY)

        for job_id in TASK_JOBID_SIMPLE:
            mgm_key = kvs.generate_product_key(job_id, hazard.MGM_KEY_TOKEN, 
                block_id, site)
            self.memcache_client.set(mgm_key, MEAN_GROUND_INTENSITY)

            results.append(tasks.compute_mgm_intensity.apply_async(
                args=[job_id, block_id, site]))

        wait_for_celery_tasks(results)

        for result in results:
            self.assertEqual(mgm_intensity, result.get())

    def _prepopulate_sites_for_block(self, job_id, block_id):
        sites = ["Testville,TestLand", "Provaville,TestdiTerra",
                 "Teststadt,Landtesten", "villed'essai,paystest"]
        sites_key = kvs.generate_sites_key(job_id, block_id)

        self.memcache_client.set(sites_key, json.JSONEncoder().encode(sites))

        for site in sites:
            site_key = kvs.generate_product_key(job_id,
                hazard.HAZARD_CURVE_KEY_TOKEN, block_id, site) 

            self.memcache_client.set(site_key, ONE_CURVE_MODEL)
