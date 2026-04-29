#include "ggml.h"
#include "ggml-cpu.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>
#include <random>
#include <string>
#include <vector>

namespace {

constexpr int kThreads = 12;

extern "C" {
void quantize_row_tbq2(const float * x, void * y, int64_t k);
void quantize_row_tbq3(const float * x, void * y, int64_t k);
void quantize_row_tbq4(const float * x, void * y, int64_t k);
}

enum class DistKind {
    normal_zero_mean,
    normal_shifted,
    normal_with_outliers,
};

struct CaseSpec {
    std::string name;
    int64_t hsk;
    int64_t hsv;
    int64_t nh_kv;
    int64_t gqa;
    int64_t kv;
    int64_t nb;
    DistKind k_dist;
    DistKind v_dist;
};

struct Metrics {
    double mse = 0.0;
    double nmse = 0.0;
    double max_abs = 0.0;
};

int64_t ggml_pad(int64_t n, int64_t m) {
    return ((n + m - 1) / m) * m;
}

void fill_distribution(std::vector<float> & data, DistKind kind, std::mt19937 & rng) {
    std::normal_distribution<float> normal(0.0f, 1.0f);
    std::uniform_real_distribution<float> unit(0.0f, 1.0f);
    for (float & v : data) {
        v = normal(rng);
        if (kind == DistKind::normal_shifted) {
            v += 0.75f;
        } else if (kind == DistKind::normal_with_outliers) {
            if (unit(rng) < 0.02f) {
                v *= 8.0f;
            }
        }
    }
}

void copy_or_quantize(
        ggml_tensor * t,
        const std::vector<float> & src,
        int64_t n_per_row) {
    if (t->type == GGML_TYPE_F32) {
        std::memcpy(t->data, src.data(), src.size() * sizeof(float));
        return;
    }

    if (t->type == GGML_TYPE_F16) {
        auto * out = static_cast<ggml_fp16_t *>(t->data);
        ggml_fp32_to_fp16_row(src.data(), out, src.size());
        return;
    }

    const int64_t nrows = src.size() / n_per_row;

    if (t->type == GGML_TYPE_TBQ2 || t->type == GGML_TYPE_TBQ3 || t->type == GGML_TYPE_TBQ4) {
        const size_t row_size = ggml_row_size(t->type, n_per_row);
        auto quantize_row = t->type == GGML_TYPE_TBQ2 ? quantize_row_tbq2 :
                            t->type == GGML_TYPE_TBQ3 ? quantize_row_tbq3 :
                                                         quantize_row_tbq4;
        for (int64_t row = 0; row < nrows; ++row) {
            quantize_row(src.data() + row * n_per_row, static_cast<char *>(t->data) + row * row_size, n_per_row);
        }
        return;
    }

    std::vector<float> imatrix(n_per_row, 1.0f);
    ggml_quantize_chunk(t->type, src.data(), t->data, 0, nrows, n_per_row,
            ggml_quantize_requires_imatrix(t->type) ? imatrix.data() : nullptr);
}

std::vector<float> run_flash_attn(
        ggml_type type_k,
        ggml_type type_v,
        const CaseSpec & spec,
        const std::vector<float> & q_src,
        const std::vector<float> & k_src,
        const std::vector<float> & v_src) {
    const int64_t q_heads = spec.nh_kv * spec.gqa;
    const int64_t hsk_pad = ggml_pad(spec.hsk, ggml_blck_size(type_k));
    const int64_t hsv_pad = ggml_pad(spec.hsv, ggml_blck_size(type_v));

    ggml_init_params params = {
        .mem_size = 64ull * 1024ull * 1024ull,
        .mem_buffer = nullptr,
        .no_alloc = false,
    };
    std::unique_ptr<ggml_context, decltype(&ggml_free)> ctx(ggml_init(params), ggml_free);
    if (!ctx) {
        throw std::runtime_error("ggml_init failed");
    }

    ggml_tensor * q = ggml_new_tensor_4d(ctx.get(), GGML_TYPE_F32, hsk_pad, spec.nb, q_heads, 1);
    ggml_tensor * k = ggml_new_tensor_4d(ctx.get(), type_k,        hsk_pad, spec.kv, spec.nh_kv, 1);
    ggml_tensor * v = ggml_new_tensor_4d(ctx.get(), type_v,        hsv_pad, spec.kv, spec.nh_kv, 1);

    copy_or_quantize(q, q_src, hsk_pad);
    copy_or_quantize(k, k_src, hsk_pad);
    copy_or_quantize(v, v_src, hsv_pad);

    ggml_tensor * out = ggml_flash_attn_ext(ctx.get(), q, k, v, nullptr, 1.0f / std::sqrt(static_cast<float>(spec.hsk)), 0.0f, 0.0f);
    ggml_flash_attn_ext_set_prec(out, GGML_PREC_F32);

    ggml_cgraph * graph = ggml_new_graph(ctx.get());
    ggml_build_forward_expand(graph, out);
    if (ggml_graph_compute_with_ctx(ctx.get(), graph, kThreads) != GGML_STATUS_SUCCESS) {
        throw std::runtime_error("ggml_graph_compute_with_ctx failed");
    }

    const int64_t n = ggml_nelements(out);
    const float * out_f32 = static_cast<const float *>(out->data);
    return std::vector<float>(out_f32, out_f32 + n);
}

Metrics compare_outputs(const std::vector<float> & ref, const std::vector<float> & got) {
    Metrics m;
    double ref_sq = 0.0;
    for (size_t i = 0; i < ref.size(); ++i) {
        const double diff = static_cast<double>(got[i]) - static_cast<double>(ref[i]);
        const double abs_diff = std::abs(diff);
        m.mse += diff * diff;
        ref_sq += static_cast<double>(ref[i]) * static_cast<double>(ref[i]);
        m.max_abs = std::max(m.max_abs, abs_diff);
    }
    m.mse /= static_cast<double>(ref.size());
    m.nmse = m.mse / std::max(1e-12, ref_sq / static_cast<double>(ref.size()));
    return m;
}

std::string dist_name(DistKind kind) {
    switch (kind) {
        case DistKind::normal_zero_mean: return "normal";
        case DistKind::normal_shifted: return "shifted";
        case DistKind::normal_with_outliers: return "outliers";
    }
    return "unknown";
}

void print_metric_row(const std::string & label, const Metrics & m) {
    std::cout << std::left << std::setw(8) << label
              << " mse=" << std::setw(12) << std::scientific << std::setprecision(4) << m.mse
              << " nmse=" << std::setw(12) << std::scientific << std::setprecision(4) << m.nmse
              << " max_abs=" << std::setw(12) << std::scientific << std::setprecision(4) << m.max_abs
              << "\n";
}

}  // namespace

int main() {
    try {
        const std::vector<CaseSpec> cases = {
            {"mha_1x",       128, 128, 4, 1, 1024, 1, DistKind::normal_zero_mean,     DistKind::normal_zero_mean},
            {"gqa_4x",       128, 128, 4, 4, 1024, 1, DistKind::normal_zero_mean,     DistKind::normal_zero_mean},
            {"qwen_like",    128, 128, 4, 7, 1024, 1, DistKind::normal_zero_mean,     DistKind::normal_zero_mean},
            {"qwen_shift",   128, 128, 4, 7, 1024, 1, DistKind::normal_shifted,       DistKind::normal_shifted},
            {"qwen_sinky",   128, 128, 4, 7, 1024, 1, DistKind::normal_with_outliers, DistKind::normal_with_outliers},
            {"qwen_k_sinks", 128, 128, 4, 7, 1024, 1, DistKind::normal_with_outliers, DistKind::normal_zero_mean},
            {"qwen_v_sinks", 128, 128, 4, 7, 1024, 1, DistKind::normal_zero_mean,     DistKind::normal_with_outliers},
        };

        std::mt19937 rng(12345);
        for (const CaseSpec & spec : cases) {
            const int64_t q_heads = spec.nh_kv * spec.gqa;
            const int64_t q_count = spec.hsk * spec.nb * q_heads;
            const int64_t k_count = spec.hsk * spec.kv * spec.nh_kv;
            const int64_t v_count = spec.hsv * spec.kv * spec.nh_kv;

            std::vector<float> q_src(q_count);
            std::vector<float> k_src(k_count);
            std::vector<float> v_src(v_count);

            fill_distribution(q_src, DistKind::normal_zero_mean, rng);
            fill_distribution(k_src, spec.k_dist, rng);
            fill_distribution(v_src, spec.v_dist, rng);

            const std::vector<float> ref      = run_flash_attn(GGML_TYPE_F16,  GGML_TYPE_F16,  spec, q_src, k_src, v_src);
            const std::vector<float> q8       = run_flash_attn(GGML_TYPE_Q8_0, GGML_TYPE_Q8_0, spec, q_src, k_src, v_src);
            const std::vector<float> q4       = run_flash_attn(GGML_TYPE_Q4_0, GGML_TYPE_Q4_0, spec, q_src, k_src, v_src);
            const std::vector<float> tbq4     = run_flash_attn(GGML_TYPE_TBQ4, GGML_TYPE_TBQ4, spec, q_src, k_src, v_src);
            const std::vector<float> q8_q4    = run_flash_attn(GGML_TYPE_Q8_0, GGML_TYPE_Q4_0, spec, q_src, k_src, v_src);
            const std::vector<float> q8_tbq4  = run_flash_attn(GGML_TYPE_Q8_0, GGML_TYPE_TBQ4, spec, q_src, k_src, v_src);

            std::cout << "\nCASE " << spec.name
                      << " k_dist=" << dist_name(spec.k_dist)
                      << " v_dist=" << dist_name(spec.v_dist)
                      << " gqa=" << spec.gqa
                      << " kv=" << spec.kv
                      << "\n";
            print_metric_row("q8_0", compare_outputs(ref, q8));
            print_metric_row("q4_0", compare_outputs(ref, q4));
            print_metric_row("tbq4", compare_outputs(ref, tbq4));
            print_metric_row("q8/q4", compare_outputs(ref, q8_q4));
            print_metric_row("q8/tbq4", compare_outputs(ref, q8_tbq4));
        }

        ggml_quantize_free();
        return 0;
    } catch (const std::exception & e) {
        std::cerr << "error: " << e.what() << "\n";
        ggml_quantize_free();
        return 1;
    }
}
