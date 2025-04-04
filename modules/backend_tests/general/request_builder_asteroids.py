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

    def build(self):
        return self.params
