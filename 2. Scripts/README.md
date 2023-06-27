# Overview of scripts:

**Step 1: Preprocessing**

This script prepares the reference data (i.e., Sentinel-1 binary melt) and input features (i.e., ASCAT, SSMIS, elevation, and Sentinel-1 monthly average). The data are preprocessed and the 'matching overpasses' (see manuscript for more details) were selected to form the training, validation, and testing data sets. These date sets were exported in TF-records format to a Google Cloud Bucket. 

--> The script can be used as a Python Notebook or in Google Colab (click [here](https://colab.research.google.com/drive/1K-b04tuQiqAWzgprKUSsRVh2i2xtw70o?usp=sharing) for the Google Colab script)

**Step 2: Training U-Net**

The training, validation, and testing data sets were imported from a Google Cloud Bucket. It was possible to import a specific selection of data, such as Regions 1, 2, and 3, to evaluate the model's spatial performance on Region 4 (see manuscript for more details). Subsequently, an Attention U-Net model was developed and trained using the imported data. Finally, the trained model was saved as part of the script's concluding phase.

--> The script can be used as a Python Notebook or in Google Colab (click [here](https://colab.research.google.com/drive/1bFzgO4JSyyfnOwN0ZUYMILMsBR5nTp35?usp=sharing) for the Google Colab script)

**Step 3: Employ U-Net**

The U-Net model was deployed, a process commonly referred to as "GEE-ifying" the model, to facilitate its utilization within the Google Earth Engine platform.

--> The script can be used as a Python Notebook or in Google Colab (click [here](https://colab.research.google.com/drive/1fWuPGNDlD4rMURXWR0j_JQ50PxJ5GXVl?usp=sharing) for the Google Colab script)

**Step 4: Prediction**


--> The script can be used as a Python Notebook
