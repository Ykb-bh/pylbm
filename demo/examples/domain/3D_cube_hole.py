# Authors:
#     Loic Gouarin <loic.gouarin@math.u-psud.fr>
#     Benjamin Graille <benjamin.graille@math.u-psud.fr>
#
# License: BSD 3 clause

"""
Example of the cube in 3D
"""
import pyLBM
dico = {
    'box':{'x': [0, 2], 'y': [0, 2], 'z':[0, 2], 'label':range(1,7)},
    'elements':[pyLBM.Sphere((0.5,0.5,0.5), 0.2, label = 0)],
    'space_step':0.25,
    'schemes':[{'velocities':range(19)}]
}
dom = pyLBM.Domain(dico)
print dom
dom.visualize(view_distance=True)
