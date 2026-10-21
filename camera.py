import math
import glm

class Camera:
    def __init__(self, position=(0.0, 3.0, 7.0), yaw=-90.0, pitch=-15.0, fov=45.0):
        self.position = glm.vec3(*position)
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw = float(yaw)
        self.pitch = float(pitch)
        self.fov = float(fov)

        self.speed = 4.5
        self.sensitivity = 0.1

        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.right = glm.vec3(1.0, 0.0, 0.0)

        self.update_vectors()

    def update_vectors(self):
        rad_yaw = glm.radians(self.yaw)
        rad_pitch = glm.radians(self.pitch)

        front = glm.vec3()
        front.x = math.cos(rad_yaw) * math.cos(rad_pitch)
        front.y = math.sin(rad_pitch)
        front.z = math.sin(rad_yaw) * math.cos(rad_pitch)

        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def get_projection_matrix(self, aspect):
        return glm.perspective(glm.radians(self.fov), aspect, 0.1, 100.0)

    def process_keyboard(self, direction, dt):
        velocity = self.speed * dt
        if direction == "FORWARD":
            self.position += self.front * velocity
        elif direction == "BACKWARD":
            self.position -= self.front * velocity
        elif direction == "LEFT":
            self.position -= self.right * velocity
        elif direction == "RIGHT":
            self.position += self.right * velocity
        elif direction == "UP":
            self.position += self.world_up * velocity
        elif direction == "DOWN":
            self.position -= self.world_up * velocity

    def process_mouse(self, dx, dy):
        self.yaw += dx * self.sensitivity
        self.pitch += dy * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))
        self.update_vectors()
