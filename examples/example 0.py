
from bw2link2tespy import bw_link_2_tespy as bw2t

import bw2data as bd

from tespy.components import  Pump
from tespy.connections import Connection, PowerConnection
from tespy.tools.characteristics import CharLine
import numpy as np
# Tespy Model setup:
nw = bw2t.Network(p_unit='bar', T_unit='C', h_unit='kJ / kg', v_unit='l / s',
iterinfo=False)
si = bw2t.Sink('sink')
so = bw2t.Source('source')
pu = Pump('pump')
inc = Connection(so, 'out1', pu, 'in1')
outg = Connection(pu, 'out1', si, 'in1')
nw.add_conns(inc, outg)
v = np.array([0, 0.4, 0.8, 1.2, 1.6, 2]) / 1000
dp = np.array([15, 14, 12, 9, 5, 0]) * 1e5
char = CharLine(x=v, y=dp)
pu.set_attr(eta_s=0.8, flow_char={'char_func': char, 'is_set': True},
design=['eta_s'], offdesign=['eta_s_char'])
inc.set_attr(fluid={'water': 1}, p=1, T=20, v=1.5, design=['v'])

pump_power = bw2t.PowerSource('pump power')
e_p = PowerConnection(pump_power, 'power', pu, 'power')

nw.add_conns(e_p)
nw.solve('design')

#link brightway25 datasets:
bd.projects.set_current('bw_meets_tespy')
ei=bd.Database('ecoinvent-3.11-cutoff')
ei_steam=[act for act in ei if 'steam production, as energy carrier, in chemical industry' in act['name']
    and 'RER' in act['location']][0]
ei_electricity=[act for act in ei if 'market for electricity, medium' in act['name']
    and 'DE' in act['location']
    ][0]

impact_category=[meth for meth in bd.methods if 'EF v3.1' in meth[1] 
 and 'climate change' in meth[2]
 and 'no LT' not in meth[1]]

pump_power.link_bw(ei_electricity)
so.link_bw(ei_steam)

functional_unit={'pumped_steam':{'component':si,
                                 'allocationfactor':1,
                                 'direction':1}}

nw.set_functional_unit(functional_unit)
nw.calc_background_impact(impact_category)

nw.get_lca_results()