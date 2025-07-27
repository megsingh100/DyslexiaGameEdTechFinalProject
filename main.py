import pygame
import json
import os
from games.game_to_letter import run_treasure_hunt
from games.game_unjumble  import run_unjumble
from games.add_letters    import run_add_letters
from games.memory_match   import run_memory_match

# ─── Config ──────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1024, 768
FONT_PATH        = "assets/OpenDyslexic-Regular.otf"
PROFILES_FILE    = "profiles.json"
NAME_IMAGE       = "assets/images/enter_name.png"

# only background for map & locked popups
MAP_BG           = "assets/images/adventure_map.png"
LOCKED_BG = "assets/images/default_screen.png"

# ─── Profile I/O ─────────────────────────────────────────────────────────
def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        return {}
    with open(PROFILES_FILE, "r") as f:
        return json.load(f)

def save_profiles(profiles):
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

def create_or_load_profile(username):
    default_scores = {
        "treasure":    0.0,
        "unjumble":    0.0,
        "add_letters": 0.0,
        "memory":      0.0
    }
    if username == "Guest":
        return {"scores": default_scores.copy()}, None

    profiles = load_profiles()
    if username not in profiles:
        profiles[username] = {"scores": default_scores.copy()}
    else:
        if "scores" not in profiles[username]:
            profiles[username]["scores"] = default_scores.copy()
    save_profiles(profiles)
    return profiles[username], profiles

# ─── Start Screen ────────────────────────────────────────────────────────
def start_screen(screen, font):
    bg = pygame.image.load("assets/images/main_menu.png")
    bg = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return "start"
                if e.key == pygame.K_2: return "guest"
        screen.blit(bg, (0, 0))
        pygame.display.flip()

# ─── Username Prompt ─────────────────────────────────────────────────────
def username_prompt(screen, font):
    bg = pygame.image.load(NAME_IMAGE)
    bg = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
    box = pygame.Rect(int(SCREEN_W*0.58), int(SCREEN_H*0.4), 300, 60)
    color, active, username = pygame.Color('black'), False, ""
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.MOUSEBUTTONDOWN:
                active = box.collidepoint(e.pos)
            if e.type == pygame.KEYDOWN and active:
                if e.key == pygame.K_RETURN:
                    return username.strip() or "Player"
                if e.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif e.unicode.isprintable() and len(username)<12:
                    username += e.unicode

        screen.blit(bg, (0,0))
        txt = font.render(username, True, (0,0,0))
        box.w = max(300, txt.get_width()+20)
        screen.blit(txt, (box.x+10, box.y+15))
        pygame.draw.rect(screen, color, box, 3)
        pygame.display.flip()
        clock.tick(30)

# ─── Welcome Popup ───────────────────────────────────────────────────────
def popup_message(screen, font, lines):
    bg     = pygame.image.load("assets/images/default_screen.png")
    bg     = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
    texts  = [font.render(l, True, (0,0,0)) for l in lines]
    prompt = font.render("Press SPACE to continue", True, (80,80,80))
    clock  = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                return True

        screen.blit(bg, (0,0))
        # center all texts
        total_h = sum(t.get_height() for t in texts) + 20*(len(texts)-1)
        y = SCREEN_H//2 - total_h//2
        for t in texts:
            r = t.get_rect(center=(SCREEN_W//2, y + t.get_height()//2))
            screen.blit(t, r)
            y += t.get_height() + 20
        screen.blit(prompt, prompt.get_rect(center=(SCREEN_W//2, SCREEN_H*0.85)))
        pygame.display.flip()
        clock.tick(30)

# ─── Locked Level Popup ───────────────────────────────────────────────────
def show_locked(screen, font):
    bg      = pygame.image.load(LOCKED_BG)
    bg      = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0,0,0,180))
    text   = font.render("You are not at this level yet", True, (255,0,0))
    prompt = font.render("Press SPACE to return", True, (200,200,200))
    clock  = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                return

        screen.blit(bg, (0,0))
        screen.blit(overlay, (0,0))
        screen.blit(text, text.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 20)))
        screen.blit(prompt, prompt.get_rect(center=(SCREEN_W//2, SCREEN_H*0.85)))
        pygame.display.flip()
        clock.tick(30)

# ─── Adventure Map ───────────────────────────────────────────────────────
def adventure_map(screen, font, username, profile, profiles):
    bg    = pygame.image.load(MAP_BG)
    bg    = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
    BLUE  = (0,102,204)
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return

            if e.type == pygame.KEYDOWN:
                # Treasure Hunt
                if e.key == pygame.K_1:
                    acc = run_treasure_hunt(screen, font)
                    profile["scores"]["treasure"] = acc
                    if profiles: save_profiles(profiles)

                # Unjumble (needs ≥80%)
                elif e.key == pygame.K_2:
                    if (profile["scores"].get("treasure") or 0.0) >= 0.8:
                        acc = run_unjumble(screen, font)
                        profile["scores"]["unjumble"] = acc
                        if profiles: save_profiles(profiles)
                    else:
                        show_locked(screen, font)

                # Add Letters (needs ≥80%)
                elif e.key == pygame.K_3:
                    if (profile["scores"].get("unjumble") or 0.0) >= 0.8:
                        acc = run_add_letters(screen, font)
                        profile["scores"]["add_letters"] = acc
                        if profiles: save_profiles(profiles)
                    else:
                        show_locked(screen, font)

                # Memory Match (needs ≥80%)
                elif e.key == pygame.K_4:

                    if (profile["scores"].get("add_letters") or 0.0) >= 0.8:
                        font = pygame.font.Font(FONT_PATH, 20)
                        acc = run_memory_match(screen, font)
                        profile["scores"]["memory"] = acc
                        if profiles: save_profiles(profiles)
                    else:
                        show_locked(screen, font)

        # draw map on top of bg
        screen.blit(bg, (0,0))


        pygame.display.flip()
        clock.tick(30)

# ─── Main ────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Lucky Letters")
    font = pygame.font.Font(FONT_PATH, 36)

    # 1) startup
    from_start = start_screen(screen, font)
    if from_start is None:
        pygame.quit()
        return

    # 2) name or guest
    if from_start == "start":
        username = username_prompt(screen, font)
        if username is None:
            pygame.quit()
            return
    else:
        username = "Guest"

    # 3) load/create profile
    profile, profiles = create_or_load_profile(username)

    # 4) welcome popup
    lines = (["Welcome, Guest!", "Ready to explore?"]
             if username=="Guest"
             else [f"Welcome, {username}!", "Let's begin your adventure!"])
    if not popup_message(screen, font, lines):
        pygame.quit()
        return

    # 5) adventure map
    adventure_map(screen, font, username, profile, profiles)
    pygame.quit()

if __name__ == "__main__":
    main()
