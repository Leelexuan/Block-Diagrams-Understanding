import os
import torch
from PIL import Image
from torch.utils.data import Dataset
import xml.etree.ElementTree as ET
import numpy as np

# add label map and convert labels to integers

class XMLDataset(Dataset):
    def __init__(self, image_dir, annotation_dir, label_map=None, transform=None):
        self.image_dir = image_dir
        self.annotation_dir = annotation_dir
        self.image_filenames = sorted(os.listdir(image_dir))
        self.annotation_filenames = sorted(os.listdir(annotation_dir))
        self.label_map = label_map
        self.image_name = ""
        self.transform = transform
        
    def parse_xml(self, annotation_path):
        tree = ET.parse(annotation_path)
        root = tree.getroot()
        self.image_name = root.find('filename').text
        
        boxes = []
        labels = []
        areas = []
        size = root.find('size')
        width = int(size.find('width').text)
        height = int(size.find('height').text)
        
        
        for obj in root.findall('object'):
            label = obj.find('name').text
            bndbox = obj.find('bndbox')
            xmin = int(bndbox.find('xmin').text)
            ymin = int(bndbox.find('ymin').text)
            xmax = int(bndbox.find('xmax').text)
            ymax = int(bndbox.find('ymax').text)
            xwidth = xmax - xmin
            yheight = ymax - ymin
            area = xwidth*yheight
            
            areas.append(area)
            #for albumentations
            boxes.append([xmin, ymin, xmax, ymax])
            if (self.label_map):
                label_idx = self.label_map[label]
            labels.append(label_idx)
        
        return torch.tensor(boxes, dtype=torch.float32), labels, areas, width, height
    
    def __len__(self):
        return len(self.image_filenames)
    
    def __getitem__(self, idx):
        
        try:
            # Load image
            img_path = os.path.join(self.image_dir, self.image_filenames[idx])
            image = Image.open(img_path).convert("RGB")
            
            # Load annotation
            annotation_path = os.path.join(self.annotation_dir, self.annotation_filenames[idx])
            boxes, labels, areas, width, height= self.parse_xml(annotation_path)
            
            target = {
                'boxes': boxes,
                'labels': labels,
                'image_id': idx,
                'area': areas,
                }
            
             # Apply transformation if provided
            if self.transform:
                # Convert boxes to a format suitable for albumentations (COCO format)
                transformed_image = self.transform(image)
                
                # Update the data with the transformed image and boxes
                image = transformed_image

                
            target['boxes'] = torch.tensor(target['boxes'], dtype=torch.float32)
            target['labels'] = torch.tensor(target['labels'], dtype=torch.int64)
            
            
            return (image, target)
        
        except Exception as e:
            # Print the error and the image_id that caused it
            print(f"Error loading data for image name {self.image_name}, idx {idx}")
            print(f"Error: {str(e)}")
            # You can return None or raise the error depending on your need
        return None
