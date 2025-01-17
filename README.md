# Abstract
 Understanding block diagrams is an often-overlooked challenge that requires complex functions such
 as deep-learning based computer vision and object detection methods. While these methods are effective
 for symbol detection, their reliance on bounding box representations poses challenges in recognizing
 line segments that are either very short or nearly parallel to the axes. In this report, we propose an
 improvement to the model developed by Bhushan and Lee by presenting a change in the Inception
ResNet-v2 backbone used in their paper. We compared the performances of using a Swin transformer
 and also introduced a new dataset for a wider variety of values.

 # Report
 
[Team16 (1).pdf](https://github.com/user-attachments/files/18449459/Team16.1.pdf)

 # Results
 The models were trained on CBD dataset, which consisted of computerized block diagrams, and tested on FC_A dataset, which consisted of handwritten block diagrams.
 This was to test the generalizability of the models. 

 Below are tables comparing the results of both the Swin-T and Inception Resnet-v2 backbone models.

![image](https://github.com/user-attachments/assets/b886a508-1a09-4c23-ab8a-f34924612398)


![image](https://github.com/user-attachments/assets/c506c049-3cbc-4822-a209-b28073c30be8)


![image](https://github.com/user-attachments/assets/93b487a3-f44d-4ab4-b49b-be40c2aa8c03)

![image](https://github.com/user-attachments/assets/18402ee3-f3e2-4a83-8c1e-8981d843ba82)

This is an example of how the object detection prediction looks like on a test image from FC_A dataset.

![image](https://github.com/user-attachments/assets/ea83ffb5-5596-48aa-8c47-fa232ec5269c)
