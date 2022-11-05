"""
Hayden Corbin - 11/2/2022

Purpose of this is to determine the movement behavior of the Agents
    The cleaner middle-man between the main game and the Agent class
"""
import math
import numpy as np
import pygame as pg
import RigidBody as rb


""" TODO
Make this better;  Need the agent to remember the location of food
    so that it doesn't overshoot the food nor wander right after finding food
"""
def seek_food(surface, agent, food_list):
    # Function to help the agents find food
    potential_poi = look(surface, agent, food_list)
    if potential_poi[0] or potential_poi[1]:  # Because value of 0 -> False
        agent.rigid_body.angle = agent.rigid_body.get_rotation_angle(potential_poi[0] - agent.rigid_body.xy_pos[0],
                                                                     potential_poi[1] - agent.rigid_body.xy_pos[1])
        agent.rigid_body.accelerate()
        agent.step([0, 0], surface, [False, False])
    else:
        agent.wander([0, 0], surface, [False, False])


def seek_mate(agent_list, wh_surface):
    # Function to help the agents find a mate
    return 0


""" Raycasting function
Create a line from xy_pos of agent cast to some point calculated by the sight_dist of the agent, within the sight_arc
    of the agent
If cast ray collides with a rigid_body, return the xy_pos of that rigid_body
This is extremely computation heavy, look for optimizations
"""
def look(surface, agent, other_list):
    num_rays = 5  # This is actually quite sufficient because the arc is so narrow for agents
    rot_offset = 90  # To align with the rotation of the agent
    angle_diff = agent.sight_arc / (num_rays - 1)  # Number empty spaces between lines = number_lines - 1
    max_step = 3
    for ray_num in range(num_rays):
        # Calculate angle offset from clockwise
        angle_offset = agent.rigid_body.angle - ((num_rays // 2) * angle_diff) + (angle_diff * ray_num) + rot_offset
        cos_val = math.cos(angle_offset * math.pi / 180)
        sin_val = math.sin(angle_offset * math.pi / 180)

        """# Used to visually represent FOV of agent for debugging
        line_point = [agent.rigid_body.xy_pos[0] + (agent.sight_dist * math.cos(angle_offset * math.pi/180)),
                      agent.rigid_body.xy_pos[1] - (agent.sight_dist * math.sin(angle_offset * math.pi/180))]

        pg.draw.line(surface, [200, 200, 100], agent.rigid_body.xy_pos, line_point)"""

        """ Slight optimization to increase step size greatly increases performance. Do not increase step size to
              greater than the size of any rigid_body blitted to screen to preserve accuracy
        """
        for point in range(0, agent.sight_dist, max_step):
            # use a point along ray projected from agent's center
            # find point at end of cast ray as ray is being cast
            proj_ray_point = [agent.rigid_body.xy_pos[0] + (point * cos_val),
                              agent.rigid_body.xy_pos[1] - (point * sin_val)]

            for other in other_list:
                half_width = other.rigid_body.body_rect.width / 2
                half_height = other.rigid_body.body_rect.height / 2
                # Check if projected point has entered any rigid_body passed in the other_list
                if (proj_ray_point[0] >= (other.rigid_body.xy_pos[0] - half_width))\
                and (proj_ray_point[0] <= (other.rigid_body.xy_pos[0] + half_width))\
                and (proj_ray_point[1] >= (other.rigid_body.xy_pos[1] - half_height))\
                and (proj_ray_point[1] <= (other.rigid_body.xy_pos[1] + half_height)):
                    return other.rigid_body.xy_pos

    return [0, 0]  # should return other's center

