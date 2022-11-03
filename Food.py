class Food:
    def __init__(self, size, rgb_color):
        self.rigid_body = None
        self.size = size
        self.energy = size * 2
        self.rgb_color = list(rgb_color)

    def set_rigid_body(self, rigid_body):
        self.rigid_body = rigid_body

