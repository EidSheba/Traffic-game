import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import subprocess  # لاستدعاء ملف game.py

window_width = 500
window_height = 600

button_images = ["level1.png", "level2.png", "level3.png", "play.png"]
textures = []

selected_level = None
message = ""

btn_width = 200
btn_height = 60
x_pos = (window_width - btn_width) // 2

y_positions = [
    window_height - 201,
    window_height - 201 - (btn_height + 29),
    window_height - 201 - 2*(btn_height + 29),
    window_height - 201 - 2*(btn_height + 29) - btn_height - 33
]

def load_textures():
    global textures
    textures = glGenTextures(len(button_images))

    for i, path in enumerate(button_images):
        surface = pygame.image.load(path)
        surface = pygame.transform.flip(surface, False, True)
        width, height = surface.get_size()
        img_data = pygame.image.tostring(surface, "RGBA", 1)

        glBindTexture(GL_TEXTURE_2D, textures[i])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

def load_texture(path, flip_y=False):
    surface = pygame.image.load(path)
    if flip_y:
        surface = pygame.transform.flip(surface, False, True)
    image = pygame.image.tostring(surface, "RGBA", 1)
    width, height = surface.get_size()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return tex_id, width, height

def draw_button(texture_id, x, y, w, h):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x, y + h)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_background(texture_id, width, height):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(0, 0)
    glTexCoord2f(1, 0); glVertex2f(width, 0)
    glTexCoord2f(1, 1); glVertex2f(width, height)
    glTexCoord2f(0, 1); glVertex2f(0, height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_cloud(x, y, width, height, texture_id):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + width, y)
    glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
    glTexCoord2f(0, 1); glVertex2f(x, y + height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def init_opengl():
    glClearColor(0.2, 0.2, 0.2, 1)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if 'bg_texture_id' in globals():
        draw_background(bg_texture_id, window_width, window_height)

    if 'cloud1_texture_id' in globals() and 'cloud2_texture_id' in globals():
        draw_cloud(cloud1_x, cloud1_y, cloud_w, cloud_h, cloud1_texture_id)
        draw_cloud(cloud2_x, cloud2_y, cloud_w, cloud_h, cloud2_texture_id)

    for i in range(4):
        draw_button(textures[i], x_pos, y_positions[i], btn_width, btn_height)

    if message:
        draw_text(20, 20, message)

    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)

def mouse(button, state, x, y):
    global selected_level, message

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        ogl_y = window_height - y

        for i in range(4):
            if x_pos <= x <= x_pos + btn_width and y_positions[i] <= ogl_y <= y_positions[i] + btn_height:
                if i < 3:
                    selected_level = i + 1
                    message = f"Level {selected_level} selected"
                else:  # Clicked the "Play" button
                    if selected_level is None:
                        message = "Choose a level first"
                    else:
                        message = f"Starting level {selected_level}..."
                        try:
                            subprocess.Popen(["python", "game.py", str(selected_level)])
                            # يمكنك هنا إغلاق نافذة القائمة إذا أردت
                            # pygame.quit()
                            # sys.exit()
                        except FileNotFoundError:
                            message = "Error: game.py not found!"
                        except Exception as e:
                            message = f"Error starting game: {e}"
                break

    glutPostRedisplay()

def update(value):
    global cloud1_x, cloud2_x, cloud_w

    cloud1_x -= 1
    if cloud1_x < -cloud_w:
        cloud1_x = window_width

    cloud2_x += 1
    if cloud2_x > window_width:
        cloud2_x = -cloud_w

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def init():
    pygame.init()
    init_opengl()
    load_textures()

    try:
        global bg_texture_id, cloud1_texture_id, cloud2_texture_id, cloud_w, cloud_h
        global cloud1_x, cloud1_y, cloud2_x, cloud2_y

        bg_texture_id, _, _ = load_texture("background.png", flip_y=False)
        cloud1_texture_id, cloud_w, cloud_h = load_texture("cloud.png", flip_y=True)
        cloud2_texture_id, _, _ = load_texture("cloud2.png", flip_y=True)

        cloud1_x = window_width
        cloud1_y = window_height * 0.55

        cloud2_x = -cloud_w
        cloud2_y = window_height * 0.7

        glutTimerFunc(0, update, 0)
    except:
        print("Some graphics files are missing, only buttons will be displayed")

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Interface")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    init()
    glutMainLoop()

if __name__ == "__main__":
    main()