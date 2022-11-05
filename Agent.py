import copy
import random as rand
import math
import RigidBody as rb


class Agent:
    def __init__(self, rgb_color, mass, energy, sight_dist, reproduction_factor):
        self.rigid_body = None
        self.rgb_color = list(rgb_color)
        self.mass = mass
        self.strength = 2 / math.log10(mass)  # As a measure of acceleration for the agent
        self.wants_to_move = False
        self.energy = energy
        self.sight_dist = sight_dist  # this is the range an agent can look
        self.sight_arc = math.floor(5 * 70 / math.log(sight_dist))  # In degrees, arbitrarily chose 5 * 30
        self.is_controllable = False
        self.desire_to_reproduce = reproduction_factor
        # Possibly gene for how many children are created when reproducing?

        # Easier way of creating random mutations in agents for later algorithm
        self.gene_sequece = [self.rgb_color, self.mass, self.energy, self.sight_dist]

    def set_rigid_body(self, rigid_body):
        self.rigid_body = rigid_body
        self.rigid_body.accel = self.strength
        self.rigid_body.body_surface.fill(self.rgb_color)
        self.rigid_body.rgb_color = self.rgb_color

    def step(self, origin, surface, xy_pass_through):
        if self.rigid_body is None:
            print("No rigid body added to Agent")
            return

        self.rigid_body.accelerate()
        self.rigid_body.step()
        accel = 1  # Friction coefficient

        self.rigid_body.apply_vertical_friction(accel)
        self.rigid_body.apply_horizontal_friction(accel)

        # True, False to trigger x_pass_through, no y_pass_through
        self.rigid_body.check_collide_bounds(origin, [surface.get_width(), surface.get_height()],
                                             xy_pass_through[0], xy_pass_through[1])

    def wander(self, origin, surface, xy_pass_through):
        if self.is_controllable:
            self.step(origin, surface, xy_pass_through)
            return

        # Has a chance to start moving, will move until it runs out of energy, then waits to recharge energy
        chance = rand.randint(1, 10)
        if self.wants_to_move or chance > 3:  # want 70% chance to move
            self.wants_to_move = True
            if self.wants_to_move and self.energy != 0:
                rotation = rand.randint(0, 359)
                self.rigid_body.angle = rotation  # Potentially add offset here
                self.step(origin, surface, xy_pass_through)
                self.energy -= self.calc_energy_cost(True)

        if self.energy <= 0:
            self.step(origin, surface, xy_pass_through)
            self.wants_to_move = False
            # self.rigid_body.xy_accel = [0, 0]  # No acceleration

        # Condition to regenerate energy
        if self.rigid_body.xy_velocity[0] == 0 and self.rigid_body.xy_velocity[1] == 0:  # Not moving
            self.energy += 1

    # def find_food(self):

    def calc_energy_cost(self, is_moving):
        total_cost = 0
        if is_moving:
            total_cost += self.rigid_body.mass
            total_cost += math.floor(self.strength)

        total_cost += 1  # For existing

        return total_cost

    def print_pos(self):
        print("X =", self.rigid_body.xy_pos[0])
        print("Y =", self.rigid_body.xy_pos[1])
        print()
