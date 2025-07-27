import pygame
import random
import os

# ─── CONFIG ─────────────────────────────────────────────────────────────
SOUND_BASE_DIR = "assets/audios"
BG_IMAGE       = "assets/images/default_screen.png"
CARD_COLOR     = (200, 200, 250)
MATCHED_COLOR  = (0, 200, 0)
BORDER_COLOR   = (50, 50, 100)
TEXT_COLOR     = (0, 0, 0)
CARD_W, CARD_H = 150, 100
GAP            = 20

class Card:
    def __init__(self, rect, value, is_audio):
        self.rect     = rect
        self.value    = value
        self.is_audio = is_audio
        self.matched  = False

    def draw(self, screen, font):
        fill_color = MATCHED_COLOR if self.matched else CARD_COLOR
        pygame.draw.rect(screen, fill_color, self.rect)
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, 2)

        if not self.is_audio:
            txt = font.render(self.value.upper(), True, TEXT_COLOR)
            screen.blit(txt, txt.get_rect(center=self.rect.center))

def popup(screen, font, lines):
    sw, sh = screen.get_size()
    bg     = pygame.image.load(BG_IMAGE)
    bg     = pygame.transform.scale(bg, (sw, sh))
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    text_surfs  = [font.render(line, True, (255, 255, 255)) for line in lines]
    prompt_surf = font.render("Press SPACE to continue", True, (200, 200, 200))
    clock       = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: return
        screen.blit(bg, (0, 0))
        screen.blit(overlay, (0, 0))
        total_h = sum(s.get_height() for s in text_surfs) + 20*(len(text_surfs)-1)
        y = (sh - total_h)//2
        for surf in text_surfs:
            rect = surf.get_rect(center=(sw//2, y + surf.get_height()//2))
            screen.blit(surf, rect)
            y += surf.get_height() + 20
        screen.blit(prompt_surf, prompt_surf.get_rect(center=(sw//2, int(sh*0.85))))
        pygame.display.flip()
        clock.tick(30)

def flash_message(screen, font, message, color):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((*color, 120))
    text_surf = font.render(message, True, (0, 0, 0))
    clock     = pygame.time.Clock()
    start     = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 1000:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
        screen.blit(overlay, (0, 0))
        screen.blit(text_surf, text_surf.get_rect(center=screen.get_rect().center))
        pygame.display.flip()
        clock.tick(30)

def ask_grade_level(screen, font):
    sw, sh = screen.get_size()
    bg = pygame.image.load(BG_IMAGE)
    bg = pygame.transform.scale(bg, (sw, sh))

    options = ["1) K–1", "2) Grade 2–3"]
    prompt  = "Choose your level:"
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.KEYDOWN:
                if e.unicode == "1": return "k"
                elif e.unicode == "2": return "spelling"

        screen.blit(bg, (0, 0))
        prompt_surf = font.render(prompt, True, TEXT_COLOR)
        screen.blit(prompt_surf, prompt_surf.get_rect(center=(sw // 2, sh // 2 - 100)))

        for i, line in enumerate(options):
            option_surf = font.render(line, True, TEXT_COLOR)
            screen.blit(option_surf, option_surf.get_rect(center=(sw // 2, sh // 2 + i * 50)))

        pygame.display.flip()
        clock.tick(30)

# ─── GAME LOGIC ─────────────────────────────────────────────────────────
def run_memory_match(screen, font):
    pygame.mixer.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()
    bg     = pygame.image.load(BG_IMAGE)
    bg     = pygame.transform.scale(bg, (sw, sh))

    level = ask_grade_level(screen, font)
    if not level: return 0

    instructions = [
        "Match each sound with its written word.",
        "Click a sound card to hear it.",
        "Then click the word that matches.",
        "Make all matches to win!"
    ]
    popup(screen, font, instructions)

    sound_dir = os.path.join(SOUND_BASE_DIR, level)
    sound_files = [f for f in os.listdir(sound_dir) if f.endswith(".mp3")]
    words       = [os.path.splitext(f)[0] for f in sound_files]
    if not words: return 0
    random.shuffle(words)

    all_card_data = [(w, True) for w in words] + [(w, False) for w in words]
    random.shuffle(all_card_data)

    cols = min(6, len(all_card_data))
    rows = (len(all_card_data) + cols - 1) // cols

    cards_all = []
    for i, (val, is_audio) in enumerate(all_card_data):
        row, col = divmod(i, cols)
        x = GAP + col * (CARD_W + GAP)
        y = GAP + row * (CARD_H + GAP)
        rect = pygame.Rect(x, y, CARD_W, CARD_H)
        cards_all.append(Card(rect, val, is_audio))

    matched = 0
    selected_audio = None

    while matched < len(words):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return matched / len(words)
            if e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for c in cards_all:
                    if c.rect.collidepoint(pos) and not c.matched:
                        if c.is_audio:
                            selected_audio = c
                            if pygame.mixer.music.get_busy():
                                pygame.mixer.music.stop()
                            mp3 = os.path.join(sound_dir, f"{c.value}.mp3")
                            pygame.mixer.music.load(mp3)
                            pygame.mixer.music.play()
                        elif selected_audio:
                            if c.value == selected_audio.value:
                                c.matched = selected_audio.matched = True
                                matched += 1
                                flash_message(screen, font, "Matched!", (0, 200, 0))
                            else:
                                flash_message(screen, font, "Try Again", (200, 50, 50))
                            selected_audio = None

        screen.blit(bg, (0, 0))
        for c in cards_all:
            c.draw(screen, font)
        pygame.display.flip()
        clock.tick(30)

    popup(screen, font, [
        "Great job! All matches completed.",
        "Press SPACE to play again"
    ])
    return matched / len(words)

# ─── MAIN ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Audio Match Game")
    font = pygame.font.SysFont(None, 48)
    run_memory_match(screen, font)
    pygame.quit()
