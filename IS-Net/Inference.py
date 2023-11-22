import os
import time
import numpy as np
from skimage import io, color

import time
from glob import glob
from tqdm import tqdm

import torch, gc
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import torch.nn.functional as F
from torchvision.transforms.functional import normalize

from models import *


if __name__ == "__main__":

    dataset_path="/home/gbugaj/tmp/demo"  #Your dataset path
    model_path="../saved_models/IS-Net-test/gpu_itr_122000_traLoss_1.1169_traTarLoss_0.0255_valLoss_0.5976_valTarLoss_0.0201_maxF1_0.9965_mae_0.0111_time_0.007597.pth"  # the model path
    result_path="../demo_datasets/your_dataset_result_kk"  #The folder path that you want to save the results
    input_size=[2048,2048]
    net=ISNetDIS()
    
    has_cuda=torch.cuda.is_available()
    has_cuda=False

    if has_cuda:
        net.load_state_dict(torch.load(model_path))
        net=net.cuda()
    else:
        net.load_state_dict(torch.load(model_path,map_location="cpu"))


    net.eval()
    im_list = glob(dataset_path+"/*.jpg")+glob(dataset_path+"/*.JPG")+glob(dataset_path+"/*.jpeg")+glob(dataset_path+"/*.JPEG")+glob(dataset_path+"/*.png")+glob(dataset_path+"/*.PNG")+glob(dataset_path+"/*.bmp")+glob(dataset_path+"/*.BMP")+glob(dataset_path+"/*.tiff")+glob(dataset_path+"/*.TIFF")
    with torch.no_grad():
        for i, im_path in tqdm(enumerate(im_list), total=len(im_list)):
            print("im_path: ", im_path)
            im = io.imread(im_path)

            # Convert the grayscale image to RGB
            im = color.gray2rgb(im)

            if len(im.shape) < 3:
                im = im[:, :, np.newaxis]
            im_shp=im.shape[0:2]


            im_tensor = torch.tensor(im, dtype=torch.float32).permute(2,0,1)
            im_tensor = F.upsample(torch.unsqueeze(im_tensor,0), input_size, mode="bilinear").type(torch.uint8)
            image = torch.divide(im_tensor,255.0)
            image = normalize(image,[0.5,0.5,0.5],[1.0,1.0,1.0])

            if has_cuda:
                image=image.cuda()

            result=net(image)
            result=torch.squeeze(F.upsample(result[0][0],im_shp,mode='bilinear'),0)
            ma = torch.max(result)
            mi = torch.min(result)
            result = (result-mi)/(ma-mi)
            im_name=im_path.split('/')[-1].split('.')[0]

            print("result_path: ", result_path)
            io.imsave(os.path.join(result_path,im_name+".png"),(result*255).permute(1,2,0).cpu().data.numpy().astype(np.uint8))
