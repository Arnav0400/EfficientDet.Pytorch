import os
import os.path as osp
import sys
import torch
import torch.utils.data as data
import torchvision.transforms as transforms
import cv2
import numpy as np


class SPINEDetection(data.Dataset):

    def __init__(self, root, bboxes_df, corners_df, fileame_df, image_set='training',
     transform=None, img_size = (1536,512)):
        self.root = osp.join(root, image_set)
        self.transform = transform
        self.bboxes_df = bboxes_df
        self.corners_df = corners_df
        self.fileame_df = fileame_df
        self.H, self.W = img_size

    def __getitem__(self, index):
        img_id = self.fileame_df.iloc[index,0]
        bboxes = self.bboxes_df[self.bboxes_df.image_id == img_id]
        corners = self.corners_df.iloc[index,:]

        img = cv2.imread(osp.join(self.root, img_id))
        H,W,_ = img.shape

        corner_arr = []
        for i in range(17):
            x1,x2,x3,x4 = np.round((W)*corners.iloc[4*i:4*(i+1)])
            y1,y2,y3,y4 = np.round((H)*corners.iloc[68+4*i:68+4*(i+1)])
            corner_arr.extend([(x1,y1),(x2,y2),(x3,y3),(x4,y4)])
#             corner_arr.append(np.array([x1,x2,x3,x4,y1,y2,y3,y4]))
            

#         corner_arr = np.array(corner_arr)
        bbox = bboxes.iloc[:,1:5].values
        labels = bboxes.iloc[:,5].values
        if self.transform is not None:
            annotation = {'image': img, 'bboxes': bbox, 'category_id': labels,'keypoints':corner_arr}
            augmentation = self.transform(**annotation)
            img = augmentation['image']
            bbox = augmentation['bboxes']
            labels = augmentation['category_id']
            corner_arr = augmentation['keypoints']
#         print(corner_arr[0:4])
        aug_corners = []
        for i in range(17):
            [(x1,y1),(x2,y2),(x3,y3),(x4,y4)] = corner_arr[4*i:4*i+4]
            aug_corners.append(np.round(np.array([x1,x2,x3,x4,y1,y2,y3,y4])))
        aug_corners_ = np.array(aug_corners)

        return {'image': img, 'bboxes': bbox, 'corners': aug_corners_, 'category_id': labels} 


    def __len__(self):
        return len(self.fileame_df)

class SPINEDetection_test(data.Dataset):

    def __init__(self, root = 'test_images', transform = None, img_size = (1408,768)):
        self.root = root
        self.transform = transform
        self.H, self.W = img_size
        path = []
        for img in os.listdir(root):
            if img[-3:] == 'jpg':
                path.append(img)
        self.path = path

    def __getitem__(self, index):
        img_name = self.path[index]
        img = cv2.imread(osp.join(self.root, img_name))

        if self.transform is not None:
            annotation = {'image': img}
            augmentation = self.transform(**annotation)
            img = augmentation['image']
            
        return img 


    def __len__(self):
        return len(self.path)