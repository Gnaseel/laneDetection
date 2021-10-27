from tool.trainer import Trainer
from tool.inference import Inference
from back_logic.evaluate import EDeval
from model.VGG16 import myModel
from model.VGG16_rf20 import VGG16_rf20
from model.ResNet34 import ResNet34
from model.ResNet50 import ResNet50
from model.ResNet34_lin import ResNet34_lin
from torchsummary import summary
from torchvision import models
import os
from evaluator.lane import LaneEval
from evaluator.lane import Eval_Cfg
from evaluator.lane import Eval_data
import torch
class EngineTheRun():
    def __init__(self, args):
        self.cfg= args
        self.device = 'cpu'
        if args.device!='-1':
            self.device='cuda:'+args.device
        print("My Device is {}".format(self.device))

        return
    def train(self):
        trainer = Trainer(self.cfg)
        trainer.model = self.getModel()
        trainer.dataset_path = "D:\\lane_dataset\\img_lane_640.npy"
        trainer.device = self.device
        if self.cfg.backbone=="ResNet34_lin":
            trainer.dataset_path = "/home/ubuntu/Hgnaseel_SHL/Dataset/img_lane_640.npy"
#             trainer.dataset_path = "D:\\lane_dataset\\img_lane.npy"

            trainer.train_lane_lin()
        elif self.cfg.backbone=="ResNet50":
            trainer.dataset_path = "D:\\lane_dataset\\img_lane_640.npy"
            trainer.train_lane_lin()
        else:
            trainer.dataset_path = "/home/ubuntu/Hgnaseel_SHL/Dataset/img_lane_640.npy"
            trainer.train_lane_lin()
    def inference(self):
        inferencer = Inference(self.cfg)
        inferencer.model = self.getModel()
        inferencer.model.load_state_dict(torch.load(self.cfg.model_path, map_location='cpu'))

        inferencer.model.eval()
        inferencer.device = self.device
        
        
        if self.cfg.showAll:
            inferencer.inference_all()
        else:
            inferencer.inference()

        
    def scoring(self):
#         print(os.getcwd())
#         print(os.path.dirname(self.cfg.model_path))
        
        
        inferencer = Inference(self.cfg)
        inferencer.image_save_path = os.path.dirname(self.cfg.model_path)+"/Image"
#         print(inferencer.image_save_path)
#         return
        os.makedirs(inferencer.image_save_path, exist_ok=True)
#         inferencer.image_save_path = os.path.dirname(self.cfg.model_path)
        inferencer.model = self.getModel()
        inferencer.model.load_state_dict(torch.load(self.cfg.model_path, map_location='cpu'))
        inferencer.model.to(self.device)
        inferencer.device = self.device
        
        lane_tensor, path_list = inferencer.inference_dir()
        evaluator = EDeval()
        evaluator.save_JSON(lane_tensor, path_list)
        
        bench = LaneEval()
        eval_cfg = Eval_Cfg()
        print("BENCH1")
        eval_cfg = bench.bench_one_submit("./back_logic/result_li.json","./evaluator/gt.json")
        eval_cfg.sort_list()
        
        filepaths=[]
        
        idx =0
        for i in eval_cfg.eval_list:
            idx+=1
            print(i.acc)
            print(i.pred_lane)
            print(i.gt_lane)
            print(i.filePath[5:])
            filepaths.append(self.cfg.image_path + i.filePath[5:]) #+ "/0531/1492729085263099246/20.jpg")
 
            if idx > 5:
                break
        print("SDFSDFSDFSDF-------------------------")
        print("SDFSDFSDFSDF-------------------------")
        print("SDFSDFSDFSDF-------------------------")
        idx =0
        for i in reversed(eval_cfg.eval_list):
            idx+=1
            print(i.acc)
            print(i.pred_lane)
            print(i.gt_lane)
            print(i.filePath[5:])
            filepaths.append(self.cfg.image_path + i.filePath[5:]) #+ "/0531/1492729085263099246/20.jpg")
 
            if idx > 5:
                break
#         return
#         filepaths=[]
#         filepaths.append(self.cfg.image_path + "/0531/1492729085263099246/20.jpg")
        
        os.makedirs(inferencer.image_save_path, exist_ok=True)
        
        print("FILEPATH {}".format(filepaths))
        inferencer.save_image_dir(filepaths)
        print(inferencer.image_save_path)
        
        # f = open(inferencer.image_save_path+"/data.txt", 'w')
        # f.write()

        print("BENCH2")
        return
    def getModel(self):
        model = None
        # model = models.resnet34(pretrained=True)
        # summary(model, (3, 368, 640),device='cpu')

        if self.cfg.backbone == "VGG16":
            model = myModel()
            summary(model, (3, 368, 640),device='cpu')
        elif self.cfg.backbone == "VGG16_rf20":
            model = VGG16_rf20()
            summary(model, (3, 368, 640),device='cpu')
        elif self.cfg.backbone == "ResNet34":
            model = ResNet34()
            summary(model, (3, 368, 640),device='cpu')
        elif self.cfg.backbone == "ResNet34_lin":
            model = ResNet34_lin()
            summary(model, (3, 176, 304),device='cpu')
        elif self.cfg.backbone == "ResNet50":
            model = ResNet50()
            summary(model, (3, 368, 640),device='cpu')
        return model
