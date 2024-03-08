import cv2
import numpy as np

# Global mouse coordinates
x_mouse = 0
y_mouse = 0

# Mouse events function
def mouse_events(event, x, y, flags, param):
    global x_mouse, y_mouse
    # Mouse movement event
    if event == cv2.EVENT_MOUSEMOVE:
        # Update global mouse coordinates
        x_mouse = x
        y_mouse = y

# Create a window to capture mouse events
cv2.namedWindow('gray8')
cv2.setMouseCallback('gray8', mouse_events)

# Initialize video capture
thermal_camera = cv2.VideoCapture(0)

if not thermal_camera.isOpened():
    print("Error: Unable to open video capture.")
    exit()

# Set up the thermal camera resolution
thermal_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
thermal_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

while True:
    # Grab the frame from the thermal camera stream
    grabbed, thermal_frame = thermal_camera.read()

    if not grabbed:
        print("Error: Failed to grab frame.")
        break

    # Calculate temperature
    temperature_pointer = thermal_frame[y_mouse, x_mouse][0]  # Accessing the first element of the array
    temperature_pointer = ((temperature_pointer / 100)) * 9 / 5 +32

    # Convert the gray16 image into a gray8
    thermal_frame_normalized = cv2.normalize(thermal_frame, None, 0, 255, cv2.NORM_MINMAX)
    thermal_frame_normalized = np.uint8(thermal_frame_normalized)

    # Colorize the gray8 image using OpenCV colormaps
    thermal_frame_colorized = cv2.applyColorMap(thermal_frame_normalized, cv2.COLORMAP_INFERNO)

    # Write pointer
    cv2.circle(thermal_frame_colorized, (x_mouse, y_mouse), 2, (255, 255, 255), -1)
    # Write temperature
    temperature_text = "{0:.1f} Fahrenheit".format(float(temperature_pointer))
    cv2.putText(thermal_frame_colorized, temperature_text, (x_mouse - 40, y_mouse - 15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    # Show the thermal frame
    cv2.imshow('gray8', thermal_frame_colorized)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
thermal_camera.release()
cv2.destroyAllWindows()
