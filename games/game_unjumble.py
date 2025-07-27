import pygame, random, json, os
from games.game_to_letter import popup

# CONFIG
WORD_BANK = os.path.join(os.path.dirname(__file__), "word_bank.json")
BG_IMAGE  = "assets/images/default_screen.png"

def scramble(word):
    arr = list(word)
    s   = word
    while s == word:
        random.shuffle(arr)
        s = "".join(arr)
    return s

def ask_grade_level(screen, font):
    sw, sh = screen.get_size()
    bg = pygame.image.load(BG_IMAGE)
    bg = pygame.transform.scale(bg, (sw, sh))
    options = ["1) K–1", "2) Grade 2–3"]
    prompt = "Choose your level:"
    font_small = font
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

def run_unjumble(screen, font):
    level = ask_grade_level(screen, font)
    if not level: return 0

    clock = pygame.time.Clock()
    sw, sh = screen.get_size()
    bg = pygame.image.load(BG_IMAGE)
    bg = pygame.transform.scale(bg, (sw, sh))

    with open(WORD_BANK, "r") as f:
        data = json.load(f)
    words = data.get(level, [])
    if not words: return 0
    random.shuffle(words)
    rounds = words
    correct_count = 0

    for word in rounds:
        scrambled = scramble(word)
        entry = ""
        feedback = ""
        answered = False

        while not answered:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return correct_count / len(rounds)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_BACKSPACE:
                        entry = entry[:-1]
                    elif e.key == pygame.K_RETURN:
                        if entry.lower() == word.lower():
                            feedback = "Correct!"
                            correct_count += 1
                        else:
                            feedback = "Wrong"
                        answered = True
                    elif e.unicode.isalpha() and len(entry) < len(word):
                        entry += e.unicode

            # draw
            screen.blit(bg, (0,0))
            sc = font.render(f"Unscramble: {scrambled}", True, (0,0,0))
            screen.blit(sc, sc.get_rect(center=(sw//2, sh//2 - 100)))

            inp = font.render(entry, True, (0,0,0))
            screen.blit(inp, inp.get_rect(center=(sw//2, sh//2)))

            if feedback:
                clr = (0,180,0) if feedback.startswith("Correct") else (200,0,0)
                fb = font.render(feedback, True, clr)
                screen.blit(fb, fb.get_rect(center=(sw//2, sh//2 + 80)))

            sp = font.render(f"Score: {correct_count}", True, (0,0,0))
            screen.blit(sp, (20,20))

            pygame.display.flip()
            clock.tick(30)

        pygame.time.delay(800)

    accuracy = correct_count / len(rounds)
    popup(screen, font, [
        f"You got {correct_count}/{len(rounds)}.",
        "You passed!" if accuracy >= 0.8 else "Try again next time.",
        "Press SPACE to return"
    ])
    return accuracy
