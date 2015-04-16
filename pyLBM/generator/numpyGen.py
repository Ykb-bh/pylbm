# Authors:
#     Loic Gouarin <loic.gouarin@math.u-psud.fr>
#     Benjamin Graille <benjamin.graille@math.u-psud.fr>
#
# License: BSD 3 clause
import sympy as sp
import re

from .base import Generator
from .utils import matMult, load_or_store

class NumpyGenerator(Generator):
    """
    the default generator of code,
    subclass of :py:class:`Generator<pyLBM.generator.Generator>`

    Parameters
    ----------

    build_dir : string, optional
      the directory where the code has to be written

    Notes
    -----

    This generator can always be used but is not the most efficient.

    Attributes
    ----------

    build_dir : string
      the directory where the code is written
    f : file identifier
      the file where the code is written
    code : string
      the generated code

    Methods
    -------

    transport :
      generate the code of the transport phase
    relaxation :
      generate the code of the relaxation phase
    equilibrium :
      generate the code of the equilibrium
    m2f :
      generate the code to compute the distribution functions
      from the moments
    f2m :
      generate the code to compute the moments
      from the distribution functions
    """
    def __init__(self, build_dir=None):
        Generator.__init__(self, build_dir)

    def transport(self, ns, stencil, dtype = 'f8'):
        """
        generate the code of the transport phase

        Parameters
        ----------

        ns : int
          the number of elementary schemes
        stencil : :py:class:`Stencil<pyLBM.stencil.Stencil>`
          the stencil of velocities
        dtype : string, optional
          the type of the data (default 'f8')

        Returns
        -------

        code : string
          add the transport phase in the attribute ``code``.
        """
        self.code += "def transport(f):\n"
        v = stencil.get_all_velocities()
        self.code += load_or_store('f', 'f', -v, v, indent='\t')
        self.code += "\n"

    def equilibrium(self, ns, stencil, eq, la, dtype = 'f8'):
        """
        generate the code of the projection on the equilibrium

        Parameters
        ----------

        ns : int
          the number of elementary schemes
        stencil : :py:class:`Stencil<pyLBM.stencil.Stencil>`
          the stencil of velocities
        eq : sympy matrix
          the equilibrium (formally given)
        la : double
          the value of the scheme velocity (dx/dt)
        dtype : string, optional
          the type of the data (default 'f8')

        Returns
        -------

        code : string
          add the equilibrium function in the attribute ``code``.
        """
        self.code += "def equilibrium(m):\n"

        def sub(g):
            i = int(g.group('i'))
            j = int(g.group('j'))

            return '[' + str(stencil.nv_ptr[i] + j) + ']'

        for k in xrange(ns):
            for i in xrange(stencil.nv[k]):
                if str(eq[k][i]) != "m[%d][%d]"%(k,i):
                    if eq[k][i] != 0:
                        res = re.sub("\[(?P<i>\d)\]\[(?P<j>\d)\]", sub,
                                   str(eq[k][i].subs([(sp.symbols('LA'), la),])))
                        self.code += "\tm[%d] = %s\n"%(stencil.nv_ptr[k] + i, res)
                    else:
                        self.code += "\tm[%d] = 0.\n"%(stencil.nv_ptr[k] + i)
        self.code += "\n"

    def relaxation(self, ns, stencil, s, eq, la, dtype = 'f8'):
        """
        generate the code of the relaxation phase

        Parameters
        ----------

        ns : int
          the number of elementary schemes
        stencil : :py:class:`Stencil<pyLBM.stencil.Stencil>`
          the stencil of velocities
        s : list of list of double
          the values of the relaxation parameters
        eq : sympy matrix
          the equilibrium (formally given)
        la : double
          the value of the scheme velocity (dx/dt)
        dtype : string, optional
          the type of the data (default 'f8')

        Returns
        -------

        code : string
          add the relaxation phase in the attribute ``code``.
        """
        self.code += "def relaxation(m):\n"

        def sub(g):
            i = int(g.group('i'))
            j = int(g.group('j'))

            return '[' + str(stencil.nv_ptr[i] + j) + ']'

        for k in xrange(ns):
            for i in xrange(stencil.nv[k]):
                if str(eq[k][i]) != "m[%d][%d]"%(k,i):
                    if eq[k][i] != 0:
                        res = re.sub("\[(?P<i>\d)\]\[(?P<j>\d)\]", sub,
                                   str(eq[k][i].subs([(sp.symbols('LA'), la),])))
                        self.code += "\tm[{0:d}] += {1:.16f}*({2} - m[{0:d}])\n".format(stencil.nv_ptr[k] + i, s[k][i], res)
                    else:
                        self.code += "\tm[{0:d}] *= (1. - {1:.16f})\n".format(stencil.nv_ptr[k] + i, s[k][i])
        self.code += "\n"

    def m2f(self, A, k, dim, dtype = 'f8'):
        """
        generate the code to compute the distribution functions from the moments

        Parameters
        ----------

        A : numpy array
          the matrix M^(-1) in the d'Humieres framework
        k : int
          the number of the stencil for which the code has to be generated
        dim : int
          the space dimension (unused)
        dtype : string, optional
          the type of the data (default 'f8')

        Returns
        -------

        code : string
          add the m2f function in the attribute ``code``.

        Notes
        -----

        For the NumpyGenerator, it seems to be more efficient
        to generate one function per elementary scheme
        because the index corresponding to the stencil is the first index.
        """
        self.code += "def m2f_{0:d}(m, f):\n".format(k)
        self.code += matMult(A, 'm', 'f', '\t')
        self.code += "\n"

    def f2m(self, A, k, dim, dtype = 'f8'):
        """
        generate the code to compute the moments from the distribution functions

        Parameters
        ----------

        A : numpy array
          the matrix M in the d'Humieres framework
        k : int
          the number of the stencil for which the code has to be generated
        dim : int
          the space dimension (unused)
        dtype : string, optional
          the type of the data (default 'f8')

        Returns
        -------

        code : string
          add the f2m function in the attribute ``code``.

        Notes
        -----

        For the NumpyGenerator, it seems to be more efficient
        to generate one function per elementary scheme
        because the index corresponding to the stencil is the first index.
        """
        self.code += "def f2m_{0:d}(f, m):\n".format(k)
        self.code += matMult(A, 'f', 'm', '\t')
        self.code += "\n"
