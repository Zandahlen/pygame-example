import logging
import pygame
import sys
import math
import random

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Constants
FPS = 60
SCREEN_SIZE = (800, 600)
CAPTION = "Edwin's game"

COLOR = {'ship': pygame.Color('#FF4444'),
         'ship_fill': pygame.Color('#440000'),
         'bg': pygame.Color('#000000'),
         'thruster': pygame.Color('#7799FF'),
         'steering': pygame.Color('#7799FF'),
         'fuel': pygame.Color('#FF4444'),
         'fuelPackage': pygame.Color('#7799FF')
}

# Game states
STATE_PREGAME = 1
STATE_RUNNING = 2
STATE_GAMEOVER = 3
STATE_PAUSED = 4

class Controller():
    """Game controller."""

    def __init__(self):
        """Initialize game controller."""
        self.fps = FPS

        pygame.init()
        pygame.mixer.quit()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()

        self.player = Player(self.screen)
        self.fuelPackage = fuelPackage(self.screen)

        # Initialize game state
        self.game_state = STATE_PREGAME

        self.font1 = pygame.font.SysFont("monospace", 40)
        self.font2 = pygame.font.SysFont("monospace", 25)
        self.font3 = pygame.font.SysFont("monospace", 15)



    def run(self):
        """Main game loop."""
        while True:
            # Manage event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # ALT + F4 or icon in upper right corner.
                    self.quit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Escape key pressed.
                    self.quit()

                if self.game_state == STATE_PREGAME:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.game_state = STATE_RUNNING

                if self.game_state == STATE_GAMEOVER:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.player.reset()
                        self.fuelPackage.reset()
                        self.game_state = STATE_RUNNING

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        self.fuelPackage.reset()
                        self.player.reset()
                        self.game_state = STATE_PREGAME

                if self.game_state == STATE_PAUSED:
                    #Preventing engines to continue when unpausing
                    if event.type == pygame.KEYUP and event.key == pygame.K_w:
                        self.player.engine_off()
                    if event.type == pygame.KEYUP and event.key == pygame.K_a:
                        self.player.a_steering_off()
                    if event.type == pygame.KEYUP and event.key == pygame.K_d:
                        self.player.d_steering_off()


                    if event.type == pygame.KEYDOWN and event.key != pygame.K_p:
                        self.game_state = STATE_RUNNING

                if self.game_state == STATE_RUNNING:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        self.game_state = STATE_PAUSED

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                        self.player.engine_on()

                    if event.type == pygame.KEYUP and event.key == pygame.K_w:
                        self.player.engine_off()

                    #Advanced steering
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                        self.player.a_steering_on()

                    if event.type == pygame.KEYUP and event.key == pygame.K_a:
                        self.player.a_steering_off()

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                        self.player.d_steering_on()

                    if event.type == pygame.KEYUP and event.key == pygame.K_d:
                        self.player.d_steering_off()

            # Manage game_state
            if self.game_state == STATE_PREGAME:
                self.screen.fill(COLOR['bg'])

                lblPG1 = self.font1.render("Press Space to play!", 1, (0,255,255))
                lblPG2 = self.font2.render("- W for gas, ESC to quit", 1, (0,255,255))
                lblPG3 = self.font2.render("- A and D, to turn", 1, (0,255,255))
                lblPG4 = self.font2.render("- P for pause and SPACE to continue", 1, (0,255,255))


                self.screen.blit(lblPG1, (SCREEN_SIZE[0]/2 - lblPG1.get_width()/2, lblPG1.get_height()))
                self.screen.blit(lblPG2, (SCREEN_SIZE[0]/2 - lblPG1.get_width()/2, lblPG1.get_height() * 2))
                self.screen.blit(lblPG3, (SCREEN_SIZE[0]/2 - lblPG1.get_width()/2, lblPG1.get_height() * 2 + lblPG2.get_height()))
                self.screen.blit(lblPG4, (SCREEN_SIZE[0]/2 - lblPG1.get_width()/2, lblPG1.get_height() * 2 + lblPG2.get_height() + lblPG3.get_height()))

            if self.game_state == STATE_PAUSED:
                lblPaused = self.font3.render("Game paused!", 1, (0,255,255))
                lblContinue = self.font3.render("Press to Continue", 1, (0,255,255))
                self.screen.blit(lblPaused, (100, 100))
                self.screen.blit(lblContinue, (100, 125))

            if self.game_state == STATE_RUNNING:
                with open("highscore.txt", 'r+') as hstxt:
                    highscore = hstxt.read().strip()

                self.player.tick()
                self.fuelPackage.tick()

                if math.sqrt((self.player.x - self.fuelPackage.x) ** 2 + (self.player.y - self.fuelPackage.y) ** 2) < 15:
#                if abs(self.player.x - self.fuelPackage.x) < 5 and abs(self.player.y - self.fuelPackage.y) < 5:
                    self.player.fuel += self.fuelPackage.fuelWorth
                    #self.player.fuel += 200
                    self.player.score += self.fuelPackage.fuelWorth
                    self.fuelPackage.reset()

                if self.player.y > SCREEN_SIZE[1] or self.player.y < 1:
#                    logger.debug('OUT OF BOUNDS!')
                    reasonOfLoss = "You flew to far!"
                    self.game_state = STATE_GAMEOVER

                if self.player.x > SCREEN_SIZE[0] or self.player.x < 1:
                    reasonOfLoss = "You flew to far!"
                    self.game_state = STATE_GAMEOVER

                if self.player.fuel <= 0 and abs(self.player.x_speed) + abs(self.player.y_speed) < 0.02:
                    reasonOfLoss = "Out of fuel!"
                    self.game_state = STATE_GAMEOVER


                self.screen.fill(COLOR['bg'])
                self.player.draw()
                self.fuelPackage.draw()

                labelFuel = self.font3.render("FUEL:", 1, self.player.fuelColor)
                labelFuelAmount = self.font3.render(str(self.player.fuel), 1, self.player.fuelColor)
                self.screen.blit(labelFuel, (10, 10))
                self.screen.blit(labelFuelAmount, (20, 25))

                labelScore = self.font3.render("Score:", 1, (50,255,50))
                labelScoreAmount = self.font3.render(str(self.player.score), 1, (50,255,50))
                self.screen.blit(labelScore, (10, 40))
                self.screen.blit(labelScoreAmount, (20, 55))


                labelWorth = self.font3.render("Worth:", 1, (255,255,25))
                labelWorthAmount = self.font3.render(str(self.fuelPackage.fuelWorth), 1, (255,255,25))
                self.screen.blit(labelWorth, (10, 70))
                self.screen.blit(labelWorthAmount, (20, 85))


                labelHS = self.font3.render("Highscore:", 1, (230,25,255))
                labelHSAmount = self.font3.render(highscore, 1, (230,25,255))
                self.screen.blit(labelHS, (10, 100))
                self.screen.blit(labelHSAmount, (20, 117))


            if self.game_state == STATE_GAMEOVER:
                highscoreInt = int(highscore)
                if self.player.score > highscoreInt:
                    hstxt.close()
                    with open("highscore.txt", 'r+') as hstxt:
                        hstxt.write(str(self.player.score))
                        highscoreInt = self.player.score
                        hstxt.close()
                        labelNewHighScore = self.font2.render(("The new highscore is " + str(highscoreInt)), 1, (25,255,25))
                        labelBeatHS = self.font1.render("You beat the highscore!", 1, (25, 255,25))
                        self.screen.blit(labelNewHighScore, (200, 125))
                        self.screen.blit(labelBeatHS, (150, 150))

                labelGameOver1 = self.font1.render("GAME OVER", 1, (0,255,255))
                labelOutOfFuel = self.font2.render(reasonOfLoss, 1, (255,25,25))
                labelGameOver2 = self.font2.render("- press ESC to quit", 1, (0,255,255))
                labelGameOver3 = self.font2.render("- press SPACE to play again", 1, (0,255,255))
                labelPregame4 = self.font2.render("- P to go back to main page", 1, (0,255,255))
                #labelInput = self.font2.render(input('Name'), 1, (0,255,255))


                self.screen.blit(labelGameOver1, (300, 225))
                self.screen.blit(labelGameOver2, (300, 300))
                self.screen.blit(labelGameOver3, (300, 325))
                self.screen.blit(labelPregame4, (300, 350))
                self.screen.blit(labelOutOfFuel, (310, 275))
                #self.screen.blit(labelInput, (310, 400))

            pygame.display.flip()

            self.clock.tick(self.fps)

    def quit(self):
        logging.info('Quitting... good bye!')
        pygame.quit()
        sys.exit()


class Player():
    def __init__(self, screen):
        self.screen = screen
        self.reset()

    def reset(self):
        self.x = SCREEN_SIZE[0] / 2
        self.y = SCREEN_SIZE[1] / 2
        self.engine = False
        self.x_speed = 0
        self.y_speed = 0
        self.direction = 0
        self.a_steering = False
        self.d_steering = False
        self.turn_y = 0
        self.turn_x = 0
        self.fuel = 1000
        self.score = 0
        self.fuelColor = (0, 255, 0)

    def draw(self):
        surface = pygame.Surface((20, 20))
        surface.fill(COLOR['bg'])
#        pygame.draw.line(surface, COLOR['ship'], (10, 0), (15, 20))
#        pygame.draw.line(surface, COLOR['ship'], (10, 0), (5, 20))
        pygame.draw.polygon(surface, COLOR['ship_fill'], ((10, 0), (15, 15), (5, 15)), 0)
        pygame.draw.polygon(surface, COLOR['ship'], ((10, 0), (15, 15), (5, 15)), 1)

        if self.engine and self.fuel >= 2:
            pygame.draw.polygon(surface, COLOR['thruster'], ((13, 16), (10, 19), (7, 16)), 0)

        #Steering
        if self.a_steering and self.fuel >= 1:
            pygame.draw.polygon(surface, COLOR['steering'], ((14, 12), (15, 10), (18, 13), (14, 12), 0))

        if self.d_steering and self.fuel >= 1:
            pygame.draw.polygon(surface, COLOR['steering'], ((6, 12), (5, 10), (2, 13), (6, 12), 0))

        #surface = pygame.transform.rotate(surface, 180)
        surface = pygame.transform.rotate(surface, self.direction)
        self.screen.blit(surface, (self.x - 10, self.y - 10))

        #logSurface = pygame.Surface(20, 20)



    def tick(self):
        #Steering
        if self.engine and self.fuel >= 2:
            self.x_speed -= math.sin(math.radians(self.direction)) * 0.17
            self.y_speed -= math.cos(math.radians(self.direction)) * 0.17
            self.fuel -= 2

        self.x_speed = self.x_speed *0.975
        self.y_speed = self.y_speed *0.975


        self.y = self.y + self.y_speed + self.turn_y
        self.x = self.x + self.x_speed + self.turn_x

        if self.a_steering and self.fuel >= 1:
            self.fuel -= 1
            if self.direction == 357.5:
                self.direction = 0
            else:
                self.direction += 2.5
        # adds speed when turning
            self.turn_x = -1 * math.sin(math.radians(self.direction))
            self.turn_y = -1 * math.cos(math.radians(self.direction))
        else:
            self.turn_x = self.turn_x * 0.9
            self.turn_y = self.turn_y * 0.9

        if self.d_steering and self.fuel >= 1:
            self.fuel -= 1
            if self.direction == 0:
                self.direction = 357.5
            else:
                self.direction -= 2.5
        # adds speed when turning
            self.turn_x = -1 * math.sin(math.radians(self.direction))
            self.turn_y = -1 * math.cos(math.radians(self.direction))
        else:
            self.turn_x = self.turn_x * 0.9
            self.turn_y = self.turn_y * 0.9

        if self.fuel >= 755:
            self.fuelColor = (0, 255, 0)
        else:
            if self.fuel >= 500:
                self.fuelColor = ((755 - self.fuel), 255, 0)
            else:
                self.fuelColor = (255, (self.fuel * 0.5), 0)


    def engine_on(self):
        self.engine = True

    def engine_off(self):
        self.engine = False

    #Steering
    def a_steering_on(self):
        self.a_steering = True

    def a_steering_off(self):
        self.a_steering = False

    def d_steering_on(self):
        self.d_steering = True

    def d_steering_off(self):
        self.d_steering = False

class fuelPackage():
    #fuelPackage to refill fuel
    def __init__(self, screen):
        self.screen = screen
        self.reset()

    def reset(self):
        self.fuelWorth = 255
        self.x = random.randint(20, (SCREEN_SIZE[0] - 20))
        self.y = random.randint(20, (SCREEN_SIZE[1] - 20))
        self.clock_tick = 1

    def tick(self):
        #Use to see where random place and doesn't place
        #self.x = random.randint(20, (SCREEN_SIZE[0] - 20))
        #self.y = random.randint(20, (SCREEN_SIZE[1] - 20))
        COLOR['fuel'] = ((self.clock_tick * 20 ), 0, 0)

        if self.clock_tick == 10:
            COLOR['fuelPackage'] = ((255 - self.fuelWorth), (255 - self.fuelWorth),(self.fuelWorth))
            self.clock_tick = 0
            if self.fuelWorth > 50:
                self.fuelWorth = self.fuelWorth - 4
        else:
            self.clock_tick += 1

    def draw(self):
        fuelP = pygame.Surface((20, 20))
        #fuelP.fill(COLOR['fuelPackage'])
        #pygame.draw.circle(fuelP, COLOR['fuelPackage'], [10, 10], 1, 1)
        pygame.draw.circle(fuelP, COLOR['fuelPackage'], [10, 10], 5, 5)
        pygame.draw.circle(fuelP, COLOR['fuel'], [10, 10], 10, 1)
        #pygame.draw.polygon(fuelP, COLOR['fuel'], ((9, 9), (9, 9), (9, 9)), 0)
        #pygame.draw.rect(fuelP, COLOR['fuel'], (9, 9, 2, 2), 1)

        self.screen.blit(fuelP, (self.x - fuelP.get_width() / 2, self.y - fuelP.get_height() / 2))

if __name__ == "__main__":
    logger.info('Starting...')
    c = Controller()
    c.run()
