"""Examples of solving convex problems with TensorFlow."""

import cvxpy as cvx
import numpy as np
import scipy.sparse as sp
import sys
import time

def nn_deconv(n):
    sigma = 0.1*n
    k = 5

    x0 = np.zeros(n)
    x0[np.random.choice(n,k)] = np.random.randn(k)*n/10

    c = np.exp(-np.arange(-n/2., n/2.)**2./(2*sigma**2))/np.sqrt(2*sigma**2*np.pi)
    c[c < 1e-6] = 0
    b = np.convolve(c, x0) + 0.1*np.random.randn(2*n-1)

    x = cvx.Variable(n)
    f = cvx.norm(cvx.conv(c, x) - b)
    return cvx.Problem(cvx.Minimize(f), [x >= 0])

def lasso_dense(n):
    m = 2*n
    A = np.random.randn(m, n)
    A /= np.sqrt(np.sum(A**2, 0))
    b = A*sp.rand(n, 1, 0.1) + 1e-2*np.random.randn(m,1)
    lam = 0.2*np.max(np.abs(A.T.dot(b)))

    x = cvx.Variable(n)
    f = cvx.sum_squares(A*x - b) + lam*cvx.norm1(x)
    return cvx.Problem(cvx.Minimize(f))

def lasso_sparse(n):
    m = 2*n
    A = sp.rand(m, n, 0.1)
    A.data = np.random.randn(A.nnz)
    N = A.copy()
    N.data = N.data**2
    A = A*sp.diags([1 / np.sqrt(np.ravel(N.sum(axis=0)))], [0])

    b = A*sp.rand(n, 1, 0.1) + 1e-2*np.random.randn(m,1)
    lam = 0.2*np.max(np.abs(A.T*b))

    x = cvx.Variable(n)
    f = cvx.sum_squares(A*x - b) + lam*cvx.norm1(x)
    return cvx.Problem(cvx.Minimize(f))

def lasso_conv(n):
    sigma = n/10
    c = np.exp(-np.arange(-n/2., n/2.)**2./(2*sigma**2))/np.sqrt(2*sigma**2*np.pi)
    c[c < 1e-4] = 0

    x0 = np.array(sp.rand(n, 1, 0.1).todense()).ravel()
    b = np.convolve(c, x0) + 1e-2*np.random.randn(2*n-1)
    lam = 0.2*np.max(np.abs(np.convolve(b, c, "valid")))
    print lam

    x = cvx.Variable(n)
    f = cvx.sum_squares(cvx.conv(c, x) - b) + lam*cvx.norm1(x)
    return cvx.Problem(cvx.Minimize(f))

def run_scs(prob):
    # t0 = time.time()
    # prob.solve(solver=cvx.SCS, verbose=True, gpu=True)
    # print "gpu_solve_time: %.2f secs" % (time.time() - t0)

    t0 = time.time()
    prob.solve(solver=cvx.SCS, verbose=True, gpu=False)
    print "cpu_solve_time: %.2f secs" % (time.time() - t0)

    t0 = time.time()
    prob.get_problem_data(cvx.SCS)
    print "get_problem_data_time: %.2f secs" % (time.time() - t0)

def run_tensorflow(prob):
    from cvxflow.problem import TensorProblem
    from cvxflow import scs_tf

    t0 = time.time()
    t_prob = TensorProblem(prob)
    print "problem_time:", time.time() - t0

    t0 = time.time()
    objective = scs_tf.solve(t_prob, max_iters=2500, gpu=True)
    print "gpu_solve_time: %.2f secs" % (time.time() - t0)
    print "objective: %.2e" % objective

    t0 = time.time()
    objective = scs_tf.solve(t_prob, max_iters=2500, gpu=False)
    print "cpu_solve_time: %.2f secs" % (time.time() - t0)
    print "objective: %.2e" % objective
n = 1000
np.random.seed(0)
prob = nn_deconv(n)
run_tensorflow(prob)
run_scs(prob)