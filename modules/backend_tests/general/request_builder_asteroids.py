class AsteroidRequestBuilder:
    def __init__(self):
        self.params = {}

    def with_date_range(self, start, end):
        self.params['date-min'] = start
        self.params['date-max'] = end
        return self

    def with_dist_max(self, distance):
        self.params['dist-max'] = distance
        return self

    def with_dist_min(self, distance):
        self.params['dist-min'] = distance
        return self

    def with_dist_range(self, dist_min, dist_max):
        return self.with_dist_min(dist_min).with_dist_max(dist_max)

    def with_h_max(self, h_value):
        """Set upper bound for absolute magnitude (H) filter."""
        self.params['h-max'] = h_value
        return self

    def with_v_inf_max(self, velocity):
        """Set maximum relative velocity (v-inf) filter in km/s."""
        self.params['v-inf-max'] = velocity
        return self

    def with_kind(self, kind_value):
        # should be 'a', 'c', or 'p'
        self.params['kind'] = kind_value
        return self

    def with_fullname(self):
        self.params['fullname'] = 'true'
        return self

    def with_diameter(self):
        self.params['diameter'] = 'true'
        return self

    def with_julian_range(self, t_min, t_max, t_origin=None):
        self.params['t-min'] = t_min
        self.params['t-max'] = t_max
        if t_origin:
            self.params['t-origin'] = t_origin
        return self

    def build(self):
        return self.params
