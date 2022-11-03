"""
Hayden Corbin - 11/2/2022

Purpose of this is to determine the movement behavior of the Agents
    The cleaner middle-man between the main game and the Agent class
"""
import math
import pygame as pg
import RigidBody as rb


def seek_food(agent_list, food_list, wh_surface):
    # Function to help the agents find food
    return 0


def seek_mate(agent_list, wh_surface):
    # Function to help the agents find a mate
    return 0


""" Raycasting function """
def look(surface, agent, other_list):
    num_rays = 5
    angle_diff = agent.sight_arc // (num_rays - 1)  # Number empty spaces between lines = number_lines - 1
    for ray_num in range(num_rays):
        angle_offset = rb.add_angles(rb.add_angles(agent.rigid_body.angle, -(2 * angle_diff)), (ray_num * angle_diff))
        angle_offset += 180
        print(angle_offset, ",", agent.rigid_body.angle)
        line_point = [agent.rigid_body.xy_pos[0] + math.floor(agent.sight_dist * math.cos(angle_offset)),
                      agent.rigid_body.xy_pos[1] + math.floor(agent.sight_dist * math.sin(angle_offset))]
        print(line_point)
        print(agent.rigid_body.xy_pos)
        pg.draw.line(surface, [200, 200, 100], agent.rigid_body.xy_pos, line_point)
        for point in range(agent.sight_dist):
            # use a point along ray projected from agent's center
            # find point at end of cast ray as ray is being cast
            proj_ray_point = [agent.rigid_body.xy_pos[0] + (point * math.cos(angle_offset)),
                              agent.rigid_body.xy_pos[1] + (point * math.sin(angle_offset))]

            for other in other_list:
                # Check if projected point has entered any rigid_body passed in the other_list
                if (proj_ray_point[0] >= (other.rigid_body.xy_pos[0] - other.rigid_body.body_rect.width / 2))\
                and (proj_ray_point[0] <= (other.rigid_body.xy_pos[0] + other.rigid_body.body_rect.width / 2))\
                and (proj_ray_point[1] >= (other.rigid_body.xy_pos[1] - other.rigid_body.body_rect.height / 2))\
                and (proj_ray_point[1] <= (other.rigid_body.xy_pos[1] + other.rigid_body.body_rect.height / 2)):
                    return other.rigid_body.xy_pos

    print()
    return [0, 0]  # should return other's center

