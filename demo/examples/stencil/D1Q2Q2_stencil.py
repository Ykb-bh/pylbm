# Authors:
#     Loic Gouarin <loic.gouarin@math.u-psud.fr>
#     Benjamin Graille <benjamin.graille@math.u-psud.fr>
#
# License: BSD 3 clause

"""
Example of a vectorial 2 velocities scheme in 1D
"""
import pyLBM
from pyLBM.viewer import MatplotlibViewer
dsten = {
    'dim':1,
    'schemes':[
        {'velocities':range(1,3)},
        {'velocities':range(1,3)},
    ],
}
s = pyLBM.Stencil(dsten)
print s
v = MatplotlibViewer()
s.visualize(v)
