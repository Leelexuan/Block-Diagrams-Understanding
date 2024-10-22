# Block Diagram Extraction 

## Project Idea
To use computer vision techniques to detect blocks, extract information from the blocks, identify relationships represented by arrows and connections, and create a structured representation of the diagram such as triplets – $\langle \mathit{head, relation, tail} \rangle$.

## Background 
Block diagrams are used to visualize the relationships between entities to represent a larger part of a system, workflow or process. They are often found in technical documentation, software design documents, and other forms of documentation. The task of extracting block diagrams can be considered a subtask of document understanding, which is the task of extracting data from unstructured documents. By extracting the information and relationships between blocks from images, we enable downstream tasks such as knowledge graph construction, question answering, and summarization.

## How Computer Vision is Relevant 
Block diagrams can be complex, consisting of blocks, connections, and text annotations which requires a more specialised approach to image processing and pattern recognition to accurately identify and classify these components. As we are working with visual information, we would require computer vision tasks such as object detection to detect blocks and connections, optical character recognition (OCR) to extract text annotations. 

## Related Works 
- Flowchart Knowledge Extraction on Image Processing, IEEE, 2008 [Paper](https://ieeexplore.ieee.org/abstract/document/4634384)
- Block Diagram-to-Text: Understanding Block Diagram Images by Generating Natural Language Descriptors, AACL, 2022 [Paper](https://aclanthology.org/2022.findings-aacl.15/)
- Towards Automatic Parsing of Structured Visual Content through the Use of Synthetic Data, ICPR, 2022 [Paper](https://ieeexplore.ieee.org/abstract/document/9956453)
- DrawnNet: Offline Hand-Drawn Diagram Recognition Based on Keypoint Prediction of Aggregating Geometric Characteristics, MDPI, 2022 [Paper](https://www.mdpi.com/1099-4300/24/3/425)
- Unveiling the Power of Integration: Block Diagram Summarization through Local-Global Fusion, AACL, 2024 [Paper](https://aclanthology.org/2024.findings-acl.822/)