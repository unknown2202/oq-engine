# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2014-2019 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

import numpy
from openquake.hazardlib.geo.mesh import Mesh
from openquake.hazardlib.contexts import DistancesContext
from openquake.hazardlib.tests.gsim.mgmpe.dummy import Dummy

from openquake.hazardlib.gsim.abrahamson_2014 import (
    AbrahamsonEtAl2014, AbrahamsonEtAl2014RegTWN, AbrahamsonEtAl2014RegCHN,
    AbrahamsonEtAl2014RegJPN, AbrahamsonEtAl2014NonErgodic)
from openquake.hazardlib.tests.gsim.utils import BaseGSIMTestCase

# Test data have been generated from the Matlab implementation available as
# Annex 1 of Abrahamson et al. (2014)


class Abrahamson2014EtAlTestCase(BaseGSIMTestCase):
    """
    Test the default model, the total standard deviation and the within-event
    standard deviation. The between events std is implicitly tested
    """

    GSIM_CLASS = AbrahamsonEtAl2014

    def test_mean(self):
        self.check('ASK14/ASK14_ResMEAN_RegCAL.csv',
                   max_discrep_percentage=0.1)

    def test_std_total(self):
        self.check('ASK14/ASK14_ResStdTot_RegCAL.csv',
                   max_discrep_percentage=0.1)

    def test_std_intra(self):
        self.check('ASK14/ASK14_ResStdPhi_RegCAL.csv',
                   max_discrep_percentage=0.1)


class Abrahamson2014EtAlRegTWNTestCase(BaseGSIMTestCase):
    """
    Test the modified version of the base model. Regional model for Taiwan.
    Standard deviation model is not tested since it's the same used for the
    default model.
    """

    GSIM_CLASS = AbrahamsonEtAl2014RegTWN

    def test_mean(self):
        self.check('ASK14/ASK14_ResMEAN_RegTWN.csv',
                   max_discrep_percentage=0.3)


class Abrahamson2014EtAlRegCHNTestCase(BaseGSIMTestCase):
    """
    Test the modified version of the base model. Regional model for China.
    Standard deviation model is not tested since it's the same used for the
    default model.
    """

    GSIM_CLASS = AbrahamsonEtAl2014RegCHN

    def test_mean(self):
        self.check('ASK14/ASK14_ResMEAN_RegCHN.csv',
                   max_discrep_percentage=0.1)


class Abrahamson2014EtAlRegJPNTestCase(BaseGSIMTestCase):
    """
    Test the modified version of the base model. Regional model for Japan
    Standard deviation model is not tested since it's the same used for the
    default model.
    """
    GSIM_CLASS = AbrahamsonEtAl2014RegJPN

    def test_mean(self):
        self.check('ASK14/ASK14_ResMEAN_RegJPN.csv',
                   max_discrep_percentage=0.1)

    def test_std_total(self):
        self.check('ASK14/ASK14_ResStdTot_RegJPN.csv',
                   max_discrep_percentage=0.1)

    def test_std_intra(self):
        self.check('ASK14/ASK14_ResStdPhi_RegJPN.csv',
                   max_discrep_percentage=0.1)


class Abrahamson2014EtAlNonErgodicTestCase(BaseGSIMTestCase):
    """
    Test the default model, the total standard deviation and the within-event
    standard deviation. The between events std is implicitly tested
    """

    GSIM_CLASS = AbrahamsonEtAl2014NonErgodic

    #def test_mean(self):
    #    self.check('ASK14/ASK14_ResMEAN_RegCAL.csv',
    #               max_discrep_percentage=0.1)

    def test(self):
        # Input parameters
        mag = 6.0
        hyp_lon = -121.3
        hyp_lat = 37.9
        # 
        dummy = Dummy()
        surface, hypo = dummy.get_surface(hyp_lon, hyp_lat, mag=mag, 
                                          asp_ratio=2.0)
        lons = numpy.array([-121.2, -121.3])
        lats = numpy.array([37.9, 38.2])
        mesh = Mesh(lons, lats)
        rup = Dummy.get_rupture(mag=6.0)
        dists = DistancesContext()
        dists.rrup = surface.get_min_distance(mesh)
        dists.rjb = surface.get_joyner_boore_distance(mesh)
        dists.ry0 = surface.get_ry0_distance(mesh)
        dists.rx = surface.get_rx_distance(mesh)
        dists.azimuth = surface.
        
        pnts = surface.get_closest_points(mesh)
