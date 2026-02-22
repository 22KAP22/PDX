import faiss
import sys
from benchmark_utils import *
from setup_utils import *
from setup_settings import *
from sklearn import preprocessing

DATASETS_TO_USE = [
]
# Scalar Quantization in FAISS is EXTREMELY slow in ARM due to lack of SIMD
if __name__ == '__main__':
    arg_dataset = ""
    if len(sys.argv) > 1:
        arg_dataset = sys.argv[1]
    # Create dir if it doesn't exist yet
    if not os.path.exists(PCA_DATA):
        os.makedirs(PCA_DATA)
    # Use datasets defined in settings if not specified
    if not len(DATASETS_TO_USE): DATASETS_TO_USE = DATASETS


    for dataset in DATASETS_TO_USE:
        if len(arg_dataset) and dataset != arg_dataset:
            continue
        dimensionality = DIMENSIONALITIES[dataset]
        file_path = os.path.join(PCA_DATA, get_pca_filename(dataset))

        print('Building FAISS PCA transformed dataset', dataset)
        print('Loading data')
        data = read_hdf5_train_data(dataset)
        print('Normalizing')
        data = preprocessing.normalize(data, axis=1, norm='l2')
        num_embeddings = len(data)
        # Compute transformation matrix for all dimensions, later used to create indexes for lower dimensions
        pca = faiss.PCAMatrix(dimensionality, dimensionality)
        print('Computing PCA transformation Matrix')
        pca.train(data)
        print('Storing')
        faiss.write_VectorTransform(pca, file_path)
