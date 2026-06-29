"""
Defines the Gaussian canonical form container with (eta, Lam)
This helps define most of the methods from messages, beliefs,
priors, and factor potentials.

Methods:
- Canonical add/subtract
- Marginalisation (the Schur complement)
- Damping
- Transform to moment form
"""

import numpy as np
from numpy.typing import NDArray

class Gaussian:
    def __init__(
            self, 
            dim:int,
            eta: NDArray[np.float64] | None = None,
            Lam: NDArray[np.float64] | None = None
        ) -> None:

        self.dim = dim

        if eta is None:
            self.eta = np.zeros(self.dim)
        elif len(eta) == self.dim:
            self.eta = eta
        else:
            raise ValueError(f"eta has length: ({len(eta)}), expected: ({self.dim})")

        if Lam is None: # Defaults to uninformative Gaussian
            self.Lam = np.zeros((self.dim, self.dim))
        elif Lam.shape == (self.dim, self.dim):
            self.Lam = Lam
        else:
            raise ValueError(f"Lam has shape: ({Lam.shape}), expected: ({self.dim}, {self.dim}).")
    
    def __add__(self, other):
        """
        Dunder method for doing the canonical sum of two Gaussian
        distributions.
        """
        if self.dim == other.dim:
            return Gaussian(self.dim, self.eta + other.eta, self.Lam + other.Lam)
        else:
            raise ValueError("Dimensionality of Gaussians do not match.")

    def __sub__(self, other):
        """
        Same method as above just subtraction.
        """
        if self.dim == other.dim:
            return Gaussian(self.dim, self.eta - other.eta, self.Lam - other.Lam)
        else:
            raise ValueError("Dimensionality of Gaussians do not match.")

    def marginalise(self, keep:list[int], pseudo_inv:NDArray[np.float64] | None = None):
        """
        Marginalises Gaussian via the Schur complement.
        Lam_marg = Lam_aa - Lam_ab * (Lam_bb)^-1 * Lam_ba
        eta_marg = eta_a - Lam_ab * (Lam_bb)^-1 * eta_b
        """
        a = keep
        b = np.setdiff1d(range(self.dim), keep)

        eta_a = self.eta[a]
        eta_b = self.eta[b]

        Lam_bb = self.Lam[np.ix_(b, b)]
        Lam_ab = self.Lam[np.ix_(a, b)]
        Lam_ba = self.Lam[np.ix_(b, a)]
        Lam_aa = self.Lam[np.ix_(a, a)]

        inv_Lam_bb = pseudo_inv
        if pseudo_inv is None:
            try:
                inv_Lam_bb = np.linalg.inv(Lam_bb)
            except np.linalg.LinAlgError:
                raise ValueError(
                    "Input matrix is not invertible. Computation of Schur Complement not possible"
                )
            
        Lam_marg = Lam_aa - Lam_ab @ inv_Lam_bb @ Lam_ba
        eta_marg = eta_a - Lam_ab @ inv_Lam_bb @ eta_b

        return Gaussian(len(keep), eta_marg, Lam_marg)

    def to_moment(self) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Converts Gaussian in canonical form to moment form. 
        """
        Sigma = np.asarray(np.linalg.inv(self.Lam), dtype=np.float64)
        mu = Sigma @ self.eta
        return (mu, Sigma)

    def damp(self):
        """

        """
        pass

    

    
