# Preliminary Research
This document contains the preliminary research conducted for the 1-D Design Project Research Track.

## Description
In this track, students are required to study some research papers, implement the algorithms, perform experiments, and propose improvements on the algorithms, e.g., training algorithm, network architecture. The expectation is that by the end of the project the team has gained reasonable understanding of the selected papers and has performed some related experiments. It is not a requirement to have improved results. 

While research papers are the results of dedicated work by industrial / academic researchers and graduate students, some of these ideas could be surprisingly simple and are easy to understand. An  important aspect is novelty and out-of-the-box thinking. 

Some examples:
- [Masked Autoencoders Are Scalable Vision Learners](https://openaccess.thecvf.com/content/CVPR2022/papers/He_Masked_Autoencoders_Are_Scalable_Vision_Learners_CVPR_2022_paper.pdf)
- [mixup: Beyond Empirical Risk Minimization](https://openreview.net/forum?id=r1Ddp1-Rb)
- [Prototypical Networks for Few-Shot Learning](https://papers.nips.cc/paper_files/paper/2017/hash/cb8da6767461f2812ae4290eac7cbc42-Abstract.html)
- [Unsupervised Representation Learning by Predicting Image Rotations](https://openreview.net/forum?id=S1v4N2l0-)

Students can consult the instructor for suggestions of research papers. A lot of computer vision research is published in these conferences: CVPR, ICCV, ECCV, NeurIPS, ICML, ICLR, AAAI (All are A* venues in Computer Science)

## Resources
### General
- [Attention is All You Need](https://arxiv.org/abs/1706.03762) - Original paper introducing the Transformer architecture
- [Awesome Computer Vision](https://github.com/jbhuang0604/awesome-computer-vision) - Curated list of awesome computer vision resources
- [Awesome Document Understanding](https://github.com/harrytea/Awesome-Document-Understanding?tab=readme-ov-file)

### Vision Transformers (ViTs)
- [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929) - Original paper introducing the ViT architecture

### [Vision Language Models (VLMs)](https://huggingface.co/learn/computer-vision-course/en/unit4/multimodal-models/vlm-intro)
Exploring the use of general-purpose VLMs for various computer vision downstream tasks, such as:
- Image Classification
- Object Detection
- Semantic segmentation
- Image-text Retrieval
- Image Captioning: providing descriptive captions for a given image
- Visual Question-Answering (VQA): answering and reasoning about questions about images



## Possible Research Topics

### Data Augmentation With Diffusion Models
Standard approaches to data augmentation involves applying transformations to input images to generate new image samples. However, these new images lack diversity and are unable to alter high-level semantic content, such as an animal species present in a scene. 

- [Effective Data Augmentation With Diffusion Models](https://openreview.net/forum?id=ZWzUA9zeAg) - Paper exploring the use of diffusion models for data augmentation using text-to-image and image-to-image generative tasks

### Flowchart


- [Flowchart knowledge extraction on image processing](https://ieeexplore.ieee.org/abstract/document/4634384/citations?tabFilter=papers#citations) - Paper presenting an image processing method to extract text and geometrical shapes from flowchart images, linking components via flow lines, and outputs the extracted information as XML metadata for archiving, knowledge sharing, or further use.

- [Towards Automatic Parsing of Structured Visual Content through the Use of Synthetic Data](https://ieeexplore.ieee.org/abstract/document/9956453?casa_token=ObhFf9NRYHcAAAAA:2iMJTWYncFKzyPTEKLa3sCQZYi1C-nRf_cziG-yrMoTeZyKmdau26dAmrgPiPamp6RmSwYju00yFgw) - Synthetic dataset for flowcharts 

- [Tool to Extract and Summarize Methodologies of Research Articles for Visually Impaired Researchers](https://ieeexplore.ieee.org/abstract/document/9103342?casa_token=MRMZtOX6oEYAAAAA:VudG8GZ5Fk8YXmLoCVrq_qMuBjC-TNoGnNe_R1TiqGV2i_JTz1_C96bGf9WD0jsHqgjaOWKgBiGY) - Extract flowchart information for visually impaired students
