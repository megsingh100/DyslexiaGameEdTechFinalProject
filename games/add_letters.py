import pygame
import random
import string
from games.game_to_letter import popup

# ─── CONFIG ─────────────────────────────────────────────────────────────
K1_WORDS = ["WILD", "CHILD", "KIND", "MIND", "FIND", "SUN", "DOG", "LOG", "BED", "HAT"]

SPELLING_WORDS = {
    "MOST":   ("M__T", ["OS", "OA", "OU"]),
    "BREAK":  ("BR__K", ["EA", "AI", "AY"]),
    "EIGHT":  ("E__HT", ["IG", "EI", "AY"]),
    "KNOW":   ("K__W", ["NO", "KN", "NW"]),
    "LOUD":   ("L__D", ["OU", "OO", "UV"]),
    "EARLY":  ("E__LY", ["AR", "ER", "UR"]),
    "LAUGH":  ("L__GH", ["AU", "AR", "AF"]),
    "SURE":   ("S__E", ["UR", "OR", "IR"]),
    "THOUGH": ("TH__GH", ["OU", "OA", "OE"]),
}

BG_IMAGE        = "assets/images/default_screen.png"
PROMPT_COLOR    = (0, 102, 204)
TEXT_COLOR      = (0, 0, 0)
CORRECT_COLOR   = (0, 200, 0)
WRONG_COLOR     = (200, 0, 0)

def run_add_letters(screen, font):
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()
    bg = pygame.image.load(BG_IMAGE)
    bg = pygame.transform.scale(bg, (sw, sh))

    # ─── Grade Selection ──────────────────────────────────────────────
    grade = ""
    while not grade:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            elif e.type == pygame.KEYDOWN:
                if e.unicode == "1":
                    grade = "K1"
                elif e.unicode == "2":
                    grade = "23"

        screen.blit(bg, (0, 0))
        line1 = font.render("Select Grade Level:", True, 'black')
        line2 = font.render("Press 1 for K–1", True, 'black')
        line3 = font.render("Press 2 for Grade 2–3", True, 'black')
        screen.blit(line1, line1.get_rect(center=(sw//2, sh//2 - 80)))
        screen.blit(line2, line2.get_rect(center=(sw//2, sh//2)))
        screen.blit(line3, line2.get_rect(center=(sw // 2-100, sh // 2+100)))
        pygame.display.flip()
        clock.tick(30)

    # ─── Word Setup ────────────────────────────────────────────────────
    correct = 0
    if grade == "K1":
        rounds = K1_WORDS.copy()
    else:
        rounds = list(SPELLING_WORDS.items())

    random.shuffle(rounds)
    total = len(rounds)

    for r in rounds:
        typed = ""
        feedback = ""
        answered = False
        color = TEXT_COLOR

        if grade == "K1":
            word = r
            idx = random.randrange(len(word))
            missing = word[idx]
            display = word[:idx] + "_" + word[idx+1:]
            options = [missing] + random.sample([c for c in string.ascii_uppercase if c != missing], 2)
        else:
            actual_word, (display, phonemes) = r
            correct_phoneme = phonemes[0]
            options = phonemes.copy()

        random.shuffle(options)

        # ─── Game Loop ────────────────────────────────────────────────
        while not answered:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return correct / total
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN and typed:
                        if typed in options:
                            if (grade == "K1" and typed == missing) or (grade == "23" and typed == correct_phoneme):
                                feedback = "Correct!"
                                color = CORRECT_COLOR
                                correct += 1
                            else:
                                feedback = f"Oops—'{typed}' is wrong"
                                color = WRONG_COLOR
                        else:
                            feedback = f"'{typed}' is not a valid option"
                            color = WRONG_COLOR
                        answered = True
                    elif e.key == pygame.K_BACKSPACE:
                        typed = typed[:-1]
                    elif e.unicode.isalpha():
                        max_len = 1 if grade == "K1" else 2
                        if len(typed) < max_len:
                            typed += e.unicode.upper()

            screen.blit(bg, (0, 0))
            line1 = font.render("Fill in the missing part", True, PROMPT_COLOR)
            line2 = font.render("Then press ENTER:", True, PROMPT_COLOR)
            screen.blit(line1, line1.get_rect(center=(sw // 2, sh // 2 - 190)))
            screen.blit(line2, line2.get_rect(center=(sw // 2, sh // 2 - 150)))

            word_surf = font.render(display, True, PROMPT_COLOR)
            screen.blit(word_surf, word_surf.get_rect(center=(sw//2, sh//2 - 40)))

            # Options
            start_x = sw//2 - 150
            for i, opt in enumerate(options):
                opt_surf = font.render(opt, True, TEXT_COLOR)
                pos = (start_x + i*150, sh//2 + 20)
                screen.blit(opt_surf, opt_surf.get_rect(center=pos))
                box = pygame.Rect(0, 0, 80, 60)
                box.center = pos
                pygame.draw.rect(screen, PROMPT_COLOR, box, 2)

            typed_surf = font.render(typed, True, TEXT_COLOR)
            screen.blit(typed_surf, typed_surf.get_rect(center=(sw//2, sh//2 + 100)))

            if feedback:
                fb_surf = font.render(feedback, True, color)
                screen.blit(fb_surf, fb_surf.get_rect(center=(sw//2, sh//2 + 140)))

            pygame.display.flip()
            clock.tick(30)

        pygame.time.delay(800)

    # ─── Result Popup ────────────────────────────────────────────────
    accuracy = correct / total
    if accuracy >= 0.8:
        popup(screen, font, [
            f"Great job! {correct}/{total} correct.",
            "You passed!",
            "Press SPACE to return"
        ])
    else:
        popup(screen, font, [
            f"You got {correct}/{total}.",
            "Try again next time."

        ])
    return accuracy
