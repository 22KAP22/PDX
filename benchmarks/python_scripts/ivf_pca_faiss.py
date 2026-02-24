import faiss
import json
import sys
from benchmark_utils import *
from setup_utils import *
from setup_settings import *
from sklearn import preprocessing

BUILD = False 
DATASETS_TO_USE = [
]
# Scalar Quantization in FAISS is EXTREMELY slow in ARM due to lack of SIMD
if __name__ == '__main__':
    RESULTS_PATH = os.path.join(RESULTS_DIRECTORY, "PCA_IVF_FAISS.csv")
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
        dimensionality = DIMENSIONALITIES[dataset]
        gt_name = os.path.join(SEMANTIC_GROUND_TRUTH_PATH, get_ground_truth_filename(dataset, 100))
        pca_data_name = os.path.join(PCA_DATA, get_pca_filename(dataset))

        if BUILD:
            print('Building FAISS PCA indexes for', dataset)
            print('Loading data')
            data = read_hdf5_train_data(dataset)
            print('Normalizing')
            data = preprocessing.normalize(data, axis=1, norm='l2')
            pca_full = faiss.read_VectorTransform(pca_data_name)
            num_embeddings = len(data)
            pca_data = pca_full.apply(data)
            if dataset == "simplewiki-openai-3072-normalized": # Special case because it has too many dimensions!
                nbuckets = 2048
            elif num_embeddings < 500_000:
                nbuckets = math.ceil(2 * math.sqrt(num_embeddings))
            elif num_embeddings < 2_500_000:
                nbuckets = math.ceil(4 * math.sqrt(num_embeddings))
            else:  # Deep with 10m
                nbuckets = math.ceil(8 * math.sqrt(num_embeddings))
            for pca_dim_factor in PCA_DIMENSIONALITIES_FACTORS:
                print(f'Instantiating index with dim: {pca_dim_factor}')
                pca_dim = int(math.ceil(dimensionality * pca_dim_factor))
                index_name = os.path.join(CORE_INDEXES_FAISS_PCA, get_core_pca_index_filename(dataset, pca_dim))
                index_data = pca_data[:, :pca_dim]
                coarse_quantizer =  faiss.IndexFlatL2(pca_dim)
                index = faiss.IndexIVFFlat(coarse_quantizer, pca_dim, int(nbuckets))
                print('Training with all points')
                index.train(index_data)
                print('Building')
                index.add(index_data)
                print('Saving')
                faiss.write_index(index, index_name)
            continue

        disable_multithreading()
        faiss.omp_set_num_threads(1)

        queries = read_hdf5_test_data(dataset)
        queries = preprocessing.normalize(queries, axis=1, norm='l2')

        # We need to apply this for all different dimensionality reductions once and then take dimensions we need
        print(f'Transforming with PCA')
        pca_full = faiss.read_VectorTransform(pca_data_name)
        pca_queries = pca_full.apply(queries)

        nprobes_to_use = []
        if IVF_NPROBE:
            nprobes_to_use = [IVF_NPROBE]
        else :
            nprobes_to_use = PCA_IVF_NPROBES

        for pca_factor in PCA_DIMENSIONALITIES_FACTORS:
            print('PCA factor: ', pca_factor)
            pca_dim = int(math.ceil(dimensionality * pca_factor))
            print('Restoring index...')
            index_name = os.path.join(CORE_INDEXES_FAISS_PCA, get_core_pca_index_filename(dataset, pca_dim))
            index = faiss.read_index(index_name)
            print('Index restored...')
                
            # Only consider the dimensions we need
            search_queries = pca_queries[:, :pca_dim]

            for ivf_nprobe in nprobes_to_use:
                print('Nprobe: ', ivf_nprobe)
                if IVF_NPROBE > 0 and IVF_NPROBE != ivf_nprobe:
                    continue
                if ivf_nprobe > index.nlist:
                    continue

                runtimes = []
                recalls = []
                clock = TicToc()
                index.nprobe = ivf_nprobe

                print('Querying Measure...')
                for i in range(N_MEASURE_RUNS):
                    j = 0
                    for q in search_queries:
                        q = np.ascontiguousarray(np.array([q]))
                        clock.tic()
                        index.search(q, KNN)
                        runtimes.append(clock.toc())
                        print(f'Query {j}/{len(search_queries)}', end='\r')
                        j += 1

                # Measure recall afterwards to not affect cache
                gt = json.load(open(gt_name, 'r'))
                query_i = 0
                for q in search_queries:
                    _, matches = index.search(np.ascontiguousarray(np.array([q])), KNN)
                    recalls.append(float(len(set(matches[0]).intersection(set(gt[str(query_i)][:KNN])))) / KNN)
                    print(f'Query {query_i}/{len(search_queries)}', end='\r')
                    query_i += 1

                metadata = {
                    'dataset': f'{dataset}_PCA_{pca_factor}',
                    'n_queries': len(queries),
                    'algorithm': 'ivf_faiss',
                    'recall': sum(recalls) / float(len(recalls)),
                    'ivf_nprobe': ivf_nprobe
                }
                save_results(runtimes, RESULTS_PATH, metadata)
