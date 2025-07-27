import pygame
import random
import os

# ─── CONFIG ─────────────────────────────────────────────────────────────
IMAGES_DIR = "assets/images/image_game"
BG_IMAGE   = "assets/images/default_screen.png"

# ─── POPUP ──────────────────────────────────────────────────────────────
def popup(screen, font, lines):
    sw, sh = screen.get_size()
    bg = pygame.image.load(BG_IMAGE)
    bg = pygame.transform.scale(bg, (sw, sh))
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    text_surfs  = [font.render(line, True, (255,255,255)) for line in lines]
    prompt_surf = font.render("Press SPACE to continue", True, (200, 200, 200))
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: return
        screen.blit(bg, (0,0))
        screen.blit(overlay, (0,0))
        total_h = sum(s.get_height() for s in text_surfs) + 20*(len(text_surfs)-1)
        y = (sh - total_h) // 2
        for surf in text_surfs:
            rect = surf.get_rect(center=(sw//2, y + surf.get_height()//2))
            screen.blit(surf, rect)
            y += surf.get_height() + 20
        screen.blit(prompt_surf, prompt_surf.get_rect(center=(sw//2, int(sh*0.85))))
        pygame.display.flip()
        clock.tick(30)

# ─── LEVEL SELECT ───────────────────────────────────────────────────────
def ask_grade_level(screen, font):
    sw, sh = screen.get_size()
    bg = pygame.image.load(BG_IMAGE)
    bg = pygame.transform.scale(bg, (sw, sh))
    options = ["1) K–1", "2) Grade 2–3"]
    prompt  = "Choose your level:"

    font_small = font  # ← Use the main font instead
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.KEYDOWN:
                if e.unicode == "1": return "K"
                elif e.unicode == "2": return "Spelling"

        screen.blit(bg, (0,0))
        p = font.render(prompt, True, (0,0,0))
        screen.blit(p, p.get_rect(center=(sw//2, sh//2 - 100)))
        for i, line in enumerate(options):
            surf = font_small.render(line, True, (0,0,0))
            screen.blit(surf, surf.get_rect(center=(sw//2, sh//2 + i*50)))
        pygame.display.flip()
        clock.tick(30)


# ─── TREASURE HUNT GAME ─────────────────────────────────────────────────
def run_treasure_hunt(screen, font):
    level = ask_grade_level(screen, font)
    if level is None: return 0

    clock = pygame.time.Clock()
    sw, sh = screen.get_size()
    bg = pygame.image.load(BG_IMAGE)
    bg = pygame.transform.scale(bg, (sw, sh))

    files = [f for f in os.listdir(IMAGES_DIR) if f.endswith(".png")]
    random.shuffle(files)
    rounds = files  # Use all images
    correct = 0
    total = len(rounds)

    for img_file in rounds:
        img_path = os.path.join(IMAGES_DIR, img_file)
        word     = os.path.splitext(img_file)[0]
        first_letter = word[0].upper()
        image = pygame.image.load(img_path)
        image = pygame.transform.smoothscale(image, (200, 200))

        feedback = ""
        typed    = ""
        color    = (0,200,0)
        answered = False

        while not answered:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return correct / total
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_BACKSPACE:
                        typed = typed[:-1]

                    elif level == "K":
                        if e.unicode.isalpha() and len(typed) < 1:
                            typed += e.unicode.upper()
                        if e.key == pygame.K_RETURN and typed:
                            if typed == first_letter:
                                feedback = "Correct!"
                                correct += 1
                                color = (0, 200, 0)
                            else:
                                feedback = f"Nope, that was '{typed}'"
                                color = (200, 0, 0)
                            answered = True

                    elif level == "Spelling":
                        if e.unicode.isalpha():
                            typed += e.unicode
                        if e.key == pygame.K_RETURN and typed:
                            guess = typed.lower()
                            if guess == word.lower():
                                feedback = "Correct!"
                                correct += 1
                                color = (0, 200, 0)
                            else:
                                feedback = f"Nope, that was '{typed}'"
                                color = (200, 0, 0)
                            answered = True

            screen.blit(bg, (0, 0))
            screen.blit(image, image.get_rect(center=(sw//2, sh//2 - 60)))

            if level == "K":
                prompt = font.render("Type the letter this image starts with:", True, (0,0,0))
            else:
                prompt = font.render("Spell the word shown in the image:", True, (0,0,0))
            screen.blit(prompt, prompt.get_rect(center=(sw//2, sh//2 + 100)))

            typed_surf = font.render(typed, True, (0,0,0))
            screen.blit(typed_surf, typed_surf.get_rect(center=(sw//2, sh//2 + 140)))

            if feedback:
                fb = font.render(feedback, True, color)
                screen.blit(fb, fb.get_rect(center=(sw//2, sh//2 + 180)))

            pygame.display.flip()
            clock.tick(30)

        pygame.time.delay(800)

    accuracy = correct / total
    popup(screen, font, [
        f"You got {correct}/{total}.",
        "You passed!" if accuracy >= 0.8 else "Try again next time."
    ])
    return accuracy

# ─── MAIN ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    font = pygame.font.SysFont(None, 28)  # Adjusted for compact text
    run_treasure_hunt(screen, font)
    pygame.quit()
