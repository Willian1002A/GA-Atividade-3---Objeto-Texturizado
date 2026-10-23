import os
import sys
import glfw
import glm
from OpenGL.GL import *

from shader import Shader
from obj_loader import load_obj, parse_mtl, load_texture


def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(800, 600, "GA Atividade 3 - Objeto Texturizado", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.15, 1.0)

    # Carrega os shaders
    shader = Shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")

    # Carrega a malha e os dados do material (.mtl)
    obj_path = "assets/pillar.obj"
    base_dir = os.path.dirname(os.path.abspath(obj_path))

    vao, vertex_count, mtl_filename = load_obj(obj_path)
    mtl_path = os.path.join(base_dir, mtl_filename) if mtl_filename else None
    texture_path = parse_mtl(mtl_path)
    texture_id = load_texture(texture_path)

    print(f"Modelo carregado: {obj_path} | Textura: {texture_path}")

    view = glm.lookAt(glm.vec3(0.0, 1.5, 5.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))

    while not glfw.window_should_close(window):
        width, height = glfw.get_framebuffer_size(window)
        glViewport(0, 0, width, height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader.use()

        # Matrizes de transformação
        projection = glm.perspective(glm.radians(45.0), width / max(height, 1), 0.1, 100.0)
        model = glm.rotate(glm.mat4(1.0), glfw.get_time() * 0.5, glm.vec3(0.0, 1.0, 0.0))
        mvp = projection * view * model

        shader.set_mat4("mvp", mvp)

        # Textura
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        shader.set_int("tex", 0)

        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, vertex_count)
        glBindVertexArray(0)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()