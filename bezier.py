def get_bezier_point(p0, p1, p2, p3, t):
    u = 1.0 - t
    b0 = u * u * u
    b1 = 3.0 * u * u * t
    b2 = 3.0 * u * t * t
    b3 = t * t * t
    return b0 * p0 + b1 * p1 + b2 * p2 + b3 * p3
