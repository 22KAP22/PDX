import sys
from benchmark_utils import *
from setup_utils import *
from setup_settings import *

DATASETS_TO_USE = [
]
# Scalar Quantization in FAISS is EXTREMELY slow in ARM due to lack of SIMD
if __name__ == '__main__':
    RESULTS_PATH = os.path.join(RESULTS_DIRECTORY, "IVF_FAISS_U8.csv")
    arg_dataset = ""
    IVF_NPROBE = 0
    if len(sys.argv) > 1:
        arg_dataset = sys.argv[1]
    if len(sys.argv) > 2:
        IVF_NPROBE = int(sys.argv[2])  # controls recall of search
    if not len(DATASETS_TO_USE): DATASETS_TO_USE = DATASETS
    for dataset in DATASETS_TO_USE:
        if len(arg_dataset) and dataset != arg_dataset:
            continue
        data = read_hdf5_train_data(dataset)
        num_embeddings = len(data)
        print(f'{dataset} has {num_embeddings} datapoints')



