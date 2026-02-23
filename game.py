"OEC PROJECT"
"THE GOLDEN AGE OF SPACE COMMERCE"
"By: SADAT TANZIM, ZAIN USMANI, AFFAN SYED, ABDERRAHMENE NACERI"

from pygame import *
from math import *
import numpy as np
from collections import deque
from formula_implementation import find_best_flight

init()
font.init()

fullscreen_mode = False
screen = display.set_mode((800, 600))
WIDTH, HEIGHT = screen.get_size()
display.set_caption("GAOS")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE  = (50, 100, 255)
GREEN = (50, 200, 100)
GRAY  = (200, 200, 200)
YELLOW = (255, 220, 60)
RED = (240, 70, 70)

main_font = font.SysFont(None, 40)
coord_font = font.SysFont(None, 24)
ui_font = font.SysFont(None, 28)

clock = time.Clock()
FPS = 60
current_screen = "menu"

btn_mission = Rect(130, 520, 250, 60)#mission button
btn_instructions = Rect(400, 520, 250, 60)#instructions button
btn_launch = Rect(275, 420, 250, 60)#launch button inside mission screen
btn_back = Rect(20, 20, 120, 45)#back button
btn_exit = Rect(WIDTH - 140, 20, 120, 45)

#background images
menu_bg = image.load("images/ss.jpg").convert()
screen1_bg = image.load("images/bg.jpg").convert()
screen2_bg = image.load("images/bbg.jpg").convert()
menu_bg = transform.scale(menu_bg, (WIDTH, HEIGHT))
screen1_bg = transform.scale(screen1_bg, (WIDTH, HEIGHT))
screen2_bg = transform.scale(screen2_bg, (WIDTH, HEIGHT))

logo_img = None
try:
    logo_img = image.load("images/lgo.png").convert_alpha()
except:
    logo_img = None

planet_options = [
    "Mercury", "Venus", "Earth", "Mars", "Ceres",
    "Jupiter", "Saturn", "Uranus", "Neptune",
    "Pluto"
]

planet_imgs = {}
for p in planet_options:
    try:
        planet_imgs[p] = image.load(f"images/{p.lower()}.png").convert_alpha()
    except:
        planet_imgs[p] = None

logo_img = None
try:
    logo_img = image.load("images/lgo.png").convert_alpha()
except:
    logo_img = None

rocket_img = None
try:
    rocket_img = image.load("images/rocket.png").convert_alpha()
    rocket_img = transform.smoothscale(rocket_img, (30, 30))  # Adjust size
except:
    rocket_img = None

dep_rect = Rect(270, 100, 360, 40)
dest_rect = Rect(270, 160, 360, 40)
dep_open = False
dest_open = False
dep_selected = "Earth"
dest_selected = "Mars"

input_rects = [ 
    Rect(270, 220, 360, 40),#launch window
    Rect(270, 340, 360, 40),#payload
]
input_labels = ["Launch Window:", "Payload Mass:"]
input_texts = ["", ""]
active_input = -1

ship_rect = Rect(270, 280, 360, 40)
ship_open = False
ship_options = [
    "Cheverolet", "The Planet Hopper", "Moonivan",
    "Blue Origin Delivery Ship", "Yamaha Space Cycle",
    "Ford F-1500", "Beheamoth"
]
ship_selected = ship_options[0]

orbit_data = {
    "Mercury": (45,  1.0),
    "Venus":   (70,  1.10),
    "Earth":   (100, 1.2),
    "Mars":    (150, 0.90),
    "Ceres":   (180, 0.65),
    "Jupiter": (230, 0.45),
    "Saturn":  (280, 0.40),
    "Uranus":  (320, 0.42),
    "Neptune": (350, 0.45),
    "Pluto":   (400, 0.6),
}

planet_sizes = {
    "Mercury": 12,
    "Venus": 18,
    "Earth": 20,
    "Mars": 15,
    "Jupiter": 40,
    "Saturn": 35,
    "Uranus": 25,
    "Neptune": 24,
    "Pluto": 10,
    "Ceres": 12
}

sun_pos = (WIDTH // 2, HEIGHT // 2 + 40)
sim_time = 0.0

travel_active = False
travel_t = 0.0
travel_from = "Earth"
travel_to = "Mars"
travel_payload = 0.0
travel_ship_name = ""
travel_window = ""
exhaust_trail = []
buffer = deque(maxlen=10)

def safe_float(s, default=0.0):
    try:
        return float(s.strip())
    except:
        return default

def draw_button(rect, text, base_col, hover_col, text_col=BLACK, border_col=BLACK):
    mx, my = mouse.get_pos()
    hovering = rect.collidepoint((mx, my))
    col = hover_col if hovering else base_col

    shadow_rect = rect.copy()
    shadow_rect.x += 4
    shadow_rect.y += 4
    draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=12)

    draw.rect(screen, col, rect, border_radius=12)
    draw.rect(screen, border_col, rect, 2, border_radius=12)

    label = main_font.render(text, True, text_col)
    screen.blit(label, label.get_rect(center=rect.center))
    return hovering

def draw_input_box(r, text, is_active):
    draw.rect(screen, WHITE, r)
    draw.rect(screen, BLACK, r, 3 if is_active else 2)
    t = ui_font.render(text, True, BLACK)
    screen.blit(t, (r.x + 10, r.y + 8))

def draw_dropdown_box(rect, selected, open_state, options, draw_list=True):
    draw.rect(screen, WHITE, rect)
    draw.rect(screen, BLACK, rect, 2)
    screen.blit(ui_font.render(selected, True, BLACK), (rect.x + 10, rect.y + 8))

    draw.polygon(screen, BLACK, [
        (rect.right - 25, rect.y + 15),
        (rect.right - 10, rect.y + 15),
        (rect.right - 17, rect.y + 28),
    ])

    if open_state and draw_list:
        for i, opt in enumerate(options):
            opt_rect = Rect(rect.x, rect.y + (i + 1) * rect.h, rect.w, rect.h)
            draw.rect(screen, WHITE, opt_rect)
            draw.rect(screen, BLACK, opt_rect, 1)
            screen.blit(ui_font.render(opt, True, BLACK), (opt_rect.x + 10, opt_rect.y + 8))

def pick_dropdown_option(pos, rect, open_state, options):
    if not open_state:
        return None
    for i, opt in enumerate(options):
        opt_rect = Rect(rect.x, rect.y + (i + 1) * rect.h, rect.w, rect.h)
        if opt_rect.collidepoint(pos):
            return opt
    return None

def planet_xy(name, t):
    #MATH LOGIC ssm
    r, spd = orbit_data.get(name, (120, 1.0))#ach planet has an orbit radius "r" and an orbit speed "spd"
    ang = t * spd#we convert time into an angle
    #then we use trig to place the planet on a circle:
    #x = center_x + cos(angle) * r
    #y = center_y + sin(angle) * r
    x = sun_pos[0] + cos(ang) * r
    y = sun_pos[1] + sin(ang) * r * 0.7#we multiply y by 0.7 to squash the circle into an ellipse which gives us a 3dish look
    return (int(x), int(y))

def draw_orbit(r):
    #MATH LOGIC or
    rect_orb = Rect(0, 0, r * 2, int(r * 2 * 0.7))#we draw an ellipse whose width is 2r and height is 2r*0.7
    rect_orb.center = sun_pos#the ellipse is centered at the sun position so it looks like an orbit track
    draw.ellipse(screen, (80, 80, 80), rect_orb, 1)

# main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    sim_time += dt * 1.2  # Accumulate time for planet rotation
    mx, my = mouse.get_pos()

    for evt in event.get():
        if evt.type == QUIT:
            running = False

        if evt.type == KEYDOWN:
            if evt.key == K_F11:
                fullscreen_mode = not fullscreen_mode
                if fullscreen_mode:
                    screen = display.set_mode((0, 0), FULLSCREEN)
                else:
                    screen = display.set_mode((800, 600))
                WIDTH, HEIGHT = screen.get_size()
                # Rescale backgrounds
                menu_bg = transform.scale(image.load("images/ss.jpg").convert(), (WIDTH, HEIGHT))
                screen1_bg = transform.scale(image.load("images/bg.jpg").convert(), (WIDTH, HEIGHT))
                screen2_bg = transform.scale(image.load("images/bbg.jpg").convert(), (WIDTH, HEIGHT))
                # Update button positions
                btn_exit = Rect(WIDTH - 140, 20, 120, 45)
                sun_pos = (WIDTH // 2, HEIGHT // 2 + 40)

        if evt.type == MOUSEBUTTONDOWN:
            if btn_exit.collidepoint(evt.pos):#exit button use
                running = False
                continue

            if btn_back.collidepoint(evt.pos):#back button use
                if current_screen in ["screen1", "screen2", "screen3"]:
                    current_screen = "menu"
                    dep_open = dest_open = ship_open = False
                    active_input = -1
                continue

            if current_screen == "menu":
                if btn_mission.collidepoint(evt.pos):
                    current_screen = "screen1"
                elif btn_instructions.collidepoint(evt.pos):
                    current_screen = "screen2"

            elif current_screen == "screen1":
                clicked_any_dropdown = False

                if btn_launch.collidepoint(evt.pos):
                    travel_from = dep_selected
                    travel_to = dest_selected
                    travel_window = input_texts[0].strip()
                    travel_payload = safe_float(input_texts[1], 0.0)
                    travel_ship_name = ship_selected

                    travel_active = True
                    travel_t = 0.0
                    buffer.clear() 
                    current_screen = "screen3"
                    dep_open = dest_open = ship_open = False
                    active_input = -1
                    continue

                #if drop down is open select first to make it wasier
                picked = pick_dropdown_option(evt.pos, dep_rect, dep_open, planet_options)
                if picked:
                    dep_selected = picked
                    dep_open = False
                    clicked_any_dropdown = True

                picked = pick_dropdown_option(evt.pos, dest_rect, dest_open, planet_options)
                if picked:
                    dest_selected = picked
                    dest_open = False
                    clicked_any_dropdown = True

                picked = pick_dropdown_option(evt.pos, ship_rect, ship_open, ship_options)
                if picked:
                    ship_selected = picked
                    ship_open = False
                    clicked_any_dropdown = True

                if clicked_any_dropdown:
                    continue

                #departure dropdown
                if dep_rect.collidepoint(evt.pos):
                    dep_open = not dep_open
                    dest_open = False
                    ship_open = False
                    clicked_any_dropdown = True

                #destination dropdown
                elif dest_rect.collidepoint(evt.pos):
                    dest_open = not dest_open
                    dep_open = False
                    ship_open = False
                    clicked_any_dropdown = True

                #ship dropdown
                elif ship_rect.collidepoint(evt.pos):
                    ship_open = not ship_open
                    dep_open = False
                    dest_open = False
                    clicked_any_dropdown = True


                # input boxes
                active_input = -1
                if not clicked_any_dropdown:
                    for i, r in enumerate(input_rects):
                        if r.collidepoint(evt.pos):
                            active_input = i
                            break

                #click elsewhere closes dropdowns
                if not clicked_any_dropdown and active_input == -1:
                    dep_open = dest_open = ship_open = False

        if evt.type == KEYDOWN and current_screen == "screen1":
            if active_input != -1:
                if evt.key == K_BACKSPACE:
                    input_texts[active_input] = input_texts[active_input][:-1]
                else:
                    if len(input_texts[active_input]) < 18:
                        input_texts[active_input] += evt.unicode

    if current_screen == "menu":
        screen.blit(menu_bg, (0, 0))

        if logo_img:
            logo_scaled = transform.smoothscale(logo_img, (750, 50))
            logo_rect = logo_scaled.get_rect(center=(WIDTH // 2, 120))
            screen.blit(logo_scaled, logo_rect)
        else:
            title = main_font.render("INTERSTELLER HIGHWAY", True, BLACK)
            screen.blit(title, (160, 120))

        draw_button(btn_mission, "MISSION", GRAY, (230, 230, 230))
        draw_button(btn_instructions, "INSTRUCTIONS", GRAY, (230, 230, 230))
        draw_button(btn_exit, "EXIT", RED, (255, 120, 120), text_col=WHITE)

    elif current_screen == "screen1":
        screen.blit(screen1_bg, (0, 0))
        screen.blit(main_font.render("TAKE OFF THE TRADES", True, WHITE), (240, 15))

        # NEW: back + exit buttons
        draw_button(btn_back, "BACK", GRAY, (230, 230, 230))
        draw_button(btn_exit, "EXIT", RED, (255, 120, 120), text_col=WHITE)

        screen.blit(ui_font.render("Departure Location:", True, WHITE), (70, dep_rect.y + 8))
        screen.blit(ui_font.render("Destination:", True, WHITE), (70, dest_rect.y + 8))
        screen.blit(ui_font.render("Ship selection:", True, WHITE), (70, ship_rect.y + 8))

        #launch button
        draw_button(btn_launch, "LAUNCH", BLUE, (90, 140, 255), text_col=WHITE)

        #input labels + boxes
        for i, r in enumerate(input_rects):
            lbl = ui_font.render(input_labels[i], True, WHITE)
            screen.blit(lbl, (70, r.y + 8))
            draw_input_box(r, input_texts[i], is_active=(active_input == i))

        #bottom planet images
        if planet_imgs.get(dep_selected):
            img = transform.smoothscale(planet_imgs[dep_selected], (90, 90))
            screen.blit(img, (20, HEIGHT - 110))
            screen.blit(ui_font.render(dep_selected, True, WHITE), (120, HEIGHT - 80))

        if planet_imgs.get(dest_selected):
            img = transform.smoothscale(planet_imgs[dest_selected], (90, 90))
            screen.blit(img, (WIDTH - 110, HEIGHT - 110))
            screen.blit(ui_font.render(dest_selected, True, WHITE), (WIDTH - 250, HEIGHT - 80))

        #dropdowns LAST (so they draw above everything)
        #draw all dropdown BASES first (no lists)
        draw_dropdown_box(dep_rect, dep_selected, dep_open, planet_options, draw_list=False)
        draw_dropdown_box(dest_rect, dest_selected, dest_open, planet_options, draw_list=False)
        draw_dropdown_box(ship_rect, ship_selected, ship_open, ship_options, draw_list=False)

        #draw ONLY the open dropdown list LAST so nothing draws on top of it
        if dep_open:
            draw_dropdown_box(dep_rect, dep_selected, dep_open, planet_options, draw_list=True)
        elif dest_open:
            draw_dropdown_box(dest_rect, dest_selected, dest_open, planet_options, draw_list=True)
        elif ship_open:
            draw_dropdown_box(ship_rect, ship_selected, ship_open, ship_options, draw_list=True)




    elif current_screen == "screen2":
        screen.blit(screen2_bg, (0, 0))

        draw_button(btn_back, "BACK", GRAY, (230, 230, 230))#back button
        draw_button(btn_exit, "EXIT", RED, (255, 120, 120), text_col=WHITE)#exit button

        #dark glass panel to make text readable
        panel = Rect(60, 90, 680, 420)
        panel_surf = Surface((panel.w, panel.h), SRCALPHA)
        panel_surf.fill((0, 0, 0, 150))
        screen.blit(panel_surf, (panel.x, panel.y))
        draw.rect(screen, (255, 255, 255), panel, 2, border_radius=14)

        # header
        header = main_font.render("INSTRUCTIONS", True, WHITE)
        screen.blit(header, header.get_rect(center=(WIDTH // 2, 125)))

        y = 165
        lines = [
            "The Goal of this platform is to build a smart scallable route ",
            "planning logistics platform that will serve as the foundatoin of ",
            "a safer, and more reliable space trade infrastructure.",
            "",
            "1) Pick departure + destination",
            "2) Pick a ship and enter payload mass",
            "3) Click LAUNCH to run the trade sim",
            "",
            "Use BACK to return",
            "",
            "Press F11 to toggle fullscreen"
        ]
        for line in lines:
            if line == "":
                y += 14
            else:
                screen.blit(ui_font.render(line, True, WHITE), (110, y))
                y += 34

    elif current_screen == "screen3":
        screen.fill((10, 10, 20))

        draw_button(btn_back, "BACK", GRAY, (230, 230, 230))
        draw_button(btn_exit, "EXIT", RED, (255, 120, 120), text_col=WHITE)

        #sun
        draw.circle(screen, YELLOW, sun_pos, 22)

        #orbits on the screen
        for p in planet_options:
            r, _ = orbit_data.get(p, (120, 1.0))
            draw_orbit(r)

        #planets on the orbits
        pos_map = {}
        for p in planet_options:
            px, py = planet_xy(p, sim_time)
            pos_map[p] = (px, py)

            if planet_imgs.get(p):
                size = planet_sizes.get(p, 20)
                planet_img = transform.smoothscale(planet_imgs[p], (size, size))
                img_rect = planet_img.get_rect(center=(px, py))
                screen.blit(planet_img, img_rect)
                if p == travel_from:
                    draw.circle(screen, BLUE, (px,py), 13, 3)
                elif p == travel_to:
                    draw.circle(screen, RED, (px,py), 13, 3)
            else:
                if p == travel_from:
                    draw.circle(screen, BLUE, (px, py), 10)
                elif p == travel_to:
                    draw.circle(screen, RED, (px, py), 10)
                else:
                    draw.circle(screen, (180, 180, 180), (px, py), 7)

        #ship travel
        if travel_active and travel_from in pos_map and travel_to in pos_map:
            a = pos_map[travel_from]
            b = pos_map[travel_to]

            speed = 0.1
            speed *= 1.0 / (1.0 + max(0.0, travel_payload) / 2000.0)

            travel_t += dt * speed
            if travel_t >= 1.0:
                travel_t = 1.0
                travel_active = False
                exhaust_trail = []  # Clear trail when arrived

            sx = int(a[0] + (b[0] - a[0]) * travel_t)
            sy = int(a[1] + (b[1] - a[1]) * travel_t)

            # Add current position to exhaust trail
            exhaust_trail.append((sx, sy))
            
            # Keep only last 30 positions for trail
            if len(exhaust_trail) > 30:
                exhaust_trail.pop(0)
            
            # Draw fading exhaust trail
            for i, (tx, ty) in enumerate(exhaust_trail):
                # Calculate fade: older positions are more transparent
                alpha = int(255 * (i / len(exhaust_trail)))  # 0 to 255
                size = int(3 + 4 * (i / len(exhaust_trail)))  # Growing size
                
                # Create semi-transparent surface for exhaust
                exhaust_surf = Surface((size * 2, size * 2), SRCALPHA)
                draw.circle(exhaust_surf, (255, 150, 50, alpha), (size, size), size)  # Orange glow
                screen.blit(exhaust_surf, (tx - size, ty - size))

            if len(exhaust_trail) >= 2:
                # Use last two positions to determine direction
                prev_x, prev_y = exhaust_trail[-2]
                curr_x, curr_y = exhaust_trail[-1]
                dx = curr_x - prev_x
                dy = curr_y - prev_y
                heading_deg = degrees(atan2(-dy, dx)) - 90
            else:
                # Fallback: use destination
                dx = b[0] - a[0]
                dy = b[1] - a[1]
                heading_deg = degrees(atan2(-dy, dx)) - 90

            # Draw rocket image (or fallback circle)
            if rocket_img:
                rotated_rocket = transform.rotate(rocket_img, heading_deg)
                rocket_rect = rotated_rocket.get_rect(center=(sx, sy))
                screen.blit(rotated_rocket, rocket_rect)
            else:
                draw.circle(screen, (120, 255, 200), (sx, sy), 8)

        #UI overlay
        screen.blit(main_font.render("TRADE SIMULATION", True, WHITE), (240, 15))
        screen.blit(ui_font.render(f"From: {travel_from}   To: {travel_to}", True, WHITE), (20, 70))
        screen.blit(ui_font.render(f"Ship: {travel_ship_name}", True, WHITE), (20, 100))
        screen.blit(ui_font.render(f"Launch Window: {travel_window if travel_window else '(none)'}", True, WHITE), (20, 130))
        screen.blit(ui_font.render(f"Payload: {travel_payload:.1f} kg", True, WHITE), (20, 160))

        status = "ARRIVED at the DESTINATION" if not travel_active else "En route..."
        screen.blit(ui_font.render(f"Status: {status}", True, WHITE), (20, 200))
        screen.blit(ui_font.render("Use BACK to return", True, WHITE), (20, 560))

    #mouse coordinates
    screen.blit(coord_font.render(f"({mx}, {my})", True, WHITE if current_screen == "screen3" else BLACK), (10, 10))

    display.flip()

quit()

'''Sources used: 
  1.  https://www.youtube.com/watch?v=6bHwWFOz4Ww
  2.  https://trinket.io/glowscript/63cb9fd49d
  3.  https://www.youtube.com/watch?v=yRKALsvGAGE
  4.  https://stackoverflow.com/questions/45441885/how-can-i-create-a-dropdown-menu-from-a-list-in-tkinter
  5.  https://www.youtube.com/watch?v=WTLPmUHTPqo
  6.  https://stackoverflow.com/questions/19877900/tips-on-adding-creating-a-drop-down-selection-box-in-pygame
  7.  https://www.youtube.com/watch?v=eJc6fEX-0r0
  8.  
'''