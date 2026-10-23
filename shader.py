from OpenGL.GL import *
import glm


class Shader:
    def __init__(self, vertex_path, fragment_path):
        with open(vertex_path, "r", encoding="utf-8") as f:
            v_code = f.read()
        with open(fragment_path, "r", encoding="utf-8") as f:
            f_code = f.read()

        v_shader = self._compile(GL_VERTEX_SHADER, v_code)
        f_shader = self._compile(GL_FRAGMENT_SHADER, f_code)

        self.program = glCreateProgram()
        glAttachShader(self.program, v_shader)
        glAttachShader(self.program, f_shader)
        glLinkProgram(self.program)

        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(self.program).decode("utf-8"))

        glDeleteShader(v_shader)
        glDeleteShader(f_shader)

    def _compile(self, shader_type, source):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            raise RuntimeError(glGetShaderInfoLog(shader).decode("utf-8"))
        return shader

    def use(self):
        glUseProgram(self.program)

    def set_bool(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), int(value))

    def set_int(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), int(value))

    def set_float(self, name, value):
        glUniform1f(glGetUniformLocation(self.program, name), float(value))

    def set_vec3(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        if isinstance(value, glm.vec3):
            glUniform3f(loc, value.x, value.y, value.z)
        else:
            glUniform3f(loc, float(value[0]), float(value[1]), float(value[2]))

    def set_mat4(self, name, mat):
        loc = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(mat))