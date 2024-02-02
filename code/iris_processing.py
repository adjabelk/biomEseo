import os
import cv2
import numpy as np

# Function to center a tkinter window
def center(win):
    # Centers a tkinter window
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

class IrisRecognition:

    def __init__(self):
        # Load the Haar Cascade classifier for eye detection
        self.eye_cascade_classifier = cv2.CascadeClassifier(fr"{self.get_path('utils/haarcascade_eye.xml', 'code')}")

    def get_path(self, imfile, ipath="interface"):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        project_directory = os.path.dirname(current_directory)
        image_path = os.path.join(project_directory, ipath, imfile)
        return image_path

    def detect_faces(self, image, object_classifier, divider=4):
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        small_image = cv2.resize(gray_image, (int(gray_image.shape[1]/divider), int(gray_image.shape[0]/divider)))
        min_object_size = (20, 20)
        haar_scale = 1.2
        min_neighbors = 2
        haar_flags = 0
        objects = object_classifier.detectMultiScale(small_image, haar_scale, min_neighbors, haar_flags, min_object_size)
        return objects * divider

    def detect_eyes(self, image):
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + fr"{self.get_path('haarcascade_eye.xml', 'code')}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        return eyes

    def find_pupil(self, gray_image, minsize=.1, maxsize=.5):
        detector = cv2.MSER_create()
        all_features = detector.detect(gray_image)
        large_features = [feat for feat in all_features if feat.size > gray_image.shape[0] * minsize]
        small_features = [feat for feat in large_features if feat.size < gray_image.shape[0] * maxsize]
        if len(small_features) == 0:
            return None
        sorted_features = self.sort_features_by_brightness(gray_image, small_features)
        pupil = sorted_features[0]
        return (int(pupil.pt[0]), int(pupil.pt[1]), int(pupil.size / 2))

    def sort_features_by_brightness(self, image, features):
        features_and_brightness = [(self.find_average_brightness_of_feature(image, feat), feat) for feat in features]
        features_and_brightness.sort(key=lambda x: x[0])
        return [fb[1] for fb in features_and_brightness]

    def find_average_brightness_of_feature(self, image, feature):
        feature_image = self.mask_image_by_feature(image, feature)
        total_value = feature_image.sum()
        area = np.pi * ((feature.size / 2) ** 2)
        return total_value / area

    def mask_image_by_feature(self, image, feature):
        circle_mask_image = np.zeros(image.shape, dtype=np.uint8)
        cv2.circle(circle_mask_image, (int(feature.pt[0]), int(feature.pt[1])), int(feature.size / 2), 1, -1)
        masked_image = (image * circle_mask_image).astype(np.uint8)
        return masked_image

    def circle_pupil(self, color_image, output_image=None):
        if output_image is None:
            output_image = color_image
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2GRAY)
        pupil_coordinates = self.find_pupil(gray_image)
        if pupil_coordinates is not None:
            cv2.circle(output_image, pupil_coordinates[:2], pupil_coordinates[2], (0, 255, 0), 4)

    def draw(self, photo):
        if photo is not None:
            image_to_show = photo.copy()
        else:
            image_to_show = photo
        eyes = self.detect_faces(image_to_show, self.eye_cascade_classifier)
        rightmost_eye = None
        if eyes is not None:
            for eye in eyes:
                (x, y) = eye[0], eye[1]
                (x2, y2) = (eye[0] + eye[2]), (eye[1] + eye[3])
                if (rightmost_eye is None) or (x < rightmost_eye.x):
                    rightmost_eye = self.Eye(x, y, x2, y2)
        eye_image = None
        if rightmost_eye is not None:
            eye_image = image_to_show[rightmost_eye.y:rightmost_eye.y2, rightmost_eye.x:rightmost_eye.x2]
        binary_eye_image = None
        if eye_image is not None:
            eye_histogram = [0] * 256
            eye_image = cv2.cvtColor(eye_image, cv2.COLOR_BGR2GRAY)
            for i in range(256):
                value_count = (eye_image == i).sum()
                eye_histogram[i] = value_count
            count = 0
            index = 255
            while count < (eye_image.size * 3 / 4):
                count += eye_histogram[index]
                index -= 1
            quarter_threshold = index
            binary_eye_image = cv2.equalizeHist((eye_image < quarter_threshold) * eye_image)
        relative_iris_coordinates = None
        if binary_eye_image is not None:
            eye_circles = cv2.HoughCircles(binary_eye_image, cv2.HOUGH_GRADIENT, dp=3, minDist=500, param1=50,
                                          param2=30, minRadius=0, maxRadius=int(binary_eye_image.shape[0] / 5))
            if eye_circles is not None:
                circle = eye_circles[0][0]
                relative_iris_coordinates = (circle[0], circle[1])
        absolute_iris_coordinates = None
        if relative_iris_coordinates is not None and rightmost_eye is not None:
            absolute_iris_coordinates = (int(relative_iris_coordinates[0] + rightmost_eye.x),
                                         int(relative_iris_coordinates[1] + rightmost_eye.y))
            cv2.circle(image_to_show, absolute_iris_coordinates, 5, (255, 0, 0), thickness=10)
        iris_image = None
        if absolute_iris_coordinates is not None:
            x = absolute_iris_coordinates[0]
            y = absolute_iris_coordinates[1]
            w = 60
            h = 60
            iris_image = photo[y - h:y + h, x - w:x + w]

            # Check if the iris image is not empty before resizing
            if iris_image.shape[0] > 0 and iris_image.shape[1] > 0:
                iris_image_to_show = cv2.resize(iris_image, (int(iris_image.shape[1] * 2), int(iris_image.shape[0] * 2)),
                                                interpolation=cv2.INTER_LINEAR)
                image_to_show[0:iris_image_to_show.shape[0], 0:0 + iris_image_to_show.shape[1]] = iris_image_to_show
            else:
                print("Warning: Iris image is empty, cannot resize.")

        iris_picture = None
        if iris_image is not None:
            iris_gray = cv2.cvtColor(iris_image, cv2.COLOR_BGR2GRAY)
            iris_circles_image = iris_image.copy()
            iris_circles = cv2.HoughCircles(iris_gray, cv2.HOUGH_GRADIENT, dp=2, minDist=100)
            if iris_circles is not None:
                circle = iris_circles[0][0]
                cv2.circle(iris_circles_image, (int(circle[0]), int(circle[1])), int(circle[2]), (255, 0, 0), thickness=2)
            pupil_coords = self.find_pupil(iris_gray)
            if pupil_coords is not None:
                cv2.circle(iris_circles_image, pupil_coords[:2], pupil_coords[2], (0, 255, 0), 4)
            if iris_circles is not None and pupil_coords is not None:
                ic = iris_circles[0][0]
                pc = pupil_coords
                if abs(ic[0] - pc[0]) < ic[2] and abs(ic[1] - pc[1]) < ic[2] and pc[2] < ic[2]:
                    iris_picture = iris_circles_image
            iris_circles_to_show = cv2.resize(iris_circles_image, (int(iris_image.shape[1] * 2), int(iris_image.shape[0] * 2)))
            image_to_show[0:iris_circles_to_show.shape[0], 200:200 + iris_circles_to_show.shape[1]] = iris_circles_to_show
        window_name = "Iris Enrolling"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
        cv2.moveWindow(window_name, 363, 144)
        cv2.imshow(window_name, image_to_show)
        if cv2.waitKey(10) > 0:
            return True, iris_picture
        return False, iris_picture

    class Eye:
        def __init__(self, x, y, x2, y2):
            self.x = x
            self.y = y
            self.x2 = x2
            self.y2 = y2
            self.width = x2 - x
            self.height = y2 - y
            self.topcorner = (x, y)
            self.bottomcorner = (x2, y2)

    def enroll_iris(self, filename):
        camera = cv2.VideoCapture(0)
        while True:
            result, photo = camera.read()
            finished, iris = self.draw(photo)
            if result:            
                if iris is not None:
                    image_path = fr"{self.get_path('iris','biometries_data')}\{filename}"
                    cv2.imwrite(image_path, iris)
                    camera.release()
                    cv2.destroyAllWindows()

                if finished:
                    break
        
if __name__ == '__main__':
    ir = IrisRecognition()
    ir.enroll_iris("runrun.jpg")