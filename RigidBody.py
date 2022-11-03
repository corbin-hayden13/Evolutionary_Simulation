import pygame as pg
import math


""" TODO - Want to rework xy_velocity to one speed vector, add an angular attribute """
class RigidBody:
    def __init__(self, mass, xy_pos, wh_size, xy_velocity, xy_accel, bouncy=False):
        self.mass = int(mass)
        self.angle = 0
        # must represent center because top_left corner will rotate!!
        self.xy_pos = list(xy_pos)
        self.wh_size = list(wh_size)
        self.wh_size[0] *= self.mass / 10
        self.wh_size[1] *= self.mass / 10
        self.xy_velocity = list(xy_velocity)
        self.xy_accel = list(xy_accel)
        self.bouncy = bool(bouncy)
        # pos_x, neg_x, pos_y, neg_y
        self.collision = [0, 0, 0, 0]
        self.body_surface = pg.Surface(self.wh_size, pg.SRCALPHA)
        self.body_rect = self.body_surface.get_rect()
        self.head = pg.Rect(0, 0, self.body_surface.get_height() / 5, self.body_surface.get_width())
        self.rgb_color = [0, 0, 0]

    def step(self):
        self.xy_pos[0] += self.xy_velocity[0]
        self.xy_pos[1] += self.xy_velocity[1]

    def accelerate(self):
        self.xy_velocity[0] += self.xy_accel[0]
        self.xy_velocity[1] += self.xy_accel[1]

    def calc_xy_accel(self, base_accel, rotation):
        return [base_accel * math.cos(rotation), base_accel * math.sin(rotation)]

    def get_rotation_angle(self):
        rot_offset = 90
        x_comp = self.xy_velocity[0]
        y_comp = -1 * self.xy_velocity[1]

        if x_comp == 0:
            if y_comp > 0:
                return 90 - rot_offset
            if y_comp < 0:
                return 270 - rot_offset
            if y_comp == 0:
                return 0 - rot_offset

        angle = math.atan((y_comp/x_comp))

        if x_comp > 0 and y_comp < 0:
            return angle * (180/math.pi) - rot_offset + 360

        if x_comp < 0:
            return angle * (180/math.pi) - rot_offset + 180

        if y_comp == 0:
            if x_comp > 0:
                return 0 - rot_offset
            if x_comp < 0:
                return 180 - rot_offset

        return angle * (180/math.pi) - rot_offset

    def rotate_to(self, degrees, pivot_offset_from_center):
        # pos: Where on the screen the pivot (center) is
        pos = [self.xy_pos[0] + pivot_offset_from_center[0], self.xy_pos[1] + pivot_offset_from_center[1]]
        originPos = [self.body_surface.get_width() / 2, self.body_surface.get_height() / 2]
        surface_rect = self.body_surface.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
        offset_center_to_pivot = pg.math.Vector2(pos) - surface_rect.center

        # rotated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-degrees)

        # rotated image center
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

        # get a rotated image
        rotated_image = pg.transform.rotate(self.body_surface, degrees)
        self.body_rect = rotated_image.get_rect(center=rotated_image_center)

        return rotated_image, self.body_rect

    """ Used in conjunction with check_collide_bounds """
    def apply_horizontal_friction(self, coeff_friction):
        if self.xy_velocity[0] == 0:
            return
        else:
            # Get 1 or -1 based on velocity
            friction_accel = (1 if self.xy_velocity[0] < 0 else -1) * coeff_friction
            """ If friction will make velocity switch sign, set to 0 to eliminate stuttering
             and other weird behavior from friction """
            if abs(friction_accel) > abs(self.xy_velocity[0]):
                self.xy_velocity[0] = 0
            else:
                self.xy_velocity[0] += friction_accel

    def apply_vertical_friction(self, coeff_friction):
        if self.xy_velocity[1] == 0:
            return
        else:
            # Get 1 or -1 based on velocity
            friction_accel = (1 if self.xy_velocity[1] < 0 else -1) * coeff_friction
            """ If friction will make velocity switch sign, set to 0 to eliminate stuttering
             and other weird behavior from friction """
            if abs(friction_accel) > abs(self.xy_velocity[1]):
                self.xy_velocity[1] = 0
            else:
                self.xy_velocity[1] += friction_accel
        
    def check_collide_bounds(self, origin, width_height, x_pass_through=False,
                             y_pass_through=False):
        self.collision = [0, 0, 0, 0]  # Acts as a list of flags, could be useful later on
        """ Cannot use self.body_rect.center for offset because it becomes the xy_pos after first call to rotate_to """
        # when colliding with right of screen
        if self.xy_pos[0] + self.body_rect.width / 2 >= width_height[0]:
            if self.bouncy:
                self.xy_velocity[0] *= -1
                self.xy_pos[0] = ((width_height[0] - self.body_rect.width / 2) if not x_pass_through
                                  else (origin[0] + self.body_rect.width / 2))
                self.collision[0] = 1
            else:
                self.xy_velocity[0] = (0 if not x_pass_through else self.xy_velocity[0])
                self.xy_pos[0] = ((width_height[0] - self.body_rect.width / 2) if not x_pass_through
                                  else (origin[0] + self.body_rect.width / 2))
                self.collision[0] = 1

        # when colliding with left of screen
        if self.xy_pos[0] - self.body_rect.width / 2 <= origin[0]:
            if self.bouncy:
                self.xy_velocity[0] *= -1
                self.xy_pos[0] = ((origin[0] + self.body_rect.width / 2) if not x_pass_through
                                  else (width_height[0] - self.body_rect.width / 2))
                self.collision[1] = 1
            else:
                self.xy_velocity[0] = (0 if not x_pass_through else self.xy_velocity[0])
                self.xy_pos[0] = ((origin[0] + self.body_rect.width / 2) if not x_pass_through
                                  else (width_height[0] - self.body_rect.width / 2))
                self.collision[1] = 1

        # when colliding with bottom of screen
        if self.xy_pos[1] + self.body_rect.height / 2 >= width_height[1]:
            if self.bouncy:
                self.xy_velocity[1] *= -1
                self.xy_pos[1] = width_height[1] - self.body_rect.height / 2
                self.collision[2] = 1
            else:
                self.xy_velocity[1] = (0 if not y_pass_through else self.xy_velocity[1])
                self.xy_pos[1] = width_height[1] - self.body_rect.height / 2
                self.collision[2] = 1

        # when colliding with top of screen
        if self.xy_pos[1] - self.body_rect.height / 2 <= origin[1]:
            if self.bouncy:
                self.xy_velocity[1] *= -1
                self.xy_pos[1] = origin[1] + self.body_rect.height / 2
                self.collision[3] = 1
            else:
                self.xy_velocity[1] = (0 if not y_pass_through else self.xy_velocity[1])
                self.xy_pos[1] = origin[1] + self.body_rect.height / 2
                self.collision[3] = 1

        return self.collision

    def check_collide_rigid_body(self, other):  # Not for line-of-sight collision implementation
        # There are 16 different possible collision types with other RigidBodies
        collision = [0] * 16
        # self right -> other left
        if self.xy_pos[0] + self.body_rect.width / 2 >= other.xy_pos[0] - other.body_rect.width / 2:
            collision[0] = 1
        # self right -> other right
        if self.xy_pos[0] + self.body_rect.width / 2 >= other.xy_pos[0] + other.body_rect.width / 2:
            collision[0] = 1
        # self right -> other top
        if self.xy_pos[0] + self.body_rect.width / 2 >= other.xy_pos[0] + other.body_rect.width / 2:
            collision[0] = 1


def add_angles(angle1, angle2):
    temp_angle = angle1 + angle2
    if temp_angle >= 360:
        return temp_angle - 360
    if temp_angle < 0:
        return temp_angle + 360

    return temp_angle

