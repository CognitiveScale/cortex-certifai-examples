# Segmented Models

This notebook provides an initial illustration on how to accommodate segmented models
in Certifai notebooks.

The example is entirely contrived, and only intended to illustrate the pattern, rather
than actually being a meaningful segmentation use case.

In this context a segmented model is one wherein predictions for a particular input
data point are made by one of several different sub-models (the segment models) dependent on a
segmentation partitioning of the data rows based on some criteria applied to those
rows.  A particular restricted interpretation of this is illustrated in this notebook (
see `Assumptions` below)

## Assumptions

1. Certifai toolkit (v1.2.13 or greater) is installed and if installed in a virtual environment such as Conda, that environment is active
2. The segments are defined by the value of a single categorical field present in the data
3. All segment models are trained (and can predict) on the full set of columns, including the segmentation column
4. All segment models are expecting categoricals to be 1-hot encoded (in this notebook that will include the segmentation field itself)

*Notes*

* The notebook is based on the `CleanStart` notebook from the Toolkit
* The main sections modified for the segmentation are denoted by comments beginning `SEGMENT MODEL TEST`
