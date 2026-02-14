cmake_minimum_required(VERSION 4.0)

project(test)

# ADSampling
add_executable(BenchmarkPDXADSampling bench_adsampling/pdx_ivf_adsampling.cpp)
add_executable(BenchmarkIVF2ADSampling bench_adsampling/pdx_ivf2_adsampling.cpp)
add_executable(BenchmarkU8PDXADSampling bench_adsampling/pdx_ivf_adsampling_u8.cpp)
add_executable(BenchmarkU8IVF2ADSampling bench_adsampling/pdx_ivf2_adsampling_u8.cpp)
add_executable(FilteredBenchmarkU8IVF2ADSampling bench_adsampling/pdx_ivf2_adsampling_u8_filtered.cpp)
add_executable(FilteredBenchmarkPDXADSampling bench_adsampling/pdx_ivf_adsampling_filtered.cpp)

# BOND
add_executable(BenchmarkPDXIVFBOND ./bench_bond/pdx_bond_ivf.cpp)
add_executable(BenchmarkPDXBOND ./bench_bond/pdx_bond.cpp)

# Include utilities
set(PROJECT_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../include")
set(PROJECT_EXTERN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../extern")
set(ALL_BENCHMARKS
	BenchmarkPDXADSampling
	BenchmarkIVF2ADSampling
	BenchmarkU8PDXADSampling
	BenchmarkU8IVF2ADSampling
	FilteredBenchmarkU8IVF2ADSampling
	FilteredBenchmarkPDXADSampling
	BenchmarkPDXIVFBOND
	BenchmarkPDXBOND
)

foreach(tgt IN LISTS ALL_BENCHMARKS)
	target_include_directories(${tgt} PRIVATE ${PROJECT_INCLUDE_DIR})
	target_include_directories(${tgt} PRIVATE ${PROJECT_EXTERN_DIR})
	target_compile_definitions(${tgt} PRIVATE CMAKE_SOURCE_DIR="${CMAKE_SOURCE_DIR}/..")
endforeach()

if (FFTW_FOUND)
    target_link_libraries(BenchmarkPDXADSampling ${FFTW_FLOAT_LIB})
    target_link_libraries(FilteredBenchmarkPDXADSampling ${FFTW_FLOAT_LIB})
    target_link_libraries(BenchmarkIVF2ADSampling ${FFTW_FLOAT_LIB})
    target_link_libraries(BenchmarkU8PDXADSampling ${FFTW_FLOAT_LIB})
    target_link_libraries(BenchmarkU8IVF2ADSampling ${FFTW_FLOAT_LIB})
    target_link_libraries(FilteredBenchmarkU8IVF2ADSampling ${FFTW_FLOAT_LIB})
    target_link_libraries(BenchmarkPDXIVFBOND ${FFTW_FLOAT_LIB})
    target_link_libraries(BenchmarkPDXBOND ${FFTW_FLOAT_LIB})
endif()
