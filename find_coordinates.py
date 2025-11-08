import cv2
import numpy as np


img = cv2.imread("trial.png")
if img is None:
    raise ValueError("Image not found or cannot be opened.")

# Resize image to fit within 1000x800 window (adjust as needed)
max_width, max_height = 1000, 800
h, w = img.shape[:2]
scale = min(max_width / w, max_height / h, 1.0)
display_img = cv2.resize(img, (int(w * scale), int(h * scale)))
clone = display_img.copy()
working_copy = display_img.copy()
coords = []
current_box = []  # Store temporary points for current box


def click_event(event, x, y, flags, params):
    global clone, working_copy, current_box

    if event == cv2.EVENT_LBUTTONDOWN:
        # Convert display coordinates back to original image coordinates
        orig_x = int(x / scale)
        orig_y = int(y / scale)
        if len(current_box) == 0:
            # First click - start of box
            current_box = [(orig_x, orig_y)]
            print(f"Box started at: ({orig_x}, {orig_y})")

            # Draw starting point
            cv2.circle(clone, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("form", clone)

        else:
            # Second click - end of box
            current_box.append((orig_x, orig_y))
            start_x, start_y = current_box[0]
            end_x, end_y = current_box[1]

            # Ensure coordinates are properly ordered (top-left to bottom-right)
            x1 = min(start_x, end_x)
            y1 = min(start_y, end_y)
            x2 = max(start_x, end_x)
            y2 = max(start_y, end_y)

            # Store the box coordinates
            box_coords = {
                'top_left': (x1, y1),
                'bottom_right': (x2, y2),
                'width': x2 - x1,
                'height': y2 - y1
            }
            coords.append(box_coords)

            print(f"Box completed: ({x1}, {y1}) to ({x2}, {y2})")
            print(f"Box {len(coords)}: width={x2-x1}, height={y2-y1}")

            # Draw the rectangle on the display image
            disp_x1 = int(x1 * scale)
            disp_y1 = int(y1 * scale)
            disp_x2 = int(x2 * scale)
            disp_y2 = int(y2 * scale)
            cv2.rectangle(clone, (disp_x1, disp_y1), (disp_x2, disp_y2), (0, 255, 0), 2)

            # Add box number
            cv2.putText(clone, str(len(coords)), (disp_x1, disp_y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("form", clone)

            # Reset for next box
            current_box = []

    elif event == cv2.EVENT_RBUTTONDOWN:
        # Right click to cancel current box
        if current_box:
            print("Box drawing cancelled")
            # Restore image without the starting point
            clone = working_copy.copy()
            cv2.imshow("form", clone)
            current_box = []


def reset_image():
    """Reset image to original display size"""
    global clone, working_copy, coords, current_box
    clone = display_img.copy()
    working_copy = display_img.copy()
    coords = []
    current_box = []
    cv2.imshow("form", clone)
    print("Image reset")

print("Instructions:")
print("- LEFT CLICK: First click = top-left corner, Second click = bottom-right corner")
print("- RIGHT CLICK: Cancel current box")
print("- Press 'r' to reset image")
print("- Press 'q' to quit and save coordinates")
print("- Press 'd' to delete last box")


cv2.imshow("form", clone)
cv2.setMouseCallback("form", click_event)

while True:
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('r'):
        reset_image()
    elif key == ord('d'):
        if coords:
            deleted = coords.pop()
            print(f"Deleted box: {deleted}")
            reset_image()
            # Redraw all remaining boxes
            for i, box in enumerate(coords):
                x1, y1 = box['top_left']
                x2, y2 = box['bottom_right']
                disp_x1 = int(x1 * scale)
                disp_y1 = int(y1 * scale)
                disp_x2 = int(x2 * scale)
                disp_y2 = int(y2 * scale)
                cv2.rectangle(clone, (disp_x1, disp_y1), (disp_x2, disp_y2), (0, 255, 0), 2)
                cv2.putText(clone, str(i+1), (disp_x1, disp_y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("form", clone)

cv2.destroyAllWindows()

print("\nFinal Box Coordinates:")
for i, box in enumerate(coords):
    print(f"Box {i+1}:")
    print(f"  Top-left: {box['top_left']}")
    print(f"  Bottom-right: {box['bottom_right']}")
    print(f"  Width: {box['width']}, Height: {box['height']}")

# Save to JSON format compatible with your field_config
print("\nJSON format for field_config.json:")
field_config = {}
for i, box in enumerate(coords):
    field_name = f"field_{i+1}"  # You can rename these
    field_config[field_name] = {
        "x": box['top_left'][0],
        "y": box['top_left'][1],
        "width": box['width'],
        "height": box['height']
    }

print(field_config)

# Optional: Save to file
save_to_file = input("\nSave to file? (y/n): ").lower().strip()
if save_to_file == 'y':
    filename = input("Enter filename (e.g., field_config.json): ").strip()
    if not filename.endswith('.json'):
        filename += '.json'
    
    import json
    with open(filename, 'w') as f:
        json.dump(field_config, f, indent=2)
    print(f"Coordinates saved to {filename}")