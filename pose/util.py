import cv2
import numpy as np
import matplotlib.pyplot as plt

class common():
    keypoints_symmetry = [[1, 3, 5, 7, 9, 11, 13, 15],[2, 4, 6, 8, 10, 12, 14, 16]]
    rot = np.array([ 0.14070565, -0.15007018, -0.7552408 ,  0.62232804], dtype=np.float32)
    skeleton_parents =  np.array([-1,  0,  1,  2,  0,  4,  5,  0,  7,  8,  9,  8, 11, 12,  8, 14, 15])
    pairs = [(1,2), (5,4),(6,5),(8,7),(8,9),(10,1),(11,10),(12,11),(13,1),(14,13),(15,14),(16,2),(16,3),(16,4),(16,7)]

    kps_left, kps_right = list(keypoints_symmetry[0]), list(keypoints_symmetry[1])
    joints_left, joints_right = list([4, 5, 6, 11, 12, 13]), list([1, 2, 3, 14, 15, 16])
    pad = (243 - 1) // 2 # Padding on each side
    causal_shift = 0
    joint_pairs = [[0, 1], [1, 3], [0, 2], [2, 4],
                [5, 6], [5, 7], [7, 9], [6, 8], [8, 10],
                [5, 11], [6, 12], [11, 12],
                [11, 13], [12, 14], [13, 15], [14, 16]]

def draw_2Dimg(img, kpt, display=None):
    # kpts : (17, 3)  3-->(x, y, score)
    im = img.copy()
    joint_pairs = common.joint_pairs
    for item in kpt:
        score = item[-1]
        if score > 0.1:
            x, y = int(item[0]), int(item[1])
            cv2.circle(im, (x, y), 1, (255, 5, 0), 5)
    for pair in joint_pairs:
        j, j_parent = pair
        pt1 = (int(kpt[j][0]), int(kpt[j][1]))
        pt2 = (int(kpt[j_parent][0]), int(kpt[j_parent][1]))
        cv2.line(im, pt1, pt2, (0,255,0), 2)

    if display:
        cv2.imshow('im', im)
        cv2.waitKey(3)
    return im

def draw_3Dimg(pos, image, display=None, kpt2D=None):
    from mpl_toolkits.mplot3d import Axes3D # projection 3D 必须要这个
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    fig = plt.figure(figsize=(12,6))
    canvas = FigureCanvas(fig)

    # 2D
    fig.add_subplot(121)
    if isinstance(kpt2D, np.ndarray):
        plt.imshow(draw_2Dimg(image, kpt2D))
    else:
        plt.imshow(image)

    # 3D
    ax = fig.add_subplot(122, projection='3d')
    radius = 1.7
    ax.view_init(elev=15., azim=70.)
    ax.set_xlim3d([-radius/2, radius/2])
    ax.set_zlim3d([0, radius])
    ax.set_ylim3d([-radius/2, radius/2])
    ax.set_aspect('auto')
    # 坐标轴刻度
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    ax.dist = 7.5
    parents = common.skeleton_parents
    joints_right = common.joints_right

    for j, j_parent in enumerate(parents):
        if j_parent == -1:
            continue

        col = 'red' if j in joints_right else 'black'
        # 画图3D
        ax.plot([pos[j, 0], pos[j_parent, 0]],
                                    [pos[j, 1], pos[j_parent, 1]],
                                    [pos[j, 2], pos[j_parent, 2]], zdir='z', c=col)
    width, height = fig.get_size_inches() * fig.get_dpi()
    canvas.draw()       # draw the canvas, cache the renderer
    image = np.fromstring(canvas.tostring_rgb(), dtype='uint8').reshape(int(height), int(width), 3)
    if display:
        cv2.imshow('im', image)
        cv2.waitKey(3)

    return image