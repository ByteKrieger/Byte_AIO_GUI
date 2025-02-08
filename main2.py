import pygame
import subprocess

pygame.init()

WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moderne GUI - Pygame")

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
ORANGE = (255, 140, 0)
DARK_ORANGE = (255, 69, 0)

font = pygame.font.Font(None, 28)

def draw_button(text, x, y, w, h, color, hover_color, action, events):
    mouse = pygame.mouse.get_pos()
    clicked = any(event.type == pygame.MOUSEBUTTONDOWN for event in events)
    
    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        pygame.draw.rect(screen, hover_color, (x, y, w, h))
        if clicked and action:
            action()
    else:
        pygame.draw.rect(screen, color, (x, y, w, h))
    
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect()
    text_rect.center = (x + w // 2, y + h // 2)
    
    if text_rect.width > w - 10:
        text_surf = pygame.transform.scale(text_surf, (w - 10, text_rect.height))
        text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
    
    screen.blit(text_surf, text_rect)

def run_cmd():
    subprocess.run("echo Hallo von CMD!", shell=True)

def run_powershell():
    subprocess.run(["powershell", "-Command", "Write-Output 'Hallo von PowerShell!'"], shell=True)

def show_ip():
    subprocess.run("ipconfig", shell=True)

running = True
while running:
    screen.fill(BLACK)
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    
    draw_button("CMD Befehl", 100, 50, 200, 50, ORANGE, DARK_ORANGE, run_cmd, events)
    draw_button("PowerShell Befehl", 100, 120, 200, 50, ORANGE, DARK_ORANGE, run_powershell, events)
    draw_button("IP anzeigen", 100, 190, 200, 50, ORANGE, DARK_ORANGE, show_ip, events)
    
    pygame.display.flip()
    
pygame.quit()
