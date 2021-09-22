import cv2
import numpy as np
import torch
import timeit
import util
import os

from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor

from Videopose3D.common.model import TemporalModel
from Videopose3D.common.generators import UnchunkedGenerator
from Videopose3D.common.camera import camera_to_world, normalize_screen_coordinates

common = util.common

def evaluate(test_generator, model_pos, action=None, return_predictions=False):
    joints_left, joints_right = list([4, 5, 6, 11, 12, 13]), list([1, 2, 3, 14, 15, 16])
    with torch.no_grad():
        model_pos.eval()
        N = 0
        for _, batch, batch_2d in test_generator.next_epoch():
            inputs_2d = torch.from_numpy(batch_2d.astype('float32'))
            if torch.cuda.is_available():
                inputs_2d = inputs_2d.cuda()
            # Positional model
            predicted_3d_pos = model_pos(inputs_2d)
            if test_generator.augment_enabled():
                # Undo flipping and take average with non-flipped version
                predicted_3d_pos[1, :, :, 0] *= -1
                predicted_3d_pos[1, :, joints_left + joints_right] = predicted_3d_pos[1, :, joints_right + joints_left]
                predicted_3d_pos = torch.mean(predicted_3d_pos, dim=0, keepdim=True)
            if return_predictions:
                return predicted_3d_pos.squeeze(0).cpu().numpy()

def detect2d(predictor, input_frame):
    output = predictor(input_frame)['instances'].to('cpu')
    has_bbox = False
    if output.has('pred_boxes'):
        bbox_tensor = output.pred_boxes.tensor.numpy()
        if len(bbox_tensor) > 0:
            has_bbox = True
    if has_bbox:
        kps = output.pred_keypoints.numpy()
        kps = kps[0,:,:2]
    else:
        kps = []
    
    return kps

def detect3d(predictor, input_kps, W, H):
    input_kps = normalize_screen_coordinates(input_kps[..., :2], w=W, h=H)
    keypoints = input_kps.copy()
    
    gen = UnchunkedGenerator(None, None, [keypoints], pad=common.pad, causal_shift=common.causal_shift, augment=True, kps_left=common.kps_left, kps_right=common.kps_right, joints_left=common.joints_left, joints_right=common.joints_right)
    prediction = evaluate(gen, predictor, return_predictions=True)
    prediction = camera_to_world(prediction, R=common.rot, t=0)
    prediction[:,:,2] -= np.min(prediction[:,:,2])
    return prediction
    

if __name__=='__main__':

    capture = cv2.VideoCapture("input/short.mp4")
    #capture = cv2.VideoCapture(0)
    cur_frame = 0
    frame_width = 0
    frame_height = 0

    cfg_file = 'COCO-Keypoints/keypoint_rcnn_R_101_FPN_3x.yaml'
    frame_len = 5
    
    print("preparing Detectron2...")
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(cfg_file))
    cfg.MODEL.ROI_HEADS.SCORE_TRHESH_TEST = 0.7
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(cfg_file)
    predictor_2d = DefaultPredictor(cfg)
    
    print("preparing VideoPose3D...")
    chk_point_path = 'Videopose3D/checkpoint/pretrained_h36m_detectron_coco.bin'
    chk_point = torch.load(chk_point_path)
    model_pos = TemporalModel(17,2,17,filter_widths=[3,3,3,3,3],causal=False,dropout=False)
    model_pos = model_pos.cuda()
    model_pos.load_state_dict(chk_point['model_pos'])
    
    keypoints_2d = []
    last_keypoint = None
    print("start processing")
    while(1):
        start_t = timeit.default_timer()
        ret, frame = capture.read()
        if not(ret):
            print("Load failed")
            break
        
        keypoint  = detect2d(predictor_2d, frame)
        if isinstance(keypoint, np.ndarray):
            last_keypoint_2d = keypoint.copy()
            
        kp2d_t = timeit.default_timer()
        keypoints_2d.append(last_keypoint_2d)
        
        if keypoints_2d.__len__() < frame_len+1:
            frame_height = frame.shape[0]
            frame_width = frame.shape[1]
            continue
        keypoints_2d.pop(0)
        keypoints_3d = detect3d(model_pos, np.array(keypoints_2d),frame_width,frame_height)
        
        keypoint_3d = keypoints_3d[-1]
        
        terminate_t = timeit.default_timer()
        
        time_from_video_to_2d = kp2d_t - start_t
        time_from_2d_to_3d = terminate_t - kp2d_t
        FPS = 1./(terminate_t - start_t)
        
        os.system('cls')
        print('cur_processing_frame = ',cur_frame)
        print('(video to 2d) = ',time_from_video_to_2d,"s")
        print('( 2d to 3d  ) = ',time_from_2d_to_3d,"s")
        print('fps = ',FPS)
        util.draw_3Dimg(keypoint_3d, frame, display=1, kpt2D=last_keypoint_2d)
        cur_frame+=1
