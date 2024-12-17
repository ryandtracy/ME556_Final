import tkinter as tk
import numpy as np

# Create the main application window
root = tk.Tk()
root.title("Animated Robot Traveling in a Circle")

# Create a canvas to draw on
canvas_width = 3000
canvas_height = 1000
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()

# Central rectangle dimensions
BODY_WIDTH = 130
BW = BODY_WIDTH / 2  # this represents the body half width
BODY_HEIGHT = 100
BH = BODY_HEIGHT / 2  # this represents the body half height
LXY = BW + BH

# Corner rectangle dimensions
TIRE_WIDTH = 20
TIRE_DIAMETER = 47
r = TIRE_DIAMETER / 2  # tire radius

# Global parameters
DT = 0.05

# Draw the robot
def draw_robot(center_x, center_y, angle,RECT_COLOR,TIRE_COLOR,ARROW_COLOR):
    # Define offsets for all components relative to the robot's origin
    components = []

    # Central rectangle (blue)
    central_rect = [
        (-BW, -BH),
        (BW, -BH),
        (BW, BH),
        (-BW, BH)
    ]
    components.append((central_rect, RECT_COLOR))

    corner_offsets = [
        (-BW, -BH - TIRE_WIDTH),  # Top-left
        (BW - TIRE_DIAMETER, -BH - TIRE_WIDTH),  # Top-right
        (-BW, BH),  # Bottom-left
        (BW - TIRE_DIAMETER, BH)   # Bottom-right
    ]
    for dx, dy in corner_offsets:
        rect = [
            (dx, dy),
            (dx + TIRE_DIAMETER, dy),
            (dx + TIRE_DIAMETER, dy + TIRE_WIDTH),
            (dx, dy + TIRE_WIDTH)
        ]
        components.append((rect, TIRE_COLOR))

    # Green triangle (upward pointing)
    triangle_base_width = 60
    triangle_height = 80
    triangle = [
        (- triangle_height / 2, -triangle_base_width / 2),
        (- triangle_height / 2, triangle_base_width / 2),
        (triangle_height / 2, 0)
    ]
    components.append((triangle, ARROW_COLOR))

    # Draw all components with transformations
    for shape, color in components:
        transformed_points = []
        for x, y in shape:
            # Rotate
            rotated_x = x * np.cos(angle) - y * np.sin(angle)
            rotated_y = x * np.sin(angle) + y * np.cos(angle)
            # Translate
            translated_x = rotated_x + center_x
            translated_y = rotated_y + center_y
            transformed_points.append((translated_x, translated_y))

        # Flatten points for create_polygon
        flat_points = [coord for point in transformed_points for coord in point]
        canvas.create_polygon(flat_points, fill=color, outline="black", tags="robot")

def forwardKinematics(W): 
    F = np.array([[1, 1, 1, 1], [-1, 1, 1, -1], [-1/LXY, 1/LXY, -1/LXY, 1/LXY]])
    return (r / 4) * F @ W

def inverseKinematics(Xdot):
    J = np.array([[1, -1, -LXY], [1, 1, LXY], [1, 1, -LXY], [1, -1, LXY]])
    return (1/r) * J @ Xdot

def trajectory(traj,t):
    X = np.zeros([6,np.size(t)])
    X[0] = traj[0]
    X[1] = traj[1]
    X[3] = np.gradient(X[0],t)
    X[4] = np.gradient(X[1],t)
    for i in range(len(t)):
        X[2,i] = np.arctan2(X[4,i],X[3,i])
    X[5] = np.gradient(X[2],t)
    return X

#Trajectory 1
FREQ = 1/4
CYCLES = 1 / FREQ
PERIOD = CYCLES * 8 * np.pi 
t1 = np.arange(0,PERIOD,DT)
traj1_init = np.array([[canvas_width/2],[canvas_height/2]])
traj1 = np.zeros([2,np.size(t1)])
traj1[:,0] = traj1_init[:,0]
for i in range(len(t1)):
    traj1[0,i] = 10 * (t1[i] + 1) * np.sin(t1[i] * FREQ) + traj1_init[0,0]
    traj1[1,i] = 10 * (t1[i] + 1) * np.cos(t1[i] * FREQ) + traj1_init[1,0]

#Trajectory 2
FREQ = 1/2
CYCLES = 1 / FREQ
PERIOD = CYCLES * 2 * np.pi 
t2= np.arange(0,PERIOD,DT)
traj2_init = traj1[:,-1:]
traj2 = np.zeros([2,np.size(t2)])
traj2[:,0] = traj2_init[:,0]
for i in range(len(t2)):
    traj2[0,i] = -30 * t2[i] + traj2_init[0,0]
    traj2[1,i] = 300 * np.sin(t2[i] * FREQ) + 500 + traj2_init[1,0]


i = 0
Z = trajectory(traj1,t1)
X = Z[:3,0]
def animate():
    global X, i
    canvas.delete("robot")

    # Directly Commanded Trajectory
    W = inverseKinematics(Z[3:,i])

    X = X + forwardKinematics(W) * DT
    draw_robot(X[0],X[1],X[2],"green","black","red")
    i = i + 1

    # Create a persistent small circle at the robot's location
    circle_radius = 4
    canvas.create_oval(X[0] - circle_radius, X[1] - circle_radius, X[0] + circle_radius, X[1] + circle_radius, fill="blue", outline="blue", tags="persistent")
    canvas.after(5, animate)  # delay in milliseconds

# Start the animation
animate()

# Start the Tkinter event loop
root.mainloop()
