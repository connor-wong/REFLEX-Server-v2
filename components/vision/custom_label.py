import cv2
import numpy as np

# 2. Fixed Colours
fixed_colors = {
    'Face': '#F8F4E3',            
    'Tie your hair': "#706C61",
    'Wear long pants': "#E5446D",      
    'Wear covered shoes': "#FF8966", 
    'Wear short sleeve shirt': "#2A2B2A"
}

def hex_to_bgr(hex_color: str) -> tuple:
    """
    Convert a hex color string to a BGR tuple.
    
    Parameters:
        hex_color (str): Hex color string, e.g. "#FF5733" or "FF5733".
    
    Returns:
        tuple: BGR tuple of integers (B, G, R).
    """
    hex_color = hex_color.lstrip('#')
    # Extract the R, G, and B values from the hex string.
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    # OpenCV uses BGR order.
    return (b, g, r)

def rects_overlap(rect1: tuple, rect2: tuple) -> bool:
    """
    Check if two rectangles overlap.
    Each rect is defined as (x1, y1, x2, y2) where (x1,y1) is top-left
    and (x2,y2) is bottom-right.
    """
    x1, y1, x2, y2 = rect1
    ax1, ay1, ax2, ay2 = rect2
    # No overlap if one rectangle is completely to the left/right or above/below the other.
    if x2 <= ax1 or ax2 <= x1 or y2 <= ay1 or ay2 <= y1:
        return False
    return True

def custom_annotate_segmentation(
    image: np.ndarray,
    results,
    alpha: float = 0.4,
    font=cv2.FONT_HERSHEY_SIMPLEX,
    font_scale: float = 0.8,
    text_thickness: int = 2,
    box_thickness: int = 2
) -> np.ndarray:
    """
    Annotate segmentation results with fixed colors (from hex codes) and adjust label positions to avoid overlap.
    
    Parameters:
        image (np.ndarray): The original BGR image.
        results: The YOLO segmentation results object. Must include:
                 - results.masks.xy: List of polygons for each detection.
                 - results.boxes.xyxy: Bounding box coordinates.
                 - results.boxes.cls: Class indices.
                 - results.boxes.conf: Confidence values.
                 - results.names: Dict mapping class indices to labels.
        fixed_colors (dict): Mapping of class labels (e.g., "Wear mask") to hex color strings.
        alpha (float): Transparency factor for segmentation overlay.
        font: OpenCV font type.
        font_scale (float): Scale factor for text.
        text_thickness (int): Thickness for text.
        box_thickness (int): Thickness for bounding boxes.
    
    Returns:
        np.ndarray: The annotated image.
    """
    annotated_image = image.copy()
    overlay = image.copy()

    if not hasattr(results, "masks") or not hasattr(results.masks, "xy"):
        return annotated_image

    num_detections = len(results.masks.xy)

    # List to hold already drawn text rectangles (x1, y1, x2, y2)
    drawn_label_rects = []

    for i in range(num_detections):
        # Get segmentation polygon and convert to integers.
        pts = results.masks.xy[i].astype(np.int32)
        
        # Retrieve bounding box, class index, and confidence.
        x1, y1, x2, y2 = results.boxes.xyxy[i]
        class_id = int(results.boxes.cls[i])
        confidence = float(results.boxes.conf[i])
        
        # Retrieve label and choose a fixed color (if not found, default to light gray).
        label = results.names.get(class_id, "Unknown")
        hex_color = fixed_colors.get(label, "#C8C8C8")
        color = hex_to_bgr(hex_color)
        
        # 1. Fill the segmentation polygon on the overlay.
        cv2.fillPoly(overlay, [pts], color)
        
        # 2. Draw the bounding box.
        cv2.rectangle(
            annotated_image,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            color,
            thickness=box_thickness
        )
        
        if label != "Face":
            # label_text = f"{label} {confidence:.1f}"
            label_text = f"{label}"
            (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, text_thickness)
            
            # Set the initial position: above the bounding box.
            candidate_x = int(x1)
            candidate_y = int(y1) - 5
            
            # Define the text rectangle: (x1, y1 - text_height - baseline, x1 + text_width, y1)
            candidate_rect = (candidate_x, candidate_y - text_height - baseline, candidate_x + text_width, candidate_y)
            
            # Adjust position if overlaps with any already drawn label rectangles.
            # Try shifting upward by multiples of (text_height + baseline + 2).
            offset = 0
            while any(rects_overlap(candidate_rect, drawn_rect) for drawn_rect in drawn_label_rects):
                offset += (text_height + baseline + 2)
                # Try shifting upward:
                candidate_rect = (candidate_x,
                                candidate_y - text_height - baseline - offset,
                                candidate_x + text_width,
                                candidate_y - offset)
                # If shifting upward makes the label go off the top of the image, try shifting downward instead.
                if candidate_rect[1] < 0:
                    candidate_rect = (candidate_x,
                                    candidate_y + offset,
                                    candidate_x + text_width,
                                    candidate_y + text_height + baseline + offset)
                    # break out if candidate is within image; you can add additional checks here if needed.
                    break
            
            # Save the final rectangle position.
            drawn_label_rects.append(candidate_rect)
            
            # 4. Draw a filled rectangle as background for the label.
            cv2.rectangle(
                annotated_image,
                (candidate_rect[0], candidate_rect[1]),
                (candidate_rect[2], candidate_rect[3]),
                color,
                cv2.FILLED
            )
            
            # 5. Draw the label text in white.
            # Place the text baseline appropriately; if shifted upward, use the bottom of the rectangle.
            text_org = (candidate_rect[0], candidate_rect[3] - baseline)
            cv2.putText(
                annotated_image,
                label_text,
                text_org,
                font,
                font_scale,
                (255, 255, 255),
                text_thickness,
                lineType=cv2.LINE_AA
            )

    # 6. Blend the overlay (segmentation fill) with the annotated image.
    cv2.addWeighted(overlay, alpha, annotated_image, 1 - alpha, 0, annotated_image)

    return annotated_image

def custom_annotate(image, results, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.9, thickness=2):
    """
    Annotate image with bounding boxes and customized labels.

    Parameters:
        image (numpy.ndarray): The original image.
        results: The detection results object returned by YOLO.
        font: OpenCV font type (e.g., cv2.FONT_HERSHEY_SIMPLEX).
        font_scale (float): Font scale factor that controls the size of the font.
        thickness (int): The thickness of the text stroke.
        
    Returns:
        image (numpy.ndarray): The annotated image.
    """
    # Iterate through each detected bounding box.
    for box in results.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = box
        # Retrieve the label from the names dictionary.
        label = results.names[int(cls)]
        
        # Draw the bounding box.
        cv2.rectangle(
            image, 
            (int(x1), int(y1)), 
            (int(x2), int(y2)), 
            color=(255, 0, 0), 
            thickness=thickness
        )
        
        # Optionally, you can also compute the size of the text to create a filled background.
        ((text_width, text_height), _) = cv2.getTextSize(label, font, font_scale, thickness)
        text_offset_x, text_offset_y = int(x1), int(y1) - 10  # Position text above the box.
        
        # Draw a filled rectangle to put the text on for better visibility.
        cv2.rectangle(
            image,
            (text_offset_x, text_offset_y - text_height - 4),
            (text_offset_x + text_width, text_offset_y),
            (255, 0, 0),
            cv2.FILLED
        )
        
        # Draw the text label with the custom font and size.
        cv2.putText(
            image, 
            label, 
            (text_offset_x, text_offset_y - 2),  # Slight offset for aesthetics.
            font, 
            font_scale, 
            (255, 255, 255),  # White text for contrast.
            thickness,
            lineType=cv2.LINE_AA
        )
    return image

