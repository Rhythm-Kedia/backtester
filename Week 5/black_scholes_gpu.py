import math
from numba import cuda
import numpy as np

@cuda.jit(device=True)
def norm_cdf_device(x): return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

@cuda.jit
def black_scholes_kernel(s_d, k_d, t_d, r_d, sigma_d, option_type_d, prices_d):
    """GPU-accelerated Black-Scholes formula for options pricing"""
    i = cuda.grid(1)
    if i < s_d.size:
        s = s_d[i]
        k = k_d[i]
        t = t_d[i]
        r = r_d[i]
        sigma = sigma_d[i]

        if t <= 0:
            if option_type_d[i] == 0: prices_d[i] = max(0.0, s - k)
            else: prices_d[i] = max(0.0, k - s)
            return

        d1 = (math.log(s / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * math.sqrt(t))
        d2 = d1 - sigma * math.sqrt(t)

        if option_type_d[i] == 0: price = s * norm_cdf_device(d1) - k * math.exp(-r * t) * norm_cdf_device(d2)
        else: price = k * math.exp(-r * t) * norm_cdf_device(-d2) - s * norm_cdf_device(-d1)
        
        prices_d[i] = price

@cuda.jit
def greeks_kernel(s_d, k_d, t_d, r_d, sigma_d, option_type_d, delta_d, gamma_d, theta_d, vega_d):
    """
    CUDA kernel for calculating option Greeks (Delta, Gamma, Theta, Vega) in parallel.
    """
    i = cuda.grid(1)
    if i < s_d.size:
        s = s_d[i]
        k = k_d[i]
        t = t_d[i]
        r = r_d[i]
        sigma = sigma_d[i]

        if t <= 0:
            delta_d[i] = 1.0 if s > k else 0.0
            gamma_d[i] = 0.0
            theta_d[i] = 0.0
            vega_d[i] = 0.0
            return

        d1 = (math.log(s / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * math.sqrt(t))
        d2 = d1 - sigma * math.sqrt(t)
        
        pdf_d1 = math.exp(-d1**2 / 2) / (math.sqrt(2 * math.pi))

        gamma_d[i] = pdf_d1 / (s * sigma * math.sqrt(t))
        vega_d[i] = s * pdf_d1 * math.sqrt(t) * 0.01

        if option_type_d[i] == 0: # Call
            delta_d[i] = norm_cdf_device(d1)
            theta_d[i] = (-(s * pdf_d1 * sigma) / (2 * math.sqrt(t)) - r * k * math.exp(-r * t) * norm_cdf_device(d2)) / 365.0
        else: # Put
            delta_d[i] = norm_cdf_device(d1) - 1.0
            theta_d[i] = (-(s * pdf_d1 * sigma) / (2 * math.sqrt(t)) + r * k * math.exp(-r * t) * norm_cdf_device(-d2)) / 365.0

def black_scholes_gpu(s, k, t, r, sigma, option_types):
    """
    Host function to price a batch of options using the GPU.
    option_types: 0 for call, 1 for put.
    """
    n = s.size
    s_d = cuda.to_device(s)
    k_d = cuda.to_device(k)
    t_d = cuda.to_device(t)
    r_d = cuda.to_device(r)
    sigma_d = cuda.to_device(sigma)
    option_type_d = cuda.to_device(option_types)
    
    prices_d = cuda.device_array(n, dtype=np.float64)

    threads_per_block = 256
    blocks_per_grid = (n + threads_per_block - 1) // threads_per_block
    
    black_scholes_kernel[blocks_per_grid, threads_per_block](s_d, k_d, t_d, r_d, sigma_d, option_type_d, prices_d)
    
    return prices_d.copy_to_host()

def greeks_gpu(s, k, t, r, sigma, option_types):
    """
    Host function to calculate Greeks for a batch of options using the GPU.
    """
    n = s.size
    s_d = cuda.to_device(s)
    k_d = cuda.to_device(k)
    t_d = cuda.to_device(t)
    r_d = cuda.to_device(r)
    sigma_d = cuda.to_device(sigma)
    option_type_d = cuda.to_device(option_types)

    delta_d = cuda.device_array(n, dtype=np.float64)
    gamma_d = cuda.device_array(n, dtype=np.float64)
    theta_d = cuda.device_array(n, dtype=np.float64)
    vega_d = cuda.device_array(n, dtype=np.float64)

    threads_per_block = 256
    blocks_per_grid = (n + threads_per_block - 1) // threads_per_block

    greeks_kernel[blocks_per_grid, threads_per_block](s_d, k_d, t_d, r_d, sigma_d, option_type_d, delta_d, gamma_d, theta_d, vega_d)

    return (
        delta_d.copy_to_host(),
        gamma_d.copy_to_host(),
        theta_d.copy_to_host(),
        vega_d.copy_to_host(),
    )
