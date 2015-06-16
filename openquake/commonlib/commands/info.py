#  -*- coding: utf-8 -*-
#  vim: tabstop=4 shiftwidth=4 softtabstop=4

#  Copyright (c) 2014, GEM Foundation

#  OpenQuake is free software: you can redistribute it and/or modify it
#  under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  OpenQuake is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with OpenQuake.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import textwrap
from openquake.baselib.performance import Monitor
from openquake.baselib.general import humansize
from openquake.commonlib import sap, readinput, nrml, source
from openquake.commonlib.calculators import base
from openquake.hazardlib import gsim


# the documentation about how to use this feature can be found
# in the file effective-realizations.rst
def _info(name, filtersources, weightsources):
    if name in base.calculators:
        print(textwrap.dedent(base.calculators[name].__doc__.strip()))
    elif name == 'gsims':
        for gs in gsim.get_available_gsims():
            print(gs)
    elif name.endswith('.xml'):
        print(nrml.read(name).to_str())
    elif name.endswith(('.ini', '.zip')):
        oqparam = readinput.get_oqparam(name)
        if 'exposure' in oqparam.inputs:
            expo = readinput.get_exposure(oqparam)
            sitecol, assets_by_site = readinput.get_sitecol_assets(
                oqparam, expo)
        elif filtersources or weightsources:
            sitecol, assets_by_site = readinput.get_site_collection(
                oqparam), []
        else:
            sitecol, assets_by_site = None, []
        if 'source_model_logic_tree' in oqparam.inputs:
            print('Reading the source model...')
            if weightsources:
                sp = source.SourceFilterWeighter
            elif filtersources:
                sp = source.SourceFilter
            else:
                sp = source.BaseSourceProcessor  # do nothing
            csm = readinput.get_composite_source_model(oqparam, sitecol, sp)
            assoc = csm.get_rlzs_assoc()
            print(assoc.csm_info)
            print('See https://github.com/gem/oq-risklib/blob/master/docs/'
                  'effective-realizations.rst for an explanation')
            print(assoc)
            if filtersources or weightsources:
                info = readinput.get_job_info(oqparam, csm, sitecol)
                info['n_sources'] = csm.get_num_sources()
                info['c_matrix'] = humansize(
                    info['n_sites'] * info['n_levels'] *
                    info['n_imts'] * len(assoc) * 8)
                for k in sorted(info):
                    print(k, info[k])
        if len(assets_by_site):
            print('assets = %d' %
                  sum(len(assets) for assets in assets_by_site))
    else:
        print("No info for '%s'" % name)


def info(name, filtersources=False, weightsources=False):
    """
    Give information. You can pass the name of an available calculator,
    a job.ini file, or a zip archive with the input files.
    """
    with Monitor('info', measuremem=True) as mon:
        _info(name, filtersources, weightsources)
    if mon.duration > 1:
        print(mon)


parser = sap.Parser(info)
parser.arg('name', 'calculator name, job.ini file or zip archive')
parser.flg('filtersources', 'flag to enable filtering of the source models')
parser.flg('weightsources', 'flag to enable weighting of the source models')
