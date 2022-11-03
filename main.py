import pygame as pg
from pygame.locals import *
import random as rand
import math
import RigidBody as rb
import Agent
import Food
import AgentAI as ai
import Platform


def init_pygame(wh_screen, background_color):
    pg.init()
    screen = pg.display.set_mode(wh_screen)
    screen.fill(background_color)
    pg.display.flip()  # updates display using flip()

    return screen


def draw_agent(surface, agent, food_list):
    # To make the agent "remember" the direction it was facing when moving
    agent.rigid_body.angle = (agent.rigid_body.angle if (agent.rigid_body.xy_velocity[0] == 0
                                                         and agent.rigid_body.xy_velocity[1] == 0)
                              else agent.rigid_body.get_rotation_angle())
    # Get rotated surface from the rotate_to() RigidBody method
    rotated_surface = agent.rigid_body.rotate_to(agent.rigid_body.angle, [0, 0])
    # Draw a small black head to visually represent the front of the agent
    pg.draw.rect(agent.rigid_body.body_surface, [0, 0, 0], agent.rigid_body.head)
    surface.blit(rotated_surface[0], rotated_surface[1])
    # dpg.draw.rect(surface, [255, 0, 0], agent.rigid_body.body_rect)
    pg.draw.circle(surface, [255, 255, 0], agent.rigid_body.xy_pos, 1)
    pg.draw.line(surface, [255, 255, 255], agent.rigid_body.xy_pos, ai.look(surface, agent, food_list))
    left_line_angle = rb.add_angles(agent.rigid_body.angle, -1 * (agent.sight_arc // 2))
    right_line_angle = rb.add_angles(agent.rigid_body.angle, (agent.sight_arc // 2))
    """
    pg.draw.line(surface, [50, 255, 200], agent.rigid_body.xy_pos,
                 [agent.rigid_body.xy_pos[0] + (50 * math.cos(left_line_angle)),
                  agent.rigid_body.xy_pos[1] + (50 * math.sin(left_line_angle))])
    pg.draw.line(surface, [50, 255, 200], agent.rigid_body.xy_pos,
                 [agent.rigid_body.xy_pos[0] + (50 * math.cos(right_line_angle)),
                  agent.rigid_body.xy_pos[1] + (50 * math.sin(right_line_angle))])"""


def draw_food(surface, food):
    surface.blit(food.rigid_body.body_surface, food.rigid_body.xy_pos)
    pg.draw.circle(surface, food.rgb_color, food.rigid_body.xy_pos, food.size)


def main():
    SURFACE_WH = [960, 540]
    # SURFACE_WH = [1920, 1080]
    LIGHT_GREY = [166, 166, 166]
    FPS = 60
    Y_ACCEL = 3  # Global accel used for x_accel and y_accel for the moment
    X_ACCEL = 3
    NUM_AGENTS = 1
    STARTING_FOOD = 1

    """ Start by creating the pygame screen """
    screen = init_pygame(SURFACE_WH, LIGHT_GREY)

    """ Next, create initial agents and food particles """
    # Agent is just an object with a color value and methods for defining movement
    agent_list = []
    for a in range(NUM_AGENTS):
        agent_list.append(Agent.Agent([rand.randint(0, 255), rand.randint(0, 255), rand.randint(0, 255)],
                                      rand.randint(5, 20), 100, rand.randint(100, 200)))
        agent_list[a].set_rigid_body(rb.RigidBody(agent_list[a].mass, [SURFACE_WH[0] // 2, SURFACE_WH[1] // 2], [10, 40],
                                                  # [rand.randint(-10, 10), rand.randint(-10, 10)],
                                                  [0, 0], [0, 0], True))

    # Food will be circles drawn using the RigidBody class for collisions and detection
    food_list = []
    for b in range(STARTING_FOOD):
        color = [rand.randint(1, 255), rand.randint(1, 255), rand.randint(1, 255)]
        food_list.append(Food.Food(rand.randint(5, 20), color))
        food_list[b].set_rigid_body(rb.RigidBody(food_list[b].size,
                                                 [rand.randint(food_list[b].size // 2,
                                                               SURFACE_WH[0] - food_list[b].size // 2),
                                                  rand.randint(food_list[b].size // 2,
                                                               SURFACE_WH[1] - food_list[b].size // 2)],
                                                 [food_list[b].size*2, food_list[b].size*2], [0, 0], [0, 0]))

    # This is the one player-controllable agent for playing with
    agent_list[0].is_controllable = True

    """ Some booleans to define if the game should be running, if agents can be controlled, and other control flags """
    running = True
    jumped = False  # Implement better jumping mechanics later
    in_control = True
    prev_b_down = False

    """ Main Game Loop """
    while running:
        # Update Frame
        pg.display.flip()
        screen.fill(LIGHT_GREY)

        # For every current agent, let's calculate the movement behavior then draw them to the screen
        for agent in agent_list:
            agent.wander([0, 0], screen, [False, False])
            draw_agent(screen, agent, food_list)  # food_list for testing ai.look()

        # Redraw food particles, later respawn more particles based on cooldown
        for food in food_list:
            draw_food(screen, food)

        for event in pg.event.get():
            # Handy little feature of hitting ESCAPE to quit the game
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False

            # Ternary operation to check if an agent can be manually controlled
            # If so, WASD used to control up, down, left, and right movement
            if event.type == pg.KEYDOWN and not jumped and in_control:
                if event.key == pg.K_w:
                    for agent in agent_list:
                        agent.rigid_body.xy_accel[1] = (-1 * Y_ACCEL if agent.is_controllable
                                                        else agent.rigid_body.xy_accel[1])

                if event.key == pg.K_s:
                    for agent in agent_list:
                        agent.rigid_body.xy_accel[1] = (Y_ACCEL if agent.is_controllable
                                                        else agent.rigid_body.xy_accel[1])

                if event.key == pg.K_d:
                    for agent in agent_list:
                        agent.rigid_body.xy_accel[0] = (X_ACCEL if agent.is_controllable
                                                        else agent.rigid_body.xy_accel[1])

                if event.key == pg.K_a:
                    for agent in agent_list:
                        agent.rigid_body.xy_accel[0] = (-1 * X_ACCEL if agent.is_controllable
                                                        else agent.rigid_body.xy_accel[1])

                if event.key == pg.K_b and not prev_b_down:
                    # Flag to make this button toggleable, not holdable
                    prev_b_down = True
                    for agent in agent_list:
                        agent.rigid_body.bouncy = (True if not agent.rigid_body.bouncy else False)

            if event.type == pg.KEYUP and in_control:
                if event.key == pg.K_w or event.key == pg.K_s:
                    for agent in agent_list:
                        agent.rigid_body.xy_accel[1] = (0 if agent.is_controllable else agent.rigid_body.xy_accel[1])

                if event.key == pg.K_d or event.key == pg.K_a:
                    for agent in agent_list:
                        agent.rigid_body.xy_accel[0] = (0 if agent.is_controllable else agent.rigid_body.xy_accel[1])

                if event.key == pg.K_b:
                    prev_b_down = False

        pg.time.delay(1000//FPS)


if __name__ == '__main__':
    main()

