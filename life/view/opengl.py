import logging
import sys

import numpy as np
from glumpy import app, gl, glm, gloo, log
from matplotlib import cm as colormaps

try:
    import glfw
except ImportError:
    glfw = None

from ..model import Board

log.setLevel(logging.INFO)


class Display:
    """OpenGL display class.

    This class implements OpenGL display using glumpy engine.
    """

    CTYPE = [('a_position', np.float32, 2), ('a_color', np.float32, 3)]
    GTYPE = [('a_position', np.float32, 2)]

    CUBE_VERTEX_SHADER = """
        in  vec2 a_position;    // Vertex position
        in  vec3 a_color;       // Vertex color
        out vec3 v_color;       // Interpolated fragment color (out)

        void main()
        {
            gl_Position = vec4(a_position, 0.5, 1.0);
            v_color = a_color;
        }
    """

    CUBE_GEOMETRY_SHADER = """
        layout (points) in;
        layout (triangle_strip, max_vertices=24) out;

        uniform mat4    u_view;          // View matrix
        uniform mat4    u_projection;    // Projection matrix
        in      vec3    v_color[];       // Interpolated fragment color (in)
        out     vec3    f_color;         // Interpolated fragment color (in)

        void main()
        {
            vec4 pos = gl_in[0].gl_Position;
            mat4 mvp = u_projection * u_view;

            f_color = v_color[0];
            gl_Position = mvp * (pos + vec4(0.5, 0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, 0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(0.5, -0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, -0.5, 0.5, 0));
            EmitVertex();
            EndPrimitive();

            f_color = 0.8 * v_color[0];
            gl_Position = mvp * (pos + vec4(0.5, 0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(0.5, -0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(0.5, 0.5, -0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(0.5, -0.5, -0.5, 0));
            EmitVertex();
            EndPrimitive();

            f_color = 0.6 * v_color[0];
            gl_Position = mvp * (pos + vec4(0.5, -0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, -0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(0.5, -0.5, -0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, -0.5, -0.5, 0));
            EmitVertex();
            EndPrimitive();

            f_color = 0.4 * v_color[0];
            gl_Position = mvp * (pos + vec4(0.5, 0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(0.5, 0.5, -0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, 0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, 0.5, -0.5, 0));
            EmitVertex();
            EndPrimitive();

            f_color = 0.3 * v_color[0];
            gl_Position = mvp * (pos + vec4(-0.5, 0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, 0.5, -0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, -0.5, 0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, -0.5, -0.5, 0));
            EmitVertex();
            EndPrimitive();

            f_color = 0.1  * v_color[0];
            gl_Position = mvp * (pos + vec4(0.5, 0.5, -0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(0.5, -0.5, -0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, 0.5, -0.5, 0));
            EmitVertex();
            gl_Position = mvp * (pos + vec4(-0.5, -0.5, -0.5, 0));
            EmitVertex();
            EndPrimitive();
        }
    """

    CUBE_FRAGMENT_SHADER = """
        in vec3 f_color;    // Interpolated fragment color (in)

        void main()
        {
            gl_FragColor = vec4(f_color, 1);
        }
    """

    GRID_VERTEX_SHADER = """
        in      vec2    a_position;     // Vertex position
        uniform mat4    u_view;         // View matrix
        uniform mat4    u_projection;   // Projection matrix

        void main() {
            gl_Position = u_projection * u_view * vec4(a_position, 0.0, 1.0);
        }
    """

    GRID_FRAGMENT_SHADER = """
        void main() {
            gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0);
        }
    """

    def __init__(self, board, cmap='viridis'):
        """Initialize OpenGL display.

        Args:
            board (Board): board instance providing game logic
            cmap (str): color map name
        """
        sys.real_argv = sys.argv[:]
        sys.argv = sys.argv[:1]

        self.running = True
        self.board = board

        # Get possible colors from Matplotlib and store them for future use as RGB tuples
        cmap = getattr(colormaps, cmap)
        self.colors = np.array([color[:3] for color in (cmap(val / board.steps) for val in range(board.steps + 1))])

        # Initialize the window
        if glfw is not None:
            app.use('glfw')
        self.window = app.Window(width=1920, height=1080)
        self.window.set_handler('on_init', self.on_init)
        self.window.set_handler('on_resize', self.on_resize)
        self.window.set_handler('on_draw', self.on_draw)
        self.window.set_handler('on_key_press', self.on_key_press)
        self.window.set_handler('on_key_release', self.on_key_release)
        self.window.set_handler('on_mouse_scroll', self.on_mouse_scroll)
        self.window.set_handler('on_mouse_press', self.on_mouse_press)
        self.window.set_handler('on_mouse_release', self.on_mouse_release)
        self.window.set_handler('on_mouse_drag', self.on_mouse_drag)
        self._shift = False
        self._toggled = None

        self.cubes = gloo.Program(self.CUBE_VERTEX_SHADER, self.CUBE_FRAGMENT_SHADER, self.CUBE_GEOMETRY_SHADER, version=330)

        self.offset = np.array(board.size)[::-1] / 2 - 0.5

        self.mesh = np.mgrid[0:board.size[1], 0:board.size[0]].reshape(2, -1).T.astype(np.float32)
        self.mesh -= self.offset[None, :]

        self.make_cubes()

        grid_offset = self.offset + 0.5

        gridx = np.arange(-grid_offset[0], grid_offset[0] + 0.5, 1.)
        gridy = np.arange(-grid_offset[1], grid_offset[1] + 0.5, 1.)

        xlines = np.array([[[x, -grid_offset[1]], [x, grid_offset[1]]] for x in gridx], np.float32).reshape(-1, 2)
        ylines = np.array([[[-grid_offset[0], y], [grid_offset[0], y]] for y in gridy], np.float32).reshape(-1, 2)

        lines = np.zeros(xlines.shape[0] + ylines.shape[0], self.CTYPE)
        lines['a_position'] = np.concatenate([xlines, ylines], axis=0)

        self.grid = gloo.Program(self.GRID_VERTEX_SHADER, self.GRID_FRAGMENT_SHADER, version=330)
        self.grid.bind(lines.view(gloo.VertexBuffer))

    def on_init(self):
        """Initialize OpenGL context."""
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        self._t = 0

    def animate(self, fps):
        """Start animation.

        Args:
            fps (int): frames per second
        """
        # Initialize the view and projection matrices
        self.projection = np.eye(4, dtype=np.float32)
        self.reset_view()

        self._t = 0
        self._updt = 1. / fps

        app.run()

    def reset_view(self):
        """Reset view matrix."""
        self.view = np.eye(4, dtype=np.float32)
        glm.translate(self.view, 0, 0, -self.board.size[1] * 2**0.5)
        self.cubes['u_view'] = self.view
        self.grid['u_view'] = self.view

    def make_cubes(self):
        """Update cube positions and colors for OpenGL."""
        board = self.board.data[::-1, :].T.ravel()
        mask = board > 0
        pixels = np.zeros(np.sum(mask), self.CTYPE)
        pixels['a_position'] = self.mesh[mask]
        pixels['a_color'] = self.colors[board[mask]]
        self.cubes.bind(pixels.view(gloo.VertexBuffer))

    def update_board(self):
        """Update board state."""
        self.board.update()
        self.make_cubes()

    def on_resize(self, width, height):
        """Update projection matrix on window resize."""
        ratio = width / height
        self.projection = glm.perspective(45.0, ratio, 0.1, 500.0)
        self.cubes['u_projection'] = self.projection
        self.grid['u_projection'] = self.projection

    def on_draw(self, dt):
        """Draw the screen."""
        if self.running:
            self._t += dt
            if self._t >= self._updt:
                self._t = 0
                self.update_board()
        self.window.clear()
        self.grid.draw(gl.GL_LINES)
        self.cubes.draw(gl.GL_POINTS)

    def on_key_press(self, key, modifiers):
        if key == app.window.key.SPACE:
            self.running = not self.running
        elif key == ord('R'):
            self.reset_view()
        elif key == ord('F'):
            self.window.set_fullscreen(not self.window.get_fullscreen())
        elif key == ord('Q'):
            self.window.close()
        elif key == app.window.key.LSHIFT:
            self._shift = True
        else:
            # Shift board on arrows
            dir = {
                app.window.key.LEFT: Board.LEFT,
                app.window.key.RIGHT: Board.RIGHT,
                app.window.key.UP: Board.UP,
                app.window.key.DOWN: Board.DOWN
            }.get(key)
            if dir is not None:
                self.board.roll(dir)
                self.make_cubes()

    def on_key_release(self, key, modifiers):
        if key == app.window.key.LSHIFT:
            self._shift = False

    def on_mouse_scroll(self, x, y, dx, dy):
        self.view = glm.translate(self.view, 0, 0, dy)
        self.cubes['u_view'] = self.view
        self.grid['u_view'] = self.view

    def raycast(self, x, y):
        # Glumpy uses transposed matrices
        view, projection = self.view.T.copy(), self.projection.T
        iview = np.linalg.inv(view)
        camera = -iview[:3, 3]
        x = 2 * x / self.window.width - 1
        y = 1 - 2 * y / self.window.height
        ray = np.linalg.inv(projection) @ np.array([x, y, -1, 1], float)
        ray = (iview @ np.array([ray[0], ray[1], -1, 0]))[:3]
        ray /= np.linalg.norm(ray)
        t = -camera[2] / ray[2]
        pos = (camera + t * ray)[:2] + self.offset
        pos[0] = self.board.size[1] - 1 - pos[0]
        j, i = np.round(pos).astype(int)
        return i, j

    def toggle_cube(self, x, y, drag=False):
        i, j = self.raycast(x, y)
        if 0 <= i < self.board.size[0] and 0 <= j < self.board.size[1]:
            if drag and self._toggled == (i, j):
                return
            self._toggled = (i, j)
            self.board.toggle(i, j)
            self.make_cubes()

    def on_mouse_press(self, x, y, button):
        'A mouse button was pressed.'
        if button in (app.window.mouse.RIGHT, app.window.mouse.MIDDLE):
            if glfw is not None:
                glfw.set_input_mode(self.window._native_window, glfw.CURSOR, glfw.CURSOR_HIDDEN)
        elif button == app.window.mouse.LEFT:
            self.toggle_cube(x, y)

    def on_mouse_release(self, x, y, button):
        'A mouse button was released.'
        if button in (app.window.mouse.RIGHT, app.window.mouse.MIDDLE):
            if glfw is not None:
                glfw.set_input_mode(self.window._native_window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def on_mouse_drag(self, x, y, dx, dy, buttons):
        if buttons == app.window.mouse.RIGHT:
            if self._shift:
                self.view = glm.rotate(self.view, 0.1 * dx, 0, 1, 0)
                self.view = glm.rotate(self.view, 0.1 * dy, 1, 0, 0)
            else:
                self.view = glm.rotate(np.eye(4), 0.1 * dx, 0, 0, 1) @ self.view
                axis = self.view[:3, :3] @ [1, 0, 0]
                self.view = glm.rotate(np.eye(4), 0.1 * dy, axis[0], axis[1], 0) @ self.view
            self.cubes['u_view'] = self.view
            self.grid['u_view'] = self.view
        elif buttons == app.window.mouse.MIDDLE:
            self.view = glm.translate(self.view, 0.1 * dx, -0.1 * dy, 0)
            self.cubes['u_view'] = self.view
            self.grid['u_view'] = self.view
        elif buttons == app.window.mouse.LEFT:
            self.toggle_cube(x, y, True)
