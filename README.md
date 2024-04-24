    The Improved FVD model(modified).

    Usage: Initialize with args, then use ``self.result`` as the result.
    The result is calculated when accessing ``self.result`` attribute.

    LaTeX:
    ``a_n(t)=\alpha\{V[ΔX^{jq}_n(t)]-V_n(t)\}-\lambda_1\frac{d\vartheta_n(t)}{dt}+\lambda2\frac{d\phi_n(t)}{dt}``

    Based on Eq. ``(4)``, but we replaced ``\(\lambda_1\frac{d\vartheta_n(t)}{dt}+\lambda_2\frac{d\phi_n(t)}{dt}\)``
    with ``\(\lambda_1\frac{|\vartheta_n(t)-\vartheta_n(t-1)|}{\Delta t_{t,t-1}}+\lambda_2\frac{|\phi_n(t)-\phi_n(t-1)|}{\Delta t_{t,t-1}}\)``,
    where ``\(\vartheta_n(t-1)\)`` and ``\(\phi_n(t-1)\)`` are the data at the previous time point;
    ``\(\Delta t_{t,t-1}\)`` is the time difference from the previous frame to the current frame.
    Since trajectory data is usually composed of discrete data points and is not differentiable,
    thus this method is adopted to represent the rate of change of this variable over time.

    Based on following paper:

    Qi, W., Ma, S., & Fu, C. (2023).
    An improved car-following model considering the influence of multiple preceding vehicles in the same and two adjacent lanes.
    Physica A, 129356.
    https://doi.org/10.1016/j.physa.2023.129356