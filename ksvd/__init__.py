# coding:utf-8
import numpy as np
import scipy as sp
from sklearn.linear_model import orthogonal_mp_gram


class ApproximateKSVD(object):
    def __init__(self, n_components, n_nonzero_coefs=None):
        self.components_ = None
        self.max_iter = 2
        self.tol = 1e-6
        self.n_components = n_components
        self.n_nonzero_coefs = n_nonzero_coefs
        if self.n_nonzero_coefs is None:
            self.n_nonzero_coefs = n_components

    def _update_dict(self, X, D, gamma):
        for j in range(self.n_components):
            I = gamma[:, j] > 0
            if np.sum(I) == 0:
                continue

            D[j, :] = 0
            g = gamma[I, j].T
            r = X[I, :] - gamma[I, :].dot(D)
            d = r.T.dot(g)
            d /= np.linalg.norm(d)
            g = r.dot(d)
            D[j, :] = d
            gamma[I, j] = g.T
        return D, gamma

    def _initialize(self, X):
        u, s, vt = sp.sparse.linalg.svds(X, k=self.n_components)
        return np.dot(np.diag(s), vt)

    def _transform(self, D, X):
        gram = D.dot(D.T)
        Xy = D.dot(X.T)
        return orthogonal_mp_gram(
            gram, Xy, n_nonzero_coefs=self.n_nonzero_coefs).T

    def fit(self, X):
        """
        Parameters
        ----------
        X: shape = [n_samples, n_features]
        """
        D = self._initialize(X)
        D /= np.linalg.norm(D, axis=1)[:, np.newaxis]
        for i in range(self.max_iter):
            gamma = self._transform(D, X)
            e = np.linalg.norm(X - gamma.dot(D))
            if e < self.tol:
                break
            D, gamma = self._update_dict(X, D, gamma)

        self.components_ = D
        return self

    def transform(self, X):
        return self._transform(self.components_, X)
