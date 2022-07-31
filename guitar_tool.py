from sys import exit, argv
from os import path
from random import randint
from json import dump, load
from my_color import myColor
import pygame as pg

def get_grabbing_cursor() -> pg.cursors.Cursor:
    cursor = (
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "        XX XX XX X      ",
    "       X..X..X..X.X     ",
    "      XX..X..X..X..X    ",
    "     X.X..X..X..X..X    ",
    "    X..X..X..X..X..X    ",
    "    X..X..X..X..X..X    ",
    "    X..X...........X    ",
    "    X..X...........X    ",
    "    X..X...........X    ",
    "    X..............X    ",
    "    X..............X    ",
    "     X.............X    ",
    "     X............X     ",
    "      X...........X     ",
    "       X.........X      ",
    "        X........X      ",
    "         XXXXXXXX       ",
    "                        ",
    "                        "
    )
    return pg.cursors.Cursor((24, 24), (12, 12), *pg.cursors.compile(cursor))

def get_percent_selector(cursor_x):
    if cursor_x <= 15:
        return 0
    if cursor_x >= 415:
        return 100
    return (cursor_x - 15) / 4

def get_highlight_gray(background, ref, contrast):
    return (ref + contrast, ref - contrast)[background - ref > 0]

def get_gray_average(gray1, gray2):
    diff = abs(gray1 - gray2) / 2
    return (gray1 + diff, gray2 + diff)[gray2 < gray1]

def get_color_list() -> list[tuple[int, int, int]]:
    color_list = []
    color = myColor((255, 0, 0))
    for i in range(361):
        color.set_hue(i)
        color_list.append(color.get_rgb_tuple())
    return color_list

def get_font_dictionnary() -> dict[str, pg.font.Font]:
    font_file = path.join(path.join(path.dirname(path.abspath(argv[0])), 'assets'), "font.ttf")
    font_dict = {
        "Title": pg.font.Font(font_file, 30),
        "Subtitle": pg.font.Font(font_file, 22),
        "Note Alpha": pg.font.Font(font_file, 20),
        "Note Syllab": pg.font.Font(font_file, 16),
        "SharpNFlat": pg.font.Font(font_file, 25),
        "Button": pg.font.Font(font_file, 16),
        "String": pg.font.Font(font_file, 25),
        "Play Alpha": pg.font.Font(font_file, 190),
        "Play Syllab": pg.font.Font(font_file, 120),
        "Next Alpha": pg.font.Font(font_file, 140),
        "Next Syllab": pg.font.Font(font_file, 70),
    }
    return font_dict

def bpm_into_ms(bpm):
    return int(60000 / bpm)

def swap_alpha_and_syllabic(list : list[str]):
    alpha = ["C", "D", "E", "F", "G", "A", "B", "C#", "D#", "F#", "G#", "A#", "Db", "Eb", "Gb", "Ab", "Bb"]
    syllabic = ["Do", "Ré", "Mi", "Fa", "Sol", "La", "Si", "Do#", "Ré#", "Fa#", "Sol#", "La#", "Réb", "Mib", "Solb", "Lab", "Sib"]
    i = 0
    for note in list:
        if note in alpha:
            list[i] = syllabic[alpha.index(note)]
        elif note in syllabic:
            list[i] = alpha[syllabic.index(note)]
        i += 1

def swap_sharp_and_flat(list : list[str], alphabetical : bool):
    if alphabetical:
        sharps = ["A#", "C#", "D#", "F#", "G#"]
        flats = ["Bb", "Db", "Eb", "Gb", "Ab"]
    else:
        sharps = ["Do#", "Ré#", "Fa#", "Sol#", "La#"]
        flats = ["Réb", "Mib", "Solb", "Lab", "Sib"]
    i = 0
    for note in list:
        if note in sharps:
            list[i] = flats[sharps.index(note)]
        elif note in flats:
            list[i] = sharps[flats.index(note)]
        i += 1

class RandomNote():
    def __init__(self):
        self.notes = []
        self.string_number = 0
        self.random_list = []
        self.inc = 0
        self.ticks_count = 0
        self.rand_note_to_play = None
        self.rand_next_note = None
    
    def get_note_to_play(self):
        return self.rand_note_to_play
    
    def get_next_note(self):
        return self.rand_next_note
    
    def new_tick(self):
        if self.rand_note_to_play != None:
            self.ticks_count += 1
            if self.ticks_count < self.string_number:
                return
        self.ticks_count = 0
        self.inc += 1
        self.rand_note_to_play = self.rand_next_note
        if self.inc < len(self.random_list):
            self.rand_next_note = self.random_list[self.inc]
        else:
            self.inc = 0
            self.set_random_list()
            self.rand_next_note = self.random_list[0]

    def init_generator(self, notes, string_number):
        self.notes = notes
        self.string_number = string_number
        self.set_random_list()
        self.inc = 0
        self.ticks_count = 0
        self.rand_note_to_play = None
        self.rand_next_note = self.random_list[0]
    
    def set_random_list(self):
        self.random_list.clear()
        stock = self.notes.copy()
        length = len(stock)
        while length > 0:
            rand = randint(0, length - 1)
            self.random_list.append(stock[rand])
            stock.pop(rand)
            length -= 1

class SoundManager():
    def __init__(self):
        self.click = pg.mixer.Sound(path.join(path.join(path.dirname(path.abspath(argv[0])), 'assets'), 'click_sound.wav'))
    
    def play(self):
        self.click.play()

class GuitarTool():
    def __init__(self, window : pg.Surface):
        self.window = window
        self.selected_notes : list[str] = []
        self.bpm = 0
        self.string_number = 0
        self.sharps_selected = True
        self.alphabetical_selected = True
        self.color_list = get_color_list()
        self.color_reference = None
        self.color_hue = 0
        self.color_saturation = 0
        self.color_lightness = 0
        self.background_color = None
        self.primary_color = None
        self.secondary_color = None
        self.tertiary_color = None
        self.quaternary_color = None
        self.color_theme = None
        self.color_mode = None
        self.retrieve_user_values()
        self.sound_manager = SoundManager()
        self.note_generator = RandomNote()
        self.tick_event = pg.event.custom_type()
        self.cant_play_event = pg.event.custom_type()
        self.cant_play_event_inc = 0
        self.dim_bpm_event = pg.event.custom_type()
        self.aug_bpm_event = pg.event.custom_type()
        self.bpm_event_frequency = 0
        self.play_button = pg.transform.scale(pg.image.load(path.join(path.join(path.dirname(path.abspath(argv[0])), 'assets'), "play_button.png")), (80, 80))
        self.pause_button = pg.transform.scale(pg.image.load(path.join(path.join(path.dirname(path.abspath(argv[0])), 'assets'), "pause_button.png")), (80, 80))
        self.button_rect = pg.Rect(395, 345, 80, 80)
        self.opt_icon = pg.image.load(path.join(path.join(path.dirname(path.abspath(argv[0])), 'assets'), "options_icon.png"))
        self.options_button = None
        self.close_button = pg.transform.scale(pg.image.load(path.join(path.join(path.dirname(path.abspath(argv[0])), 'assets'), "close_icon.png")), (50, 50))
        self.opions_rect = pg.Rect(440, 10, 50, 50)
        self.options_menu_on = False
        self.bar = pg.Rect(25, 445, 450, 20)
        self.bar_hitbox = pg.Rect(25, 435, 450, 40)
        self.bpm_handler = pg.Rect(25, 435, 40, 40)
        self.update_bpm_handler()
        self.font_dict = get_font_dictionnary()
        self.playing = False
        self.bpm_handler_used = False
        self.selector_used = False
        self.notes_list : list[pg.Rect] = []
        self.notes_buttons : list[pg.Rect] = []
        self.strings_list : list[pg.Rect] = []
        self.themes_list : list[pg.Rect] = []
        self.selectors_list : list[pg.Rect] = []
        self.modes_list : list[pg.Rect] = []
        self.bpm_buttons : list[pg.Rect] = []
        self.__init_notes_and_strings__()
        self.note_to_play = None
        self.next_note = None
        self.define_colors()
        self.hue_selector = None
        self.saturation_selector = None
        self.lightness_selector = None
        self.update_color_selectors()
        self.GRABBING_CURSOR_HAND = get_grabbing_cursor()
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
    
    def __init_notes_and_strings__(self):
        x = 10
        for i in range(7):
            self.notes_list.append(pg.Rect(x, 110, 36, 36))
            x += 60
        x = 10
        for i in range(5):
            self.notes_list.append(pg.Rect(x, 155, 36, 36))
            x += 60
        for i in range(2):
            self.notes_list.append(pg.Rect(x - 2, 153, 40, 40))
            x += 60
        y = 110
        for i in range(4):
            self.notes_buttons.append(pg.Rect(420, y, 70, 20))
            y += 30
        x = 20
        for i in range(2):
            self.notes_buttons.append(pg.Rect(x, 200, 180, 30))
            x += 195
        x = 20
        for i in range(7):
            self.strings_list.append(pg.Rect(x, 275, 40, 40))
            x += 70
        x = 25
        for i in range(2):
            self.bpm_buttons.append(pg.Rect(x, 355, 60, 60))
            x += 230
    
    def handle_event(self, event : pg.event.Event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.opions_rect.collidepoint(event.pos):
                self.options_menu_on = (True, False)[self.options_menu_on==True]
                return
        if event.type == pg.MOUSEMOTION:
            self.handle_cursor(event.pos, event.buttons)
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            self.save_user_values()
        if self.options_menu_on:
            self.handle_menu_event(event)
        elif self.playing:
            self.handle_play_event(event)
        else:
            self.handle_app_event(event)
 
    def handle_app_event(self, event : pg.event.Event):
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.bpm_event_frequency = 0
            self.bpm_handler_used = False
            pg.time.set_timer(self.dim_bpm_event, 0)
            pg.time.set_timer(self.aug_bpm_event, 0)
            self.handle_cursor(event.pos, (0, 0, 0))
            return
        if event.type == self.aug_bpm_event and self.bpm_event_frequency != 0:
            self.bpm = (self.bpm + 1, 210)[self.bpm + 1 > 210]
            self.bpm_handler.x = (self.bpm_handler.x + 2, 435)[self.bpm_handler.x + 2 > 435]
            if self.bpm == 210:
                self.bpm_event_frequency = 0
                pg.time.set_timer(self.aug_bpm_event, 0)
            else:
                self.bpm_event_frequency = (round(self.bpm_event_frequency / 2), 10)[self.bpm_event_frequency / 2 < 10]
                pg.time.set_timer(self.aug_bpm_event, self.bpm_event_frequency)
            return
        if event.type == self.dim_bpm_event and self.bpm_event_frequency != 0:
            self.bpm = (self.bpm - 1, 5)[self.bpm - 1 < 5]
            self.bpm_handler.x = (self.bpm_handler.x - 2, 25)[self.bpm_handler.x - 2 < 25]
            if self.bpm == 5:
                self.bpm_event_frequency = 0
                pg.time.set_timer(self.dim_bpm_event, 0)
            else:
                self.bpm_event_frequency = (round(self.bpm_event_frequency / 2), 10)[self.bpm_event_frequency / 2 < 10]
                pg.time.set_timer(self.dim_bpm_event, self.bpm_event_frequency)
            return
        if event.type == self.cant_play_event:
            self.cant_play_event_inc -= 1
            if self.cant_play_event_inc == 0:
                pg.time.set_timer(self.cant_play_event, 0)
            return
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.bpm_buttons[0].collidepoint(event.pos):
                self.bpm = (self.bpm - 1, 5)[self.bpm - 1 < 5]
                self.bpm_handler.x = (self.bpm_handler.x - 2, 25)[self.bpm_handler.x - 2 < 25]
                self.bpm_event_frequency = 500
                pg.time.set_timer(self.dim_bpm_event, 500)
                return
            if self.bpm_buttons[1].collidepoint(event.pos):
                self.bpm = (self.bpm + 1, 210)[self.bpm + 1 > 210]
                self.bpm_handler.x = (self.bpm_handler.x + 2, 435)[self.bpm_handler.x + 2 > 435]
                self.bpm_event_frequency = 500
                pg.time.set_timer(self.aug_bpm_event, 500)
                return
            if self.button_rect.collidepoint(event.pos):
                self.play_pause_handler()
                return
            if self.bar_hitbox.collidepoint(event.pos):
                pg.mouse.set_cursor(self.GRABBING_CURSOR_HAND)
                x = event.pos[0] - 20
                if x < 25:
                    x = 25
                elif x > 435:
                    x = 435
                self.bpm_handler.x = x
                self.bpm_handler_used = True
                self.update_bpm()
                return
            i = 0
            for note in self.notes_list:
                if note.collidepoint(event.pos):
                    self.handle_notes_selection(i)
                    return
                i += 1
            i = 0
            for button in self.notes_buttons:
                if button.collidepoint(event.pos):
                    if i == 0 and self.sharps_selected and self.alphabetical_selected:
                        self.selected_notes = ["A", "B", "C", "D", "E", "F", "G", "A#", "C#", "D#", "F#", "G#"]
                    elif i == 0 and self.sharps_selected == False and self.alphabetical_selected:
                        self.selected_notes = ["A", "B", "C", "D", "E", "F", "G", "Bb", "Db", "Eb", "Gb", "Ab"]
                    elif i == 0 and self.sharps_selected and self.alphabetical_selected == False:
                        self.selected_notes = ["Do", "Ré", "Mi", "Fa", "Sol", "La", "Si", "Do#", "Ré#", "Fa#", "Sol#", "La#"]
                    elif i == 0:
                        self.selected_notes = ["Do", "Ré", "Mi", "Fa", "Sol", "La", "Si", "Réb", "Mib", "Solb", "Lab", "Sib"]
                    elif i == 1 and self.alphabetical_selected:
                        self.selected_notes = ["A", "B", "C", "D", "E", "F", "G"]
                    elif i == 1:
                        self.selected_notes = ["Do", "Ré", "Mi", "Fa", "Sol", "La", "Si"]
                    elif i == 2 and self.sharps_selected and self.alphabetical_selected:
                        self.selected_notes = ["A#", "C#", "D#", "F#", "G#"]
                    elif i == 2 and self.sharps_selected == False and self.alphabetical_selected:
                        self.selected_notes = ["Bb", "Db", "Eb", "Gb", "Ab"]
                    elif i == 2 and self.sharps_selected and self.alphabetical_selected == False:
                        self.selected_notes = ["Do#", "Ré#", "Fa#", "Sol#", "La#"]
                    elif i == 2:
                        self.selected_notes = ["Réb", "Mib", "Solb", "Lab", "Sib"]
                    elif i == 3:
                        self.selected_notes = []
                    elif i == 4 and self.alphabetical_selected != True:
                        self.alphabetical_selected = True
                        swap_alpha_and_syllabic(self.selected_notes)
                    elif i == 5 and self.alphabetical_selected:
                        self.alphabetical_selected = False
                        swap_alpha_and_syllabic(self.selected_notes)
                    return
                i += 1
            i = 1
            for string in self.strings_list:
                if string.collidepoint(event.pos):
                    self.string_number = i
                    return
                i += 1
        if self.bpm_handler_used and event.type == pg.MOUSEMOTION and event.buttons == (1, 0, 0):
            x = event.pos[0] - 20
            if x < 25:
                x = 25
            elif x > 435:
                x = 435
            self.bpm_handler.x = x
            self.update_bpm()
            return
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE :
                self.play_pause_handler()
                return
    
    def handle_menu_event(self, event : pg.event.Event):
        selector_nb = 0
        themes_list = [
            "Complementary", "Analogous 1", "Tetradic 1", "Triadic 1", "Comp-analogous 1", 
            "Analogous 2", "Tetradic 2", "Triadic 2", "Comp-analogous 2"
            ]
        theme_inc = 0
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.selector_used = False
            self.handle_cursor(event.pos, (0, 0, 0))
            return
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.modes_list[0].collidepoint(event.pos):
                self.color_mode = "light"
                self.define_colors()
                return
            if self.modes_list[1].collidepoint(event.pos):
                self.color_mode = "dark"
                self.define_colors()
                return
            for selector in self.selectors_list:
                if selector.collidepoint(event.pos):
                    if selector_nb == 0:
                        self.color_hue = round(get_percent_selector(event.pos[0]) * 3.6)
                        self.color_reference = self.color_list[self.color_hue]
                        self.define_colors()
                        self.update_color_selectors()
                        self.selector_used = 1
                        pg.mouse.set_cursor(self.GRABBING_CURSOR_HAND)
                    elif selector_nb == 1:
                        self.color_saturation = round(get_percent_selector(event.pos[0]))
                        self.define_colors()
                        self.selector_used = 2
                        pg.mouse.set_cursor(self.GRABBING_CURSOR_HAND)
                    elif selector_nb == 2:
                        self.color_lightness = round(get_percent_selector(event.pos[0]))
                        self.define_colors()
                        self.selector_used = 3
                        pg.mouse.set_cursor(self.GRABBING_CURSOR_HAND)
                    return
                selector_nb += 1
            for theme in self.themes_list:
                if theme.collidepoint(event.pos):
                    self.color_theme = themes_list[theme_inc]
                    self.define_colors()
                    return
                theme_inc += 1
        if self.selector_used != False and event.type == pg.MOUSEMOTION and event.buttons == (1, 0, 0):
            if self.selector_used == 1:
                self.color_hue = round(get_percent_selector(event.pos[0]) * 3.6)
                self.color_reference = self.color_list[self.color_hue]
                self.define_colors()
                self.update_color_selectors()
            elif self.selector_used == 2:
                self.color_saturation = round(get_percent_selector(event.pos[0]))
                self.define_colors()
            elif self.selector_used == 3:
                self.color_lightness = round(get_percent_selector(event.pos[0]))
                self.define_colors()
            return

    def handle_play_event(self, event : pg.event.Event):
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.bpm_event_frequency = 0
            self.bpm_handler_used = False
            pg.time.set_timer(self.dim_bpm_event, 0)
            pg.time.set_timer(self.aug_bpm_event, 0)
            pg.time.set_timer(self.tick_event, bpm_into_ms(self.bpm))
            self.handle_cursor(event.pos, (0, 0, 0))
            return
        if event.type == self.aug_bpm_event and self.bpm_event_frequency != 0:
            self.bpm = (self.bpm + 1, 210)[self.bpm + 1 > 210]
            self.bpm_handler.x = (self.bpm_handler.x + 2, 435)[self.bpm_handler.x + 2 > 435]
            if self.bpm == 210:
                self.bpm_event_frequency = 0
                pg.time.set_timer(self.aug_bpm_event, 0)
            else:
                self.bpm_event_frequency = (round(self.bpm_event_frequency / 2), 10)[self.bpm_event_frequency / 2 < 10]
                pg.time.set_timer(self.aug_bpm_event, self.bpm_event_frequency)
            return
        if event.type == self.dim_bpm_event and self.bpm_event_frequency != 0:
            self.bpm = (self.bpm - 1, 5)[self.bpm - 1 < 5]
            self.bpm_handler.x = (self.bpm_handler.x - 2, 25)[self.bpm_handler.x - 2 < 25]
            if self.bpm == 5:
                self.bpm_event_frequency = 0
                pg.time.set_timer(self.dim_bpm_event, 0)
            else:
                self.bpm_event_frequency = (round(self.bpm_event_frequency / 2), 10)[self.bpm_event_frequency / 2 < 10]
                pg.time.set_timer(self.dim_bpm_event, self.bpm_event_frequency)
            return
        if event.type == self.tick_event:
            self.new_tick()
            return
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.bpm_buttons[0].collidepoint(event.pos):
                self.bpm = (self.bpm - 1, 5)[self.bpm - 1 < 5]
                self.bpm_handler.x = (self.bpm_handler.x - 2, 25)[self.bpm_handler.x - 2 < 25]
                self.bpm_event_frequency = 500
                pg.time.set_timer(self.tick_event, 0)
                pg.time.set_timer(self.dim_bpm_event, 500)
                return
            if self.bpm_buttons[1].collidepoint(event.pos):
                self.bpm = (self.bpm + 1, 210)[self.bpm + 1 > 210]
                self.bpm_handler.x = (self.bpm_handler.x + 2, 435)[self.bpm_handler.x + 2 > 435]
                self.bpm_event_frequency = 500
                pg.time.set_timer(self.tick_event, 0)
                pg.time.set_timer(self.aug_bpm_event, 500)
                return
            if self.button_rect.collidepoint(event.pos):
                self.play_pause_handler()
                return
            if self.bar_hitbox.collidepoint(event.pos):
                pg.mouse.set_cursor(self.GRABBING_CURSOR_HAND)
                x = event.pos[0] - 20
                if x < 25:
                    x = 25
                elif x > 435:
                    x = 435
                self.bpm_handler.x = x
                self.bpm_handler_used = True
                self.update_bpm()
                return
        if self.bpm_handler_used and event.type == pg.MOUSEMOTION and event.buttons == (1, 0, 0):
            x = event.pos[0] - 20
            if x < 25:
                x = 25
            elif x > 435:
                x = 435
            self.bpm_handler.x = x
            self.update_bpm()
            return
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE :
                self.play_pause_handler()
                return
    
    def handle_cursor(self, cursor_pos, cursor_buttons):
        if self.bpm_handler_used or self.selector_used != False or cursor_buttons != (0, 0, 0):
            return
        if self.opions_rect.collidepoint(cursor_pos):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
            return
        if self.options_menu_on:
            self.handle_options_cursor(cursor_pos)
            return
        if self.button_rect.collidepoint(cursor_pos):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
            return
        if self.bar_hitbox.collidepoint(cursor_pos):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
            return
        if self.bpm_buttons[0].collidepoint(cursor_pos) or self.bpm_buttons[1].collidepoint(cursor_pos):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
            return
        if self.playing == False:
            self.handle_app_cursor(cursor_pos)
            return
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
    
    def handle_app_cursor(self, cursor_pos):
        for rect in self.notes_list:
            if rect.collidepoint(cursor_pos):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
                return
        for rect in self.notes_buttons:
            if rect.collidepoint(cursor_pos):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
                return
        for rect in self.strings_list:
            if rect.collidepoint(cursor_pos):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
                return
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
    
    def handle_options_cursor(self, cursor_pos):
        for rect in self.themes_list:
            if rect.collidepoint(cursor_pos):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
                return
        for rect in self.selectors_list:
            if rect.collidepoint(cursor_pos):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
                return
        for rect in self.modes_list:
            if rect.collidepoint(cursor_pos):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
                return
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
    
    def handle_notes_selection(self, i):
        if (i == 12 and self.sharps_selected) or (i == 13 and self.sharps_selected == False):
            return
        if i == 12 and self.sharps_selected == False:
            self.sharps_selected = True
            swap_sharp_and_flat(self.selected_notes, self.alphabetical_selected)
            return
        if i == 13 and self.sharps_selected:
            self.sharps_selected = False
            swap_sharp_and_flat(self.selected_notes, self.alphabetical_selected)
            return
        if self.sharps_selected == True and self.alphabetical_selected:
            notes = ["A", "B", "C", "D", "E", "F", "G", "A#", "C#", "D#", "F#", "G#"]
        elif self.sharps_selected == False and self.alphabetical_selected:
            notes = ["A", "B", "C", "D", "E", "F", "G", "Bb", "Db", "Eb", "Gb", "Ab"]
        elif self.sharps_selected == True and self.alphabetical_selected == False:
            notes = ["Do", "Ré", "Mi", "Fa", "Sol", "La", "Si", "Do#", "Ré#", "Fa#", "Sol#", "La#"]
        else:
            notes = ["Do", "Ré", "Mi", "Fa", "Sol", "La", "Si", "Réb", "Mib", "Solb", "Lab", "Sib"]
        if notes[i] in self.selected_notes:
            self.selected_notes.remove(notes[i])
        elif notes[i] not in self.selected_notes:
            self.selected_notes.append(notes[i])
    
    def update(self):
        self.window.fill(self.background_color)
        if self.options_menu_on:
            self.update_options_menu()
            return
        title_background = pg.draw.rect(self.window, self.secondary_color, [10, 5, 400, 60], border_radius=20)
        pg.draw.rect(self.window, self.primary_color, [10, 5, 400, 60], width=10, border_radius=20)
        title = self.font_dict["Title"].render("LEARN NOTES LOCATION", 1, self.primary_color)
        x = (title_background.x + title_background.width / 2) - title.get_width() / 2
        y = (title_background.y + title_background.height / 2) - title.get_height() / 2
        self.window.blit(title, (x, y))
        self.window.blit(self.options_button, self.opions_rect)
        pg.draw.rect(self.window, self.secondary_color, [5, 325, 490, 170], border_radius=10)
        pg.draw.rect(self.window, self.primary_color, [5, 325, 490, 170], width=10, border_radius=10)
        if self.playing == True:
            pg.draw.circle(self.window, self.primary_color, (435, 385), 40)
            self.window.blit(self.pause_button, self.button_rect)
        else:
            pg.draw.circle(self.window, self.primary_color, (435, 385), 45)
            self.window.blit(self.play_button, self.button_rect)
        btn_text = "-"
        for button in self.bpm_buttons:
            pg.draw.rect(self.window, self.primary_color, button, width=10, border_radius=10)
            btn_text = self.font_dict["Next Syllab"].render(btn_text, 1, self.primary_color)
            self.window.blit(btn_text, ((button.x + button.width / 2) - btn_text.get_width() / 2, 322))
            btn_text = "+"
        pg.draw.rect(self.window, self.primary_color, self.bar)
        pg.draw.rect(self.window, self.quaternary_color, self.bar, width=5)
        pg.draw.rect(self.window, self.primary_color, self.bpm_handler)
        pg.draw.rect(self.window, self.quaternary_color, self.bpm_handler, width=6)
        pg.draw.rect(self.window, self.primary_color, [95, 345, 150, 80], width=10, border_radius=20)
        self.update_bpm_text()
        if self.playing == False:
            self.update_config()
        else:
            self.update_playing()
    
    def update_options_menu(self):
        title_background = pg.draw.rect(self.window, self.secondary_color, [10, 10, 400, 60], border_radius=20)
        pg.draw.rect(self.window, self.primary_color, [10, 10, 400, 60], width=10, border_radius=20)
        title = self.font_dict["Title"].render("CUSTOMIZE GUITAR TOOL", 1, self.primary_color)
        x = (title_background.x + title_background.width / 2) - title.get_width() / 2
        y = (title_background.y + title_background.height / 2) - title.get_height() / 2
        self.window.blit(title, (x, y))
        self.window.blit(self.close_button, self.opions_rect)
        self.display_color_selectors()
        self.display_themes_selector()
    
    def display_color_selectors(self):
        selectors_empty = False
        if self.selectors_list == []:
            selectors_empty = True
        rect_color = ((0, 0, 0), (255, 255, 255))[self.color_mode == "dark"]
        text = self.font_dict["Button"].render("Primary", 1, self.tertiary_color)
        self.window.blit(text, (15, 100))
        text = self.font_dict["Button"].render("color :", 1, self.tertiary_color)
        self.window.blit(text, (15, 120))
        pg.draw.rect(self.window, rect_color, [79, 94, 82, 82])
        pg.draw.rect(self.window, self.primary_color, [80, 95, 80, 80])
        text = self.font_dict["Button"].render("Secondary", 1, self.tertiary_color)
        self.window.blit(text, (175, 100))
        text = self.font_dict["Button"].render("color :", 1, self.tertiary_color)
        self.window.blit(text, (175, 120))
        pg.draw.rect(self.window, rect_color, [259, 94, 82, 82])
        pg.draw.rect(self.window, self.secondary_color, [260, 95, 80, 80])
        if self.color_mode == "light":
            pg.draw.rect(self.window, self.primary_color, [370, 100, 100, 30])
            text = self.font_dict["Button"].render("Light mode", 1, self.secondary_color)
            mode1 = self.window.blit(text, (380, 100))
            text = self.font_dict["Button"].render("Dark mode", 1, self.tertiary_color)
            mode2 = self.window.blit(text, (380, 140))
        else:
            pg.draw.rect(self.window, self.primary_color, [370, 140, 100, 30])
            text = self.font_dict["Button"].render("Light mode", 1, self.tertiary_color)
            mode1 = self.window.blit(text, (380, 100))
            text = self.font_dict["Button"].render("Dark mode", 1, self.secondary_color)
            mode2 = self.window.blit(text, (380, 140))
        if selectors_empty:
                self.modes_list.append(mode1)
                self.modes_list.append(mode2)
        pg.draw.rect(self.window, rect_color, [14, 199, 402, 22])
        pg.draw.rect(self.window, rect_color, [14, 239, 402, 22])
        pg.draw.rect(self.window, rect_color, [14, 279, 402, 22])
        selector1 = self.window.blit(self.hue_selector, (15, 200))
        selector2 = self.window.blit(self.saturation_selector, (15, 240))
        selector3 = self.window.blit(self.lightness_selector, (15, 280))
        if selectors_empty:
            self.selectors_list.append(selector1)
            self.selectors_list.append(selector2)
            self.selectors_list.append(selector3)
        x = round(self.color_hue / 3.6 * 4) + 15
        y = 198
        pg.draw.polygon(self.window, self.primary_color, [(x, y), (x - 5, y - 10), (x + 5, y - 10)])
        pg.draw.polygon(self.window, rect_color, [(x, y), (x - 5, y - 10), (x + 5, y - 10)], width=1)
        x = self.color_saturation * 4 + 15
        y = 238
        pg.draw.polygon(self.window, self.primary_color, [(x, y), (x - 5, y - 10), (x + 5, y - 10)])
        pg.draw.polygon(self.window, rect_color, [(x, y), (x - 5, y - 10), (x + 5, y - 10)], width=1)
        x = self.color_lightness * 4 + 15
        y = 278
        pg.draw.polygon(self.window, self.primary_color, [(x, y), (x - 5, y - 10), (x + 5, y - 10)])
        pg.draw.polygon(self.window, rect_color, [(x, y), (x - 5, y - 10), (x + 5, y - 10)], width=1)
        text = self.font_dict["Title"].render(str(self.color_hue), 1, self.tertiary_color)
        self.window.blit(text, (430, 185))
        text = self.font_dict["Title"].render(str(self.color_saturation), 1, self.tertiary_color)
        self.window.blit(text, (430, 225))
        text = self.font_dict["Title"].render(str(self.color_lightness), 1, self.tertiary_color)
        self.window.blit(text, (430, 265))
    
    def display_themes_selector(self):
        themes_empty = False
        if self.themes_list == []:
            themes_empty = True
        rect_color = ((0, 0, 0), (255, 255, 255))[self.color_mode == "dark"]
        pg.draw.rect(self.window, self.secondary_color, [5, 325, 490, 170], border_radius=10)
        pg.draw.rect(self.window, self.primary_color, [5, 325, 490, 170], width=10, border_radius=10)
        title = self.font_dict["Title"].render("THEMES", 1, self.primary_color)
        self.window.blit(title, (370, 325))
        themes_list = [
            "Complementary:+/-180", "Analogous 1:+30", "Tetradic 1:+90", "Triadic 1:+135", "Comp-analogous 1:+150", 
            "Analogous 2:-30", "Tetradic 2:-90", "Triadic 2:-135", "Comp-analogous 2:-150"
            ]
        x = 50
        y = 338
        for theme in themes_list:
            sep = theme.find(':')
            theme_rect = pg.draw.rect(self.window, rect_color, [x - 30, y, 25, 25], width=1)
            if theme[:theme.find(':')] == self.color_theme:
                pg.draw.line(self.window, rect_color, (x - 25, y + 5), (x - 10, y + 20), width=4)
                pg.draw.line(self.window, rect_color, (x - 10, y + 5), (x - 25, y + 20), width=4)
            if themes_empty:
                self.themes_list.append(theme_rect)
            text = self.font_dict["Button"].render(theme[:sep], 1, self.primary_color)
            self.window.blit(text, (x, y))
            text = self.font_dict["Button"].render(theme[sep+1:], 1, self.primary_color)
            self.window.blit(text, (x + 150, y))
            y += 30
            if y > 458:
                x = 300
                y = 368
    
    def update_playing(self):
        pg.draw.line(self.window, self.primary_color, (250, 80), (250, 310), width=10)
        text = self.font_dict["Subtitle"].render("Next note :", 1, self.tertiary_color)
        self.window.blit(text, (375 - text.get_width() / 2, 80))
        if self.alphabetical_selected:
            text = self.font_dict["Next Alpha"].render(self.next_note, 1, self.tertiary_color)
        else:
            text = self.font_dict["Next Syllab"].render(self.next_note, 1, self.tertiary_color)
        self.window.blit(text, (375 - text.get_width() / 2, 212 - text.get_height() / 2))
        if self.note_to_play == None:
            return
        if self.alphabetical_selected:
            text = self.font_dict["Play Alpha"].render(self.note_to_play, 1, self.primary_color)
        else:
            text = self.font_dict["Play Syllab"].render(self.note_to_play, 1, self.primary_color)
        self.window.blit(text, (125 - text.get_width() / 2, 195 - text.get_height() / 2))
    
    def update_config(self):
        if self.sharps_selected and self.alphabetical_selected:
            notes = ["A", "B", "C", "D", "E", "F", "G", "A#", "C#", "D#", "F#", "G#", "#", "b"]
        elif self.sharps_selected == False and self.alphabetical_selected:
            notes = ["A", "B", "C", "D", "E", "F", "G", "Bb", "Db", "Eb", "Gb", "Ab", "#", "b"]
        elif self.sharps_selected == True and self.alphabetical_selected == False:
            notes = ["Do", "Ré", "Mi", "Fa", "Sol", "La", "Si", "Do#", "Ré#", "Fa#", "Sol#", "La#", "#", "b"]
        else:
            notes = ["Do", "Ré", "Mi", "Fa", "Sol", "La", "Si", "Réb", "Mib", "Solb", "Lab", "Sib", "#", "b"]
        text = self.font_dict["Subtitle"].render("Note(s) to practice with:", 1, self.tertiary_color)
        self.window.blit(text, (20, 70))
        i = 0
        for note in self.notes_list:
            pg.draw.rect(self.window, self.secondary_color, note, border_radius=5)
            if notes[i] in self.selected_notes:
                border_rect = [note.x - 3, note.y - 3, note.height + 6, note.width + 6]
                pg.draw.rect(self.window, self.primary_color, border_rect, width=3, border_radius=10)
            elif i < 12 and self.cant_play_event_inc != 0 and self.cant_play_event_inc % 2 == 0:
                border_rect = [note.x - 5, note.y - 5, note.height + 10, note.width + 10]
                pg.draw.rect(self.window, (204, 0 , 0), border_rect, width=5, border_radius=10)
            if i < 12:
                if self.alphabetical_selected:
                    text = self.font_dict["Note Alpha"].render(notes[i], 1, self.primary_color)
                else:
                    text = self.font_dict["Note Syllab"].render(notes[i], 1, self.primary_color)
            else:
                text = self.font_dict["SharpNFlat"].render(notes[i], 1, self.primary_color)
                if i == 12 and self.sharps_selected:
                    pg.draw.rect(self.window, self.primary_color, note, width=6, border_radius=5)
                if i == 13 and self.sharps_selected == False:
                    pg.draw.rect(self.window, self.primary_color, note, width=6, border_radius=5)
            x = (note.x + note.width / 2) - text.get_width() / 2
            y = (note.y + note.height / 2) - text.get_height() / 2
            self.window.blit(text, (x, y))
            i += 1
        button_texts = ["all", "naturals", "sharps", "clear", "A B C Notation", "Do Ré Mi Notation"]
        if self.sharps_selected == False:
            button_texts[2] = "flats"
        i = 0
        for button in self.notes_buttons:
            pg.draw.rect(self.window, self.secondary_color, button, border_radius=5)
            if self.alphabetical_selected and i == 4:
                pg.draw.rect(self.window, self.primary_color, button, width=5, border_radius=5)
            elif self.alphabetical_selected == False and i == 5:
                pg.draw.rect(self.window, self.primary_color, button, width=5, border_radius=5)
            text = self.font_dict["Button"].render(button_texts[i], 1, self.primary_color)
            x = (button.x + button.width / 2) - text.get_width() / 2
            y = (button.y + button.height / 2) - text.get_height() / 2
            self.window.blit(text, (x, y))
            i += 1
        text = self.font_dict["Subtitle"].render("String(s) to practice on:", 1, self.tertiary_color)
        self.window.blit(text, (20, 235))
        i = 1
        for string in self.strings_list:
            pg.draw.rect(self.window, self.secondary_color, string, border_radius=10)
            if i == self.string_number:
                pg.draw.rect(self.window, self.primary_color, string, width=5, border_radius=10)
            text = self.font_dict["String"].render(str(i), 1, self.primary_color)
            x = (string.x + string.width / 2) - text.get_width() / 2
            y = (string.y + string.height / 2) - text.get_height() / 2
            self.window.blit(text, (x, y))
            i += 1
    
    def update_color_selectors(self):
        stock = pg.Surface((360, 20))
        x = 0
        for color in self.color_list:
            pg.draw.line(stock, color, (x, 0), (x, 20))
            x += 1
        self.hue_selector = pg.transform.scale(stock, (400, 20))
        stock = pg.Surface((100, 20))
        for x in range(101):
            color = myColor(self.color_reference).get_rgb_for_saturation(x)
            pg.draw.line(stock, color, (x, 0), (x, 20))
        self.saturation_selector = pg.transform.scale(stock, (400, 20))
        stock = pg.Surface((100, 20))
        for x in range(101):
            color = myColor(self.color_reference).get_rgb_for_lightness(x)
            pg.draw.line(stock, color, (x, 0), (x, 20))
        self.lightness_selector = pg.transform.scale(stock, (400, 20))
    
    def update_bpm(self):
        self.bpm = int((self.bpm_handler.x - 25) / 2 + 5)
        if self.playing == True:
            pg.time.set_timer(self.tick_event, bpm_into_ms(self.bpm))
    
    def update_bpm_text(self):
        bpm_text = self.font_dict["Title"].render(str(self.bpm), 1, self.primary_color)
        x = 110
        if self.bpm < 100:
            x += 15
        if self.bpm < 10:
            x += 15
        self.window.blit(bpm_text, (x, 360))
        bpm_text = self.font_dict["Title"].render("bpm", 1, self.primary_color)
        self.window.blit(bpm_text, (170, 360))
    
    def update_bpm_handler(self):
        self.bpm_handler.x = (self.bpm - 5) * 2 + 25
    
    def play_pause_handler(self):
        if self.playing == True:
            self.playing = False
            self.note_to_play = None
            self.next_note = None
            pg.time.set_timer(self.tick_event, 0)
        elif len(self.selected_notes) > 0:
            self.note_generator.init_generator(self.selected_notes, self.string_number)
            self.next_note = self.note_generator.get_next_note()
            pg.time.set_timer(self.tick_event, bpm_into_ms(self.bpm))
            self.playing = True
        else:
            pg.time.set_timer(self.cant_play_event, 150)
            self.cant_play_event_inc = 4
    
    def new_tick(self):
        self.note_generator.new_tick()
        self.note_to_play = self.note_generator.get_note_to_play()
        self.next_note = self.note_generator.get_next_note()
        self.sound_manager.play()
    
    def save_user_values(self):
        json_file_path = path.join(path.dirname(path.abspath(argv[0])), 'user_config.json')
        user_values = {
            "Selected Notes": self.selected_notes,
            "bpm": self.bpm,
            "String Number": self.string_number,
            "Sharps Selected": self.sharps_selected,
            "Alphabetical Selected": self.alphabetical_selected,
            "Hue": self.color_hue,
            "Saturation": self.color_saturation,
            "Lightness": self.color_lightness,
            "Theme": self.color_theme,
            "Mode": self.color_mode
        }
        with open(json_file_path, 'w') as file:
            dump(user_values, file, indent=4)
            file.close()
    
    def retrieve_user_values(self):
        json_file_path = path.join(path.dirname(path.abspath(argv[0])), 'user_config.json')
        if path.exists(json_file_path) == False:
            self.selected_notes = ["A", "B", "C", "D", "E", "F", "G"]
            self.bpm = 40
            self.string_number = 1
            self.color_hue = 0
            self.color_saturation = 100
            self.color_lightness = 30
            self.color_theme = "Complementary"
            self.color_mode = "light"
            self.color_reference = self.color_list[self.color_hue]
            return
        with open(json_file_path, 'r') as file:
            user_values = load(file)
            self.selected_notes = user_values["Selected Notes"]
            self.bpm = user_values["bpm"]
            self.string_number = user_values["String Number"]
            self.sharps_selected = user_values["Sharps Selected"]
            self.alphabetical_selected = user_values["Alphabetical Selected"]
            self.color_hue = user_values["Hue"]
            self.color_saturation = user_values["Saturation"]
            self.color_lightness = user_values["Lightness"]
            self.color_theme = user_values["Theme"]
            self.color_mode = user_values["Mode"]
            file.close()
            self.color_reference = self.color_list[self.color_hue]
    
    def define_colors(self):
        ref = myColor(self.color_reference)
        ref.set_saturation(self.color_saturation)
        ref.set_lightness(self.color_lightness)
        ref = ref.get_rgb_tuple()
        self.background_color = myColor(self.color_reference)
        self.primary_color = myColor(ref)
        self.secondary_color = myColor(ref)
        self.tertiary_color = myColor(ref)
        self.quaternary_color = myColor(ref)
        self.define_theme()
        self.background_color.set_saturation(25, True)
        if self.color_mode == "light":
            self.background_color.set_lightness(self.color_lightness / 10 + 75)
        elif self.color_mode == "dark":
            self.background_color.set_lightness(self.color_lightness / 10 + 15)
        self.background_color.set_background_with_contrast(self.primary_color.gray_value(), 60, self.color_mode)
        self.secondary_color.set_lightness_with_contrast(self.primary_color.gray_value(), 80)
        tertiary_gray = get_highlight_gray(self.background_color.gray_value(), self.primary_color.gray_value(), 10)
        quaternary_gray = get_gray_average(self.primary_color.gray_value(), self.secondary_color.gray_value())
        self.tertiary_color.set_lightness_with_gray(tertiary_gray)
        self.quaternary_color.set_lightness_with_gray(quaternary_gray)
        self.update_images_color()
    
    def update_images_color(self):
        self.options_button = pg.transform.scale(self.opt_icon, (50, 50))
        for y in range(50):
            for x in range(50):
                if self.options_button.get_at((x, y)) == (128, 128, 128):
                    self.options_button.set_at((x, y), self.secondary_color)
                elif self.options_button.get_at((x, y))[3] == 0:
                    self.options_button.set_at((x, y), (0, 0, 0, 0))
                else:
                    self.options_button.set_at((x, y), self.tertiary_color)
        for y in range(7, 44):
            for x in range(7, 44):
                if self.close_button.get_at((x, y)) != (0, 0, 0, 0):
                    self.close_button.set_at((x, y), self.tertiary_color)
    
    def define_theme(self):
        if self.color_theme == "Complementary":
            self.background_color.complementary_color(self.color_lightness)
            self.secondary_color.complementary_color(self.color_lightness)
            self.quaternary_color.complementary_color(self.color_lightness)
        elif self.color_theme[:9] == "Analogous":
            self.background_color.analogous_colors(self.color_theme, self.color_lightness)
            self.secondary_color.analogous_colors(self.color_theme, self.color_lightness)
            self.quaternary_color.analogous_colors(self.color_theme, self.color_lightness)
        elif self.color_theme[:7] == "Triadic":
            self.background_color.triadic_colors(self.color_theme, self.color_lightness)
            self.secondary_color.triadic_colors(self.color_theme, self.color_lightness)
            self.quaternary_color.triadic_colors(self.color_theme, self.color_lightness)
        elif self.color_theme[:8] == "Tetradic":
            self.background_color.tetradic_colors(self.color_theme, self.color_lightness)
            self.secondary_color.tetradic_colors(self.color_theme, self.color_lightness)
            self.quaternary_color.tetradic_colors(self.color_theme, self.color_lightness)
        elif self.color_theme[:14] == "Comp-analogous":
            self.background_color.complementary_analogous_colors(self.color_theme, self.color_lightness)
            self.secondary_color.complementary_analogous_colors(self.color_theme, self.color_lightness)
            self.quaternary_color.complementary_analogous_colors(self.color_theme, self.color_lightness)

def main() -> int:
    pg.init()
    window = pg.display.set_mode((500, 500))
    icon = pg.transform.scale(pg.image.load(path.join(path.join(path.dirname(path.abspath(argv[0])), 'assets'), "guitar_tool_logo.png")), (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("  Guitar Tool")
    clock = pg.time.Clock()
    guitar_tool = GuitarTool(window)

    done = False
    while not done:

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                done = True
            guitar_tool.handle_event(event)
        guitar_tool.update()
        pg.display.flip()
        clock.tick(50)
    pg.quit()
    return 0

if __name__ == '__main__':
    exit(main())