import json
import glfw
from OpenGL.GL import *
import glm

from camera import Camera
from shader import Shader
from bezier import get_bezier_point
from obj_loader import load_obj, parse_mtl, load_texture


class Object3D:
    def __init__(self, name, vao, vbo, vertex_count, texture_id, material, pos, rot, scale, bezier_points=None, bezier_speed=0.35):
        self.name = name
        self.vao = vao
        self.vbo = vbo
        self.vertex_count = vertex_count
        self.texture_id = texture_id
        self.material = material

        self.pos = glm.vec3(*pos)
        self.rot = glm.vec3(*rot)
        self.scale = glm.vec3(*scale)

        self.init_pos = glm.vec3(*pos)
        self.init_rot = glm.vec3(*rot)
        self.init_scale = glm.vec3(*scale)

        self.bezier_points = [glm.vec3(*p) for p in bezier_points] if bezier_points else None
        self.bezier_speed = bezier_speed
        self.bezier_t = 0.0
        self.bezier_dir = 1.0

    def reset(self):
        self.pos = glm.vec3(self.init_pos)
        self.rot = glm.vec3(self.init_rot)
        self.scale = glm.vec3(self.init_scale)

camera = None
objects = []
lights = []
selected_idx = 0
use_texture = True
animation_paused = False
keys = {}

mouse_active = False
last_mouse_x = 0.0
last_mouse_y = 0.0


def key_callback(window, key, scancode, action, mods):
    global selected_idx, use_texture, animation_paused

    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_TAB:
            selected_idx = (selected_idx + 1) % len(objects)
            obj = objects[selected_idx]
            print(f"Objeto [{selected_idx + 1}]: {obj.name}")
        elif key == glfw.KEY_1:
            lights[0]["enabled"] = not lights[0]["enabled"]
            print(f"Luz 1: {'ON' if lights[0]['enabled'] else 'OFF'}")
        elif key == glfw.KEY_2:
            lights[1]["enabled"] = not lights[1]["enabled"]
            print(f"Luz 2: {'ON' if lights[1]['enabled'] else 'OFF'}")
        elif key == glfw.KEY_3:
            lights[2]["enabled"] = not lights[2]["enabled"]
            print(f"Luz 3: {'ON' if lights[2]['enabled'] else 'OFF'}")
        elif key == glfw.KEY_X:
            use_texture = not use_texture
            print(f"Textura: {'ON' if use_texture else 'OFF'}")
        elif key == glfw.KEY_SPACE:
            animation_paused = not animation_paused
            print(f"Animacao: {'PAUSADA' if animation_paused else 'RODANDO'}")

    if action == glfw.PRESS:
        keys[key] = True
    elif action == glfw.RELEASE:
        keys[key] = False


def mouse_button_callback(window, button, action, mods):
    global mouse_active, last_mouse_x, last_mouse_y
    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            mouse_active = True
            last_mouse_x, last_mouse_y = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            mouse_active = False


def cursor_pos_callback(window, xpos, ypos):
    global last_mouse_x, last_mouse_y
    if mouse_active:
        dx = xpos - last_mouse_x
        dy = last_mouse_y - ypos
        last_mouse_x, last_mouse_y = xpos, ypos
        camera.process_mouse(dx, dy)


def framebuffer_size_callback(window, width, height):
    # Atualiza a área de renderização do OpenGL ao redimensionar a janela
    if height > 0:
        glViewport(0, 0, width, height)


def process_inputs(dt):
    if keys.get(glfw.KEY_W, False): camera.process_keyboard("FORWARD", dt)
    if keys.get(glfw.KEY_S, False): camera.process_keyboard("BACKWARD", dt)
    if keys.get(glfw.KEY_A, False): camera.process_keyboard("LEFT", dt)
    if keys.get(glfw.KEY_D, False): camera.process_keyboard("RIGHT", dt)
    if keys.get(glfw.KEY_E, False): camera.process_keyboard("UP", dt)
    if keys.get(glfw.KEY_Q, False): camera.process_keyboard("DOWN", dt)

    if not objects: return
    obj = objects[selected_idx]
    v_speed = 2.5 * dt
    r_speed = 60.0 * dt
    s_speed = 1.0 * dt

    if keys.get(glfw.KEY_J, False): obj.pos.x -= v_speed
    if keys.get(glfw.KEY_L, False): obj.pos.x += v_speed
    if keys.get(glfw.KEY_U, False): obj.pos.y += v_speed
    if keys.get(glfw.KEY_O, False): obj.pos.y -= v_speed
    if keys.get(glfw.KEY_I, False): obj.pos.z -= v_speed
    if keys.get(glfw.KEY_K, False): obj.pos.z += v_speed

    if keys.get(glfw.KEY_R, False): obj.rot.x += r_speed
    if keys.get(glfw.KEY_F, False): obj.rot.x -= r_speed
    if keys.get(glfw.KEY_T, False): obj.rot.y += r_speed
    if keys.get(glfw.KEY_G, False): obj.rot.y -= r_speed
    if keys.get(glfw.KEY_Y, False): obj.rot.z += r_speed
    if keys.get(glfw.KEY_H, False): obj.rot.z -= r_speed

    if keys.get(glfw.KEY_N, False):
        obj.scale = glm.max(glm.vec3(0.05), obj.scale - glm.vec3(s_speed))
    if keys.get(glfw.KEY_M, False):
        obj.scale += glm.vec3(s_speed)


def update_bezier_animations(objects_list, dt, is_paused):
    if is_paused:
        return
    for obj in objects_list:
        if obj.bezier_points:
            obj.bezier_t += obj.bezier_dir * obj.bezier_speed * dt
            if obj.bezier_t >= 1.0:
                obj.bezier_t = 1.0
                obj.bezier_dir = -1.0
            elif obj.bezier_t <= 0.0:
                obj.bezier_t = 0.0
                obj.bezier_dir = 1.0


def update_shader_mat(shader, cam, window):
    w, h = glfw.get_framebuffer_size(window)
    glViewport(0, 0, w, h)
    aspect = w / max(1, h)
    shader.set_mat4("projection", cam.get_projection_matrix(aspect))
    shader.set_mat4("view", cam.get_view_matrix())
    shader.set_vec3("viewPos", cam.position)


def update_shader_lights(shader, lights_list):
    for i, light in enumerate(lights_list[:3]):
        shader.set_bool(f"lights[{i}].enabled", light["enabled"])
        shader.set_vec3(f"lights[{i}].position", light["position"])
        shader.set_vec3(f"lights[{i}].ambient", light["ambient"])
        shader.set_vec3(f"lights[{i}].diffuse", light["diffuse"])
        shader.set_vec3(f"lights[{i}].specular", light["specular"])
        shader.set_float(f"lights[{i}].constant", light.get("constant", 1.0))
        shader.set_float(f"lights[{i}].linear", light.get("linear", 0.09))
        shader.set_float(f"lights[{i}].quadratic", light.get("quadratic", 0.032))

def render_scene_objects(shader, objects_list, show_texture):
    shader.set_bool("useTexture", show_texture)

    for obj in objects_list:
        if obj.bezier_points:
            current_pos = get_bezier_point(*obj.bezier_points, obj.bezier_t)
        else:
            current_pos = obj.pos

        model = glm.mat4(1.0)
        model = glm.translate(model, current_pos)
        model = glm.rotate(model, glm.radians(obj.rot.x), glm.vec3(1, 0, 0))
        model = glm.rotate(model, glm.radians(obj.rot.y), glm.vec3(0, 1, 0))
        model = glm.rotate(model, glm.radians(obj.rot.z), glm.vec3(0, 0, 1))
        model = glm.scale(model, obj.scale)
        shader.set_mat4("model", model)

        shader.set_vec3("material.Ka", obj.material["Ka"])
        shader.set_vec3("material.Kd", obj.material["Kd"])
        shader.set_vec3("material.Ks", obj.material["Ks"])
        shader.set_float("material.shininess", obj.material["shininess"])

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, obj.texture_id)
        shader.set_int("texture_diffuse", 0)

        glBindVertexArray(obj.vao)
        glDrawArrays(GL_TRIANGLES, 0, obj.vertex_count)
        glBindVertexArray(0)


def load_scene(config_path):
    global camera, lights, objects

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cam_data = data.get("camera", {})
    camera = Camera(
        position=cam_data.get("position", [0.0, 3.0, 7.0]),
        yaw=cam_data.get("yaw", -90.0),
        pitch=cam_data.get("pitch", -15.0),
        fov=cam_data.get("fov", 45.0)
    )

    lights = data.get("lights", [])

    for item in data.get("objects", []):
        vao, vbo, count = load_obj(item["obj_path"])
        material = parse_mtl(item.get("mtl_path"))
        tex_path = item.get("texture_path") or material["texture_path"]
        tex_id = load_texture(tex_path)

        bezier_cfg = item.get("bezier_trajectory")
        bezier_pts = bezier_cfg["control_points"] if bezier_cfg else None
        bezier_spd = bezier_cfg.get("speed", 0.35) if bezier_cfg else 0.35

        obj = Object3D(
            name=item["name"],
            vao=vao,
            vbo=vbo,
            vertex_count=count,
            texture_id=tex_id,
            material=material,
            pos=item.get("position", [0, 0, 0]),
            rot=item.get("rotation", [0, 0, 0]),
            scale=item.get("scale", [1, 1, 1]),
            bezier_points=bezier_pts,
            bezier_speed=bezier_spd
        )
        objects.append(obj)


def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(1280, 720, "Visualizador 3D - Diorama", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)

    shader = Shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")
    load_scene("scene.json")

    print("Diorama iniciado. Controles: WASD, Teclas 1-3 (Luzes), TAB (Selecionar objeto), X (Textura), ESC (Sair)")
    
    last_time = glfw.get_time()

    # Loop principal de renderização
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time

        # Exibe coordenadas do objeto selecionado em tempo real no título da janela
        if objects:
            cur = objects[selected_idx]
            glfw.set_window_title(window, f"Diorama | [{selected_idx+1}] {cur.name} | Pos: [{cur.pos.x:.2f}, {cur.pos.y:.2f}, {cur.pos.z:.2f}]")

        # Processamento de entradas e física/animação
        process_inputs(dt)
        update_bezier_animations(objects, dt, animation_paused)

        # Renderização do frame
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        shader.use()

        update_shader_mat(shader, camera, window)
        update_shader_lights(shader, lights)
        render_scene_objects(shader, objects, use_texture)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
