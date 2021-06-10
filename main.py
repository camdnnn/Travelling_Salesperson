import pygame.display
from shapes import *

# can be ignored
pygame.init()
InfoObj = pygame.display.Info()

# height and width of the window
SCREEN_FRACTION = 4 / 5
WIDTH, HEIGHT = int(InfoObj.current_w * SCREEN_FRACTION), int(InfoObj.current_h * SCREEN_FRACTION)

# radius for a circle
RADIUS = HEIGHT // 45

# line width for lines
LINE_WIDTH = RADIUS // 2

# number of circles
COUNT = 0
MAX_SIZE = 9

# colors that can be used
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# values for left and right mouse buttons
LEFT = 0
MIDDLE = 1
RIGHT = 2

# window generation and setting title
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Travelling Salesperson")


# drawing of the window during game loop
def draw_window(circles):
    circles.draw_lines()
    circles.draw_circles()
    pygame.display.update()


# main function
def main():
    # initializing display and circles
    WIN.fill(BLACK)
    pygame.display.update()
    circles = CircleSet(COUNT, RADIUS, LINE_WIDTH, WIN, WIN.get_at((0, 0)))
    if COUNT > 0:
        draw_window(circles)
    run = True
    last_printout = None
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                # holds if left shift is held down
                l_shift_held = pygame.key.get_pressed()[pygame.K_LSHIFT]

                # holds the circles returned by the ordering function
                ord_circles = None

                # resets the colors if left shift is not the button pressed
                if event.key != pygame.K_LSHIFT:
                    circles.reset_colors()
                count = len(circles.get_circles())

                # if the desired key is pressed than the desired function is ran
                # if applicable if left shift is held then the cluster order version is ran instead
                # SPACE - Generate Circles
                # 1 - Random Order
                # 2 - Closest Order
                # 3 - Value Cutoff Order
                # 0 - Optimal Order
                if event.key == pygame.K_SPACE:
                    circles.generate_circles()
                    draw_window(circles)
                elif event.key == pygame.K_1:
                    if l_shift_held and count >= 2:
                        ord_circles = cluster_order(circles.get_circles(), random_order)
                    else:
                        ord_circles = random_order(circles.get_circles())
                elif event.key == pygame.K_2:
                    if l_shift_held and count >= 2:
                        ord_circles = cluster_order(circles.get_circles(), closest_order)
                    else:
                        ord_circles = closest_order(circles.get_circles())
                elif event.key == pygame.K_3:
                    if l_shift_held and count >= 2:
                        ord_circles = cluster_order(circles.get_circles(), value_cutoff_optimal_order)
                    else:
                        ord_circles = value_cutoff_optimal_order(circles.get_circles())
                elif event.key == pygame.K_0:
                    if l_shift_held and count >= 2:
                        ord_circles = cluster_order(circles.get_circles(), optimal_order, MAX_SIZE)
                    elif count <= MAX_SIZE:
                        ord_circles = optimal_order(circles.get_circles())

                # ord circles holds the circles returned by a function
                # if none of them ran then that means the circles are the same
                # so only needs to run if ord circles is defined
                if ord_circles is not None:
                    circles.set_circles(ord_circles)
                    draw_window(circles)

            pressed = pygame.mouse.get_pressed(3)

            # if the mouse if pressed and it is left being pressed then a new circle is created where the mouse is
            # the extra check is so that holding left does not just make more circles
            if event.type == pygame.MOUSEBUTTONDOWN and pressed[LEFT]:
                mouse_pos = pygame.mouse.get_pos()
                x, y = mouse_pos
                center = (round(x), round(y))
                circles.add_circle(center)
                draw_window(circles)

            # if right is held then any circle the mouse is touching is deleted
            elif pressed[RIGHT]:
                x, y = pygame.mouse.get_pos()
                location = (x, y)
                circles.remove_circle(location)
                draw_window(circles)

            # if middle is held then any circle the mouse it touching gets its coordinates printed
            elif pressed[MIDDLE]:
                x, y = pygame.mouse.get_pos()
                location = (x, y)

                # this is here so that it does not repeat outputs and does not print None
                result = circles.find_center(location)
                if (result is not last_printout or event.type == pygame.MOUSEBUTTONDOWN) and result is not None:
                    print(result)
                    last_printout = result
    # quits the game
    pygame.quit()


# makes it so only the main program runs this code
if __name__ == "__main__":
    main()
