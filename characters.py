from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import *
from kivy.app import App
import constants
"""
  Class: CharacterManager
  Description: Manages all characters and their behaviour.
"""
class CharacterManager(Widget):
  """
    Constructor
  """
  def __init__(self, **kwargs):
    super(CharacterManager, self).__init__(**kwargs)
    self.scorer = Scorer()
    self.scorer.pos = constants.SCORER_POS
    self.add_widget(self.scorer)

    mc_sources = {
      constants.STAND_RIGHT: constants.MC_STAND_RIGHT,
      constants.STAND_LEFT: constants.MC_STAND_LEFT,
      constants.STAND_ATTACK_LEFT: constants.MC_STAND_ATTACK_LEFT,
      constants.STAND_ATTACK_RIGHT: constants.MC_STAND_ATTACK_RIGHT,
      constants.RUNNING_LEFT: constants.MC_RUNNING_LEFT,
      constants.RUNNING_RIGHT: constants.MC_RUNNING_RIGHT,
      constants.DAMAGED: constants.MC_DAMAGED,
      constants.DEAD: constants.MC_DEAD
    }
    self.main_character = MainCharacter(mc_sources, constants.MC_LIFE_MAX)
    self.add_widget(self.main_character)

  """
    Method: on_enter
    Description: Method to be called when the sprite enters the game.
  """
  def on_enter(self):
    self.difficulty = self.parent.parent.difficulty
    Clock.schedule_interval(self.check_collisions, 0)

    self.main_character.on_enter()
    self.scorer.reset()

  """
    Method: on_leave
    Description: Method to be called when the sprite exits the game.
  """
  def on_leave(self):
    Clock.unschedule(self.check_collisions)
    self.main_character.on_leave()

  """
    Method: check_collisions
    Description: Method that checks for collisions.
  """
  def check_collisions(self, dt):
    pass

#---------------------------------------------------------------------------------

"""
  Class: Character
  Description: A character that has life and can move around the screen.
    Has a life meter and various images for different action.
"""
class Character(Image):
  alive = BooleanProperty(True)
  to_right = BooleanProperty(True)
  moving = BooleanProperty(True)
  jumping = BooleanProperty(False)
  attacking = BooleanProperty(False)
  """
    Constructor
  """
  def __init__(self, sources, max_life, **kwargs):
    super(Character, self).__init__(**kwargs)
    self.sources = sources
    self.life_meter = LifeMeter(max=max_life)
    self.add_widget(self.life_meter)
    self.sources = sources
    self.change_src(constants.STAND_RIGHT)
    self.life_meter.pos = (self.x, self.y + self.height + 100)

  """
    Method: on_enter
    Description: Method to be called when the sprite enters the game.
  """
  def on_enter(self):
    self.alive, self.to_right, self.moving, self.jumping, self.attacking  = True, True, True, False, False
    self.life_meter.reset()
    Clock.schedule_interval(self.check_life, 0)
    Clock.schedule_interval(self.check_movement_images, 0)
    Clock.schedule_interval(self.check_jumping, 0)

  """
    Method: on_leave
    Description: Method to be called when the sprite exits the game.
  """
  def on_leave(self):
    Clock.unschedule(self.check_life)
    Clock.unschedule(self.check_movement_images)
    Clock.unschedule(self.check_jumping)

  """
    Method: check_life
    Description: Method that checks if the character is alive or dead.
  """
  def check_life(self, dt):
    self.life_meter.pos = (self.x, self.y + self.height)
    if self.life_meter.value <= 0:
      self.alive = False

  """
    method: check_jumping
    description: method that checks if the character is jumping.
  """
  def check_jumping(self, dt):
    if self.y != constants.STANDING_Y:
      self.jumping = True
    else:
      self.jumping = False

  """
    Method: attack
    Description: Method used to make the character attack.
  """
  def attack(self):
    if not self.attacking and self.alive:
      if self.to_right:
        self.change_src(constants.STAND_ATTACK_RIGHT)
      else:
        self.change_src(constants.STAND_ATTACK_LEFT)
      self.attacking = True
      Clock.schedule_once(self.change_back, 0.3)

  """
    Method: change_back
    Description: Changes the character back to its proper image.
  """
  def change_back(self, dt):
    if self.to_right:
      self.change_src(constants.STAND_RIGHT)
    else:
      self.change_src(constants.STAND_LEFT)
    self.attacking = False

  """
    Method: jump
    Description: Method used to make the character jump.
  """
  def jump(self):
    if not self.jumping:
      anim = Animation(
        y=constants.JUMP_HEIGHT,
        duration=constants.JUMP_DURATION
      ) + Animation(
        y=constants.STANDING_Y,
        duration=constants.JUMP_DURATION
      )
      anim.start(self)

  """
    Method: check_movement_images
    Description: Method that changes the source base on the movement variables.
  """
  def check_movement_images(self, dt):
    if self.alive and not self.attacking:
      if to_right:
        if moving:
          self.change_src(constants.RUNNING_RIGHT)
        else:
          self.change_src(constants.STAND_RIGHT)
      else:
        if moving:
          self.change_src(constants.RUNNING_LEFT)
        else:
          self.change_src(constants.STAND_LEFT)
    else:
      self.change_src(constants.DEAD)

  """
    Method: change_src
    Description: Changes the source of the image.
  """
  def change_src(self, key):
    if self.source != self.sources[key]:
      self.source = self.sources[key]
      self.size = self.texture_size

#---------------------------------------------------------------------------------

"""
  Class: MainCharacter
  Description: The avatar that the user controls.
"""
class MainCharacter(Character):
  """
    Constructor
  """
  keyboard_on = BooleanProperty(False)
  on_battle = BooleanProperty(False)
  def __init__(self, sources, max_life, **kwargs):
    super(MainCharacter, self).__init__(sources, max_life, **kwargs)
    self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
    self._keyboard.bind(on_key_down=self._on_keyboard_down)
    self._keyboard.bind(on_key_up=self._on_keyboard_up)
    self.pos = (constants.MC_X, constants.STANDING_Y)

  def _keyboard_closed(self):
    if self.alive and self.keyboard_on:
      self._keyboard.unbind(on_key_down=self._on_keyboard_down)
      self._keyboard.unbind(on_key_up=self._on_keyboard_up)
      self._keyboard = None

  def on_touch_down(self, touch):
    if self.alive:
      self.attack()
      return super(Character, self).on_touch_down(touch)

  def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if self.alive and self.keyboard_on:
      if self.on_battle:
        if keycode[1] == "d":
          self.moving, self.to_right = True, True
        elif keycode[1] == "a":
          self.moving, self.to_right = True, False
      else:
        if keycode[1] == "w":
          self.jump()

  def _on_keyboard_up(self, keyboard, keycode):
    if self.alive and self.keyboard_on and self.on_battle:
      if keycode[1] == "d":
        self.moving = False
      elif keycode[1] == "a":
        self.moving = False

  # OVERRIDEN METHODS
  """
    Method: on_enter
    Description: Method to be called when the sprite enters the game.
  """
  def on_enter(self):
    super(MainCharacter, self).on_enter()
    self.on_battle, self.keyboard_on = False, True
    Clock.schedule_interval(self.check_moving, 0)

  """
    Method: on_leave
    Description: Method to be called when the sprite exits the game.
  """
  def on_leave(self):
    super(MainCharacter, self).on_leave()
    self.keyboard_on = False
    Clock.unschedule(self.check_moving)

  """
    Method: check_movement_images
    Description: Method that changes the source base on the movement variables.
  """
  def check_movement_images(self, dt):
    if not self.attacking:
      if self.on_battle or not self.alive:
        super(MainCharacter, self).check_movement_images(dt)
      else:
        self.change_src(constants.RUNNING_RIGHT)

  """
    Method: check_moving
    Description: Method that checks if the character is moving. This moves the bg.
  """
  def check_moving(self, dt):
    if not self.on_battle:
      self.parent.parent.background.move_all()

  """
    Method: change_back
    Description: Changes the character back to its proper image.
  """
  def change_back(self, dt):
    if self.on_battle:
      super(MainCharacter, self).change_back(dt)
    else:
      self.change_src(constants.RUNNING_RIGHT)
    self.attacking = False

#---------------------------------------------------------------------------------

# OTHER CLASSES
"""
  Class: LifeMeter
  Description: A bar showing how much life characters still has.
"""
class LifeMeter(ProgressBar):
  """
    Constructor
  """
  def __init__(self, **kwargs):
    super(LifeMeter, self).__init__(**kwargs)
    self.value = self.max
    self.width = self.max * 1.5

  """
    Method: decrease_life
    Description: Decreases life by the value passed.
  """
  def decrease_life(self, dmg):
    self.value -= dmg

  """
    Method: reset
    Description: Resets the life meter to its old value.
  """
  def reset(self):
    self.value = self.max

#---------------------------------------------------------------------------------

"""
  Class: Scorer
  Description: Shows the current score the user acquired.
"""
class Scorer(Label):
  """
    Constructor
  """
  def __init__(self, **kwargs):
    super(Scorer, self).__init__(font_size="80px", markup=True, **kwargs)
    Clock.schedule_interval(self.update_text, 0)
    self.score = 0

  """
    Method: update_text
    Description: Updates the text to the current score.
  """
  def update_text(self, dt):
    self.text = '[color=79C99A]' + constants.SCORE_TEXT + str(self.score) + '[/color]'

  """
    Method: reset
    Description: Resets the score to 0.
  """
  def reset(self):
    self.score = 0

#---------------------------------------------------------------------------------
