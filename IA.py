from operator import index

import cv2
import numpy as np


def format_yolov5(frame):
    # put the image in square big enough
    row, col, _ = frame.shape
    _max = max(col, row)
    result = np.zeros((_max, _max, 3), np.uint8)
    result[0:row, 0:col] = frame
    return result


def detect(image, net):
    # resize to 640x640, normalize to [0,1[ and swap Red and Blue channels
    blob = cv2.dnn.blobFromImage(image,
                                 1 / 255.0, (640, 640),
                                 swapRB=True,
                                 crop=False)
    net.setInput(blob)
    preds = net.forward()
    return preds


def unwrap_detection(input_image, output_data):
    class_ids = []
    confidences = []
    boxes = []

    rows = output_data.shape[0]

    image_width, image_height, _ = input_image.shape

    x_factor = image_width / 640
    y_factor = image_height / 640

    for r in range(rows):
        row = output_data[r]
        confidence = row[4]
        if confidence >= 0.4:

            classes_scores = row[5:]
            _, _, _, max_indx = cv2.minMaxLoc(classes_scores)
            class_id = max_indx[1]
            if (classes_scores[class_id] > .25):

                confidences.append(confidence)

                class_ids.append(class_id)

                x, y, w, h = (row[0].item(), row[1].item(), row[2].item(),
                              row[3].item())
                left = int((x - 0.5 * w) * x_factor)
                top = int((y - 0.5 * h) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                box = np.array([left, top, width, height])
                boxes.append(box)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45)

    result_class_ids = []
    result_confidences = []
    result_boxes = []

    for i in indexes:
        result_confidences.append(confidences[i])
        result_class_ids.append(class_ids[i])
        result_boxes.append(boxes[i])

    return result_class_ids, result_confidences, result_boxes


def load_classes():
    class_list = []
    with open("./classes.txt", "r") as f:
        class_list = [cname.strip() for cname in f.readlines()]
    return class_list

def detect_pedestrians(input_img):
    net = cv2.dnn.readNet('yolov5s.onnx')
    img = input_img.copy()

    outs = detect(img, net)
    class_ids, confidences, boxes = unwrap_detection(img, outs[0])

    class_list = load_classes()
    colors = [(255, 255, 0), (0, 255, 0), (0, 255, 255), (255, 0, 0)]
    pedestrians_boxes = []

    for (classid, confidence, box) in zip(class_ids, confidences, boxes):
        # person class id
        if classid == 0 and confidence > 0.5:
            color = colors[int(classid) % len(colors)]
            cv2.rectangle(img, box, color, 2)
            cv2.rectangle(img, (box[0], box[1] - 20), (box[0] + box[2], box[1]),
                        color, -1)
            cv2.putText(img, f'{class_list[classid]} {confidence}',
                        (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5,
                        (0, 0, 0))
            pedestrians_boxes.append(box)

    while True:
        cv2.imshow("output", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    return pedestrians_boxes
