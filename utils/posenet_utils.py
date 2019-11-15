import tensorflow as tf
import cv2
#import time
import argparse
import os
# for data analysis
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
import numpy as np
import io
import boto3


import posenet


# parser = argparse.ArgumentParser()
# parser.add_argument('--model', type=int, default=101)
# parser.add_argument('--scale_factor', type=float, default=1.0)
# parser.add_argument('--notxt', action='store_true')
#parser.add_argument('--image_dir', type=str, default='./images')
#parser.add_argument('--output_dir', type=str, default='./output')
# args = parser.parse_args()



  #cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file
  #success,image = vidcap.read()
  #print 'Read a new frame: ', success
  #count += 1

def posenet_exe():

    with tf.compat.v1.Session() as sess:
        model_cfg, model_outputs = posenet.load_model(101, sess)
        output_stride = model_cfg['output_stride']

        #if args.output_dir:
        #    if not os.path.exists(args.output_dir):
        #        os.makedirs(args.output_dir)

        #filenames = [
        #    f.path for f in os.scandir(args.image_dir) if f.is_file() and f.path.endswith(('.png', '.jpg'))]
        #filenames.sort(key=takeint)
        #start = time.time()
        os.environ['AWS_PROFILE'] = "default"
        os.environ['AWS_DEFAULT_REGION'] = "ap-northeast-2"

        #s3 = boto3.client('s3')
        #s3.download_file('coffitdata', '11112.mp4', 'test_s3.mp4')

        vidcap = cv2.VideoCapture('video/shortshort.mp4')
        result_file = open("result/test_frame.csv",'w')
        result_file.write("frame,nose_y,nose_x,leftEye_y,leftEye_x,rightEye_y,rightEye_x,leftEar_y,leftEar_x,rightEar_y,rightEar_x,leftShoulder_y,leftShoulder_x,rightShoulder_y,rightShoulder_x,leftElbow_y,leftElbow_x,rightElbow_y,rightElbow_x,leftWrist_y,leftWrist_x,rightWrist_y,rightWrist_x,leftHip_y,leftHip_x,rightHip_y,rightHip_x,leftKnee_y,leftKnee_x,rightKnee_y,rightKnee_x,leftAnkle_y,leftAnkle_x,rightAnkle_y,rightAnkle_x\n")

        count = 0
        success = True
        while success:
            succes,input_image = vidcap.read()
            if not success:
                break
            #print("count: ",success,count,input_image)
            if type(input_image) == type(None):
                break
            a_img,b,c = posenet.read_img(input_image)
            #new_image = array(input_image).reshape(1, 720, 720, 3) 
            #print(input_image)
            #print(type(input_image))
            #cv2.imwrite("test/frame%d.jpg" % count, input_image)
            #a_img = cv2.imread("test/frame%d.jpg")

            heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = sess.run(
                model_outputs,
                feed_dict={'image:0': a_img}
            )

            pose_scores, keypoint_scores, keypoint_coords = posenet.decode_multiple_poses(
                heatmaps_result.squeeze(axis=0),
                offsets_result.squeeze(axis=0),
                displacement_fwd_result.squeeze(axis=0),
                displacement_bwd_result.squeeze(axis=0),
                output_stride=output_stride,
                max_pose_detections=10,
                min_pose_score=0.25)

            # if args.output_dir:
            #     draw_image = posenet.draw_skel_and_kp(
            #         draw_image, pose_scores, keypoint_scores, keypoint_coords,
            #         min_pose_score=0.25, min_part_score=0.25)

            #     cv2.imwrite(os.path.join(args.output_dir, os.path.relpath(f, args.image_dir)), draw_image)

           
            print()
            print("Results for image: %s" % count)

            result_file
            result_file.write(str(count)+',')
            # print("pose_scores: ",pose_scores)
            # print("len(pose_scores): ",len(pose_scores))
            # print("type(pose_scores): ",type(pose_scores))
            if pose_scores[0] == 0:
                    for i in range(34):
                        result_file.write(",")
            for pi in range(len(pose_scores)):
                # print("pi : ",pi)
                # print("pose_scroes[pi] : ",[pi])
                if pose_scores[pi] == 0.:
                    break

                print('Pose #%d, score = %f' % (pi, pose_scores[pi]))
                for ki, (s, c) in enumerate(zip(keypoint_scores[pi, :], keypoint_coords[pi, :, :])):
                    print('Keypoint %s, score = %f, coord = %s' % (posenet.PART_NAMES[ki], s, c))
                    
                    result_file.write("%s,%s"%(str(c[0]),str(c[1])))
                    result_file.write(",")
            
            result_file.write("\n")    
            count += 1
        #print('Average FPS:', count / (time.time() - start))
        result_file.close()





# Data Science

def data_analysis():
    regular = pd.read_csv("result/test_frame.csv")
    regular['model']=regular['nose_x']+regular['leftWrist_x']+regular['leftAnkle_x']
    rolling = regular['model'].rolling(window = 30,min_periods=1).std()
    threshold = 0.6 * rolling.to_frame()['model'].max()
    threshold2 = 0.7 * rolling.to_frame()['model'].max()
    threshold3 = 0.8 * rolling.to_frame()['model'].max()

    th_list = []
    th_list.append(threshold)
    th_list.append(threshold2)
    th_list.append(threshold3)


    count = 1
    for th in th_list:
        sieve = rolling.to_frame().query('model > @th')
        sieve_idx= list(sieve.index)

        timestamp = []
        for i in range(len(sieve_idx)):
            if sieve_idx[i] - 1 == sieve_idx[i-1]:
                pass
            else:
                timestamp.append(sieve_idx[i])

        time_list = []
        for time in timestamp:
            totalsecond = time // 10
            minute = str(totalsecond // 60)
            second = str(totalsecond % 60)

            time_list.append("%s:%s"%(minute.zfill(2),second.zfill(2)))
        print("trial %d "%(count),timestamp)
        print("timestamp: ",time_list)
        print("")

        count+=1





if __name__ == "__main__":
     posenet()
     data_analysis()

