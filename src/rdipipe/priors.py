from bilby.core.prior.dict import PriorDict
from itertools import product
import numpy as np

from typing import List, Dict, Union

class CompositePriorDict(PriorDict):
    """A class which combines deterministic (grid) draws of parameters with stochastic sampling from a prior.
    For use constructing injections sets, not appropriate for use in a stochastic sampler."""
    def __init__(self, grid : Union[Dict[str, List], None] = None, dictionary=None, filename=None, conversion_function=None):
        """Construct the stochastic prior with added parameters sampled over a grid

        Parameters
        ==========
        grid : Dict[str, List] 
        """
        super(CompositePriorDict, self).__init__(dictionary, filename, conversion_function)
        if grid is not None:
            self.grid = list(product(*grid.values()))
            self.grid_names = grid.keys()
            self.gridsize = len(self.grid)

    def sample(self, size : int) -> dict:
        """Sample from the stochastic joint prior, and also from the grid.
        This is written in a stupid and slow way, but you should only be running this once anyways
        so it doesn't really matter.
        
        """
        stochastic_samples = super(CompositePriorDict, self).sample(size)
        assert size % self.gridsize == 0
        # The grid should evenly divide the requested number of samples
        # This is the stupidest way to go about this, but whatever
        for ii, name in enumerate(self.grid_names):
            grid_samples = np.zeros((size,))
            for jj in range(int(size / self.gridsize)):
                for kk, point in enumerate(self.grid):
                    grid_samples[jj * self.gridsize  + kk] = point[ii]
            stochastic_samples[name] = grid_samples
        return stochastic_samples