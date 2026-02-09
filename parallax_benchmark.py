#!/usr/bin/env python3
"""
Parallax Distributed Inference Cluster Benchmark
Tests model performance across cluster configurations with streaming TTFT measurement.

Usage:
    # Run benchmark for a single model + cluster config
    python parallax_benchmark.py --run \
        --model "openai/gpt-oss-120b" \
        --cluster-config full_cluster

    # Generate comparison report from saved results
    python parallax_benchmark.py --report benchmark_results/*.json
"""

import argparse
import json
import os
import sys
import time
import statistics
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ─── Constants ────────────────────────────────────────────────────────────────

SCHEDULER_URL = "http://169.254.150.101:3001"
API_URL = f"{SCHEDULER_URL}/v1/chat/completions"
DEFAULT_MAX_TOKENS = 500
DEFAULT_ITERATIONS = 3
DEFAULT_TIMEOUT = 600  # 10 min for large models
COOLING_SECONDS = 2


# ─── Prompt Generation ───────────────────────────────────────────────────────

# Substantive text blocks (~250 tokens each) for building calibrated prompts
TEXT_BLOCKS = [
    (
        "In statistical analysis, hypothesis testing provides a framework for making "
        "decisions about population parameters based on sample data. The null hypothesis "
        "typically represents the status quo or a default assumption, while the alternative "
        "hypothesis represents the claim we wish to evaluate. The p-value quantifies the "
        "probability of observing results at least as extreme as the sample data, assuming "
        "the null hypothesis is true. A common threshold for statistical significance is "
        "alpha equals 0.05, though this value is arbitrary and context-dependent. "
        "Researchers must consider both Type I errors, rejecting a true null hypothesis, "
        "and Type II errors, failing to reject a false null hypothesis. The power of a test "
        "is the probability of correctly rejecting a false null hypothesis and depends on "
        "sample size, effect size, and significance level. Bayesian approaches offer an "
        "alternative framework where prior beliefs are updated with observed data to form "
        "posterior distributions, providing a more intuitive interpretation of uncertainty."
    ),
    (
        "Linear regression models the relationship between a dependent variable and one "
        "or more independent variables by fitting a linear equation to observed data. The "
        "ordinary least squares method minimizes the sum of squared residuals to find the "
        "best-fitting line. Key assumptions include linearity, independence of errors, "
        "homoscedasticity, and normality of residuals. Violations of these assumptions can "
        "lead to biased or inefficient estimates. Multicollinearity occurs when predictor "
        "variables are highly correlated, inflating the variance of coefficient estimates "
        "and making individual predictors unreliable. The coefficient of determination, "
        "R-squared, measures the proportion of variance in the dependent variable explained "
        "by the model, but adding more predictors always increases R-squared regardless of "
        "their relevance. Adjusted R-squared penalizes for the number of predictors and "
        "provides a more honest assessment of model fit. Regularization techniques like "
        "ridge regression and LASSO add penalty terms to prevent overfitting and perform "
        "feature selection, respectively."
    ),
    (
        "Machine learning algorithms can be broadly categorized into supervised, "
        "unsupervised, and reinforcement learning paradigms. Supervised learning uses "
        "labeled training data to learn a mapping from inputs to outputs, with common "
        "algorithms including decision trees, random forests, support vector machines, and "
        "neural networks. Cross-validation is essential for estimating how well a model "
        "generalizes to unseen data, with k-fold cross-validation being the most widely "
        "used approach. The bias-variance tradeoff is a fundamental concept: models with "
        "high bias underfit the data and miss relevant patterns, while models with high "
        "variance overfit to noise in the training set. Ensemble methods combine multiple "
        "models to achieve better predictive performance than any single model. Gradient "
        "boosting builds trees sequentially, each correcting the errors of its predecessor, "
        "while bagging creates independent trees on bootstrap samples and aggregates their "
        "predictions. Feature engineering transforms raw data into informative features "
        "that better represent the underlying problem to the learning algorithm."
    ),
    (
        "Time series analysis involves studying data points collected over successive "
        "equally spaced intervals. Decomposition separates a time series into trend, "
        "seasonal, and residual components using either additive or multiplicative models. "
        "Stationarity is a key assumption for many forecasting methods, requiring that "
        "the statistical properties of the series remain constant over time. The "
        "Augmented Dickey-Fuller test and KPSS test assess stationarity, and differencing "
        "can transform non-stationary data. ARIMA models combine autoregressive terms, "
        "integration for differencing, and moving average components to capture temporal "
        "dependencies. Seasonal ARIMA extends this framework with seasonal parameters. "
        "Exponential smoothing methods weight recent observations more heavily, with "
        "Holt-Winters being popular for series with both trend and seasonality. Modern "
        "approaches including Prophet from Meta and neural network architectures like "
        "LSTMs and Transformers have shown strong performance on complex forecasting tasks "
        "with multiple seasonal patterns and external regressors."
    ),
    (
        "Data preprocessing is a critical step that significantly impacts model performance. "
        "Missing value imputation strategies include mean or median substitution, "
        "k-nearest neighbors imputation, and multiple imputation using chained equations. "
        "Outlier detection methods range from simple statistical approaches like the IQR "
        "method and z-score thresholds to more sophisticated techniques including isolation "
        "forests and local outlier factor analysis. Feature scaling ensures that variables "
        "with different units or ranges contribute equally to the model. Min-max scaling "
        "normalizes features to a fixed range, typically zero to one, while standardization "
        "transforms features to have zero mean and unit variance. Categorical encoding "
        "converts non-numeric features into numerical representations: one-hot encoding "
        "creates binary columns for each category, while target encoding replaces categories "
        "with their mean target value. Dimensionality reduction techniques like PCA and "
        "t-SNE reduce the feature space while preserving important structure in the data, "
        "helping mitigate the curse of dimensionality in high-dimensional datasets."
    ),
    (
        "Clustering algorithms partition data into groups where objects within a cluster "
        "are more similar to each other than to objects in other clusters. K-means is the "
        "most widely used method, iteratively assigning points to the nearest centroid and "
        "updating centroids until convergence. The algorithm is sensitive to initialization, "
        "which k-means++ addresses by spreading initial centroids apart. DBSCAN identifies "
        "clusters of arbitrary shape based on density, classifying points as core, border, "
        "or noise based on the number of neighbors within a specified radius. Hierarchical "
        "clustering builds a tree of clusters through either agglomerative bottom-up or "
        "divisive top-down approaches, with the resulting dendrogram providing insights "
        "into cluster relationships at multiple granularities. Gaussian mixture models "
        "assume data is generated from a mixture of Gaussian distributions and use the "
        "expectation-maximization algorithm to estimate parameters. Silhouette scores "
        "and the elbow method help determine the optimal number of clusters, though "
        "domain knowledge should always inform this decision."
    ),
    (
        "Natural language processing encompasses techniques for analyzing and generating "
        "human language using computational methods. Tokenization breaks text into "
        "meaningful units, with subword tokenizers like byte-pair encoding balancing "
        "vocabulary size and coverage. Word embeddings like Word2Vec and GloVe represent "
        "words as dense vectors capturing semantic relationships, while contextual "
        "embeddings from transformer models like BERT encode meaning based on surrounding "
        "context. Attention mechanisms allow models to focus on relevant parts of the "
        "input when producing each output element, enabling the processing of long "
        "sequences. Large language models pretrained on vast corpora demonstrate emergent "
        "capabilities in reasoning, translation, summarization, and code generation. "
        "Fine-tuning adapts pretrained models to specific tasks using smaller labeled "
        "datasets, while techniques like LoRA and prompt tuning reduce the computational "
        "cost of adaptation. Evaluation metrics include BLEU for translation, ROUGE for "
        "summarization, and perplexity for language modeling, though human evaluation "
        "remains essential for assessing output quality and safety."
    ),
    (
        "Experimental design principles ensure that studies yield valid and reliable "
        "conclusions about causal relationships. Randomization eliminates systematic bias "
        "by ensuring that treatment assignment is independent of potential confounders. "
        "Blocking groups similar experimental units together to reduce variability within "
        "treatment comparisons. Factorial designs study the effects of multiple factors "
        "simultaneously, allowing estimation of interaction effects that cannot be detected "
        "in one-factor-at-a-time experiments. A/B testing in technology applications is "
        "essentially a randomized controlled trial comparing a treatment variant to a "
        "control. Sample size calculations based on desired power, significance level, and "
        "minimum detectable effect size help plan experiments that are neither underpowered "
        "nor wastefully large. Multiple testing corrections like Bonferroni and "
        "Benjamini-Hochberg control the family-wise error rate or false discovery rate "
        "when many hypotheses are tested simultaneously. Sequential testing and adaptive "
        "designs allow interim analyses and modifications to the experiment based on "
        "accumulating data while maintaining statistical validity."
    ),
    (
        "Database systems provide structured storage and efficient querying of large "
        "datasets. Relational databases organize data into tables with defined schemas, "
        "using SQL for data manipulation and retrieval. Normalization reduces data "
        "redundancy and improves integrity through decomposition into well-structured "
        "tables satisfying normal forms. Indexing accelerates query performance by "
        "creating data structures that enable rapid lookup without scanning entire tables. "
        "B-tree indexes support range queries and equality comparisons, while hash indexes "
        "excel at exact match lookups. Query optimization transforms logical query plans "
        "into efficient physical execution plans, considering factors like table sizes, "
        "index availability, and join orderings. NoSQL databases offer alternatives for "
        "specific use cases: document stores for flexible schemas, key-value stores for "
        "high-throughput simple lookups, column-family stores for analytical workloads, "
        "and graph databases for relationship-heavy data. The CAP theorem states that "
        "distributed systems can guarantee at most two of consistency, availability, and "
        "partition tolerance, informing architecture decisions."
    ),
    (
        "Deep learning architectures have revolutionized artificial intelligence across "
        "multiple domains. Convolutional neural networks process spatial data through "
        "learnable filters that detect local patterns, with deeper layers combining "
        "low-level features into increasingly abstract representations. Residual "
        "connections enable training of very deep networks by allowing gradients to flow "
        "directly through skip connections. Recurrent neural networks process sequential "
        "data by maintaining hidden state across time steps, though they suffer from "
        "vanishing gradients over long sequences. The transformer architecture replaces "
        "recurrence with self-attention, enabling parallel processing and better modeling "
        "of long-range dependencies. Vision transformers apply the transformer framework "
        "to image patches, achieving competitive performance with CNNs. Generative "
        "adversarial networks train a generator and discriminator in a minimax game to "
        "produce realistic synthetic data. Diffusion models generate samples by learning "
        "to reverse a gradual noising process, producing state-of-the-art results in "
        "image synthesis. Training these models requires careful optimization including "
        "learning rate scheduling, gradient clipping, and mixed-precision computation."
    ),
]

SYSTEM_MESSAGE = (
    "You are an expert technical writer. Write a detailed, well-structured response "
    "to the analysis prompt below. Include specific examples and technical details."
)


def generate_calibrated_prompt(target_tokens: int) -> dict:
    """Generate a prompt targeting a specific token count.

    Uses ~4 chars/token heuristic. Actual token count is verified from API response.
    Returns dict with 'system' and 'user' content.
    """
    target_chars = target_tokens * 4
    # Reserve ~400 chars for the system message
    user_target_chars = target_chars - len(SYSTEM_MESSAGE)

    prefix = (
        f"Below is a collection of analytical passages covering various topics in data "
        f"science and statistics. Please read all the material carefully, then write a "
        f"comprehensive synthesis essay that connects the key themes across all passages. "
        f"Focus on practical applications and methodological connections.\n\n"
    )

    body_parts = []
    char_count = len(prefix)
    block_idx = 0

    while char_count < user_target_chars:
        block = TEXT_BLOCKS[block_idx % len(TEXT_BLOCKS)]
        # Add passage header for variety
        passage_num = (block_idx // len(TEXT_BLOCKS)) + 1
        section_num = (block_idx % len(TEXT_BLOCKS)) + 1
        header = f"--- Passage {passage_num}.{section_num} ---\n"
        body_parts.append(header + block + "\n\n")
        char_count += len(header) + len(block) + 2
        block_idx += 1

    user_content = prefix + "".join(body_parts)
    # Trim to target if overshot
    if len(user_content) > user_target_chars:
        user_content = user_content[:user_target_chars]

    return {
        "system": SYSTEM_MESSAGE,
        "user": user_content,
        "target_tokens": target_tokens,
        "actual_chars": len(SYSTEM_MESSAGE) + len(user_content),
    }


# ─── SSE Stream Parser ──────────────────────────────────────────────────────

def parse_sse_stream(response):
    """Parse OpenAI-compatible SSE stream from Parallax.

    Yields (content_delta, usage_dict_or_none, is_done) tuples.
    """
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        if not line.startswith("data: "):
            continue
        data = line[len("data: "):]
        if data.strip() == "[DONE]":
            yield ("", None, True)
            return
        try:
            chunk = json.loads(data)
            choices = chunk.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
            else:
                content = ""
            usage = chunk.get("usage", None)
            yield (content, usage, False)
        except json.JSONDecodeError:
            continue


# ─── Single Benchmark Run ────────────────────────────────────────────────────

def run_single_benchmark(
    prompt: dict,
    scheduler_url: str = SCHEDULER_URL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.1,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """Execute a single benchmark run with streaming for TTFT measurement.

    Returns dict with all metrics or error info.
    """
    api_url = f"{scheduler_url}/v1/chat/completions"

    messages = [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": prompt["user"]},
    ]

    payload = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
        "chat_template_kwargs": {"enable_thinking": False},
    }

    result = {
        "ttft": None,
        "total_time": None,
        "prompt_tokens": None,
        "completion_tokens": None,
        "prefill_speed": None,
        "decode_speed": None,
        "throughput": None,
        "generated_text_length": 0,
        "error": None,
        "streaming": True,
    }

    try:
        t_request = time.perf_counter()

        response = requests.post(api_url, json=payload, stream=True, timeout=timeout)
        response.raise_for_status()

        t_first_token = None
        full_content = []
        usage_data = None

        for content, usage, is_done in parse_sse_stream(response):
            if is_done:
                break
            if content and t_first_token is None:
                t_first_token = time.perf_counter()
            if content:
                full_content.append(content)
            if usage:
                usage_data = usage

        t_end = time.perf_counter()

        total_time = t_end - t_request
        ttft = (t_first_token - t_request) if t_first_token else total_time

        # Extract token counts from usage or estimate
        if usage_data:
            prompt_tokens = usage_data.get("prompt_tokens", 0)
            completion_tokens = usage_data.get("completion_tokens", 0)
        else:
            # Estimate from response text (~4 chars/token)
            generated_text = "".join(full_content)
            prompt_tokens = prompt.get("target_tokens", 0)
            completion_tokens = max(1, len(generated_text) // 4)

        decode_time = total_time - ttft

        result.update({
            "ttft": round(ttft, 4),
            "total_time": round(total_time, 4),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "prefill_speed": round(prompt_tokens / ttft, 1) if ttft > 0 else 0,
            "decode_speed": round(completion_tokens / decode_time, 1) if decode_time > 0 else 0,
            "throughput": round((prompt_tokens + completion_tokens) / total_time, 1) if total_time > 0 else 0,
            "generated_text_length": len("".join(full_content)),
        })

    except requests.exceptions.Timeout:
        result["error"] = f"Timeout after {timeout}s"
        print(f"    ERROR: Request timed out after {timeout}s")

    except requests.exceptions.ConnectionError as e:
        result["error"] = f"Connection failed: {e}"
        print(f"    ERROR: Connection failed - is the cluster running?")

        # Try non-streaming fallback
        return _run_non_streaming_fallback(prompt, scheduler_url, max_tokens, temperature, timeout)

    except Exception as e:
        result["error"] = str(e)
        print(f"    ERROR: {e}")

        # Try non-streaming fallback
        return _run_non_streaming_fallback(prompt, scheduler_url, max_tokens, temperature, timeout)

    return result


def _run_non_streaming_fallback(
    prompt: dict,
    scheduler_url: str,
    max_tokens: int,
    temperature: float,
    timeout: int,
) -> dict:
    """Fallback to non-streaming mode if streaming fails."""
    api_url = f"{scheduler_url}/v1/chat/completions"
    print("    Falling back to non-streaming mode (TTFT unavailable)...")

    messages = [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": prompt["user"]},
    ]

    payload = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }

    result = {
        "ttft": None,
        "total_time": None,
        "prompt_tokens": None,
        "completion_tokens": None,
        "prefill_speed": None,
        "decode_speed": None,
        "throughput": None,
        "generated_text_length": 0,
        "error": None,
        "streaming": False,
    }

    try:
        t_request = time.perf_counter()
        response = requests.post(api_url, json=payload, timeout=timeout)
        response.raise_for_status()
        t_end = time.perf_counter()

        data = response.json()
        total_time = t_end - t_request

        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        generated_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        result.update({
            "total_time": round(total_time, 4),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "throughput": round((prompt_tokens + completion_tokens) / total_time, 1) if total_time > 0 else 0,
            "generated_text_length": len(generated_text),
        })

    except Exception as e:
        result["error"] = f"Non-streaming fallback also failed: {e}"
        print(f"    ERROR: Fallback failed: {e}")

    return result


# ─── Benchmark Suite ─────────────────────────────────────────────────────────

def verify_cluster(scheduler_url: str = SCHEDULER_URL, retries: int = 6) -> bool:
    """Verify the Parallax cluster is online and responding."""
    for i in range(retries):
        try:
            r = requests.get(f"{scheduler_url}/", timeout=5)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        if i < retries - 1:
            print(f"  Cluster not ready, retrying in 10s... ({i+1}/{retries})")
            time.sleep(10)
    return False


def run_warmup(scheduler_url: str = SCHEDULER_URL):
    """Send a short warmup request to prime the model."""
    print("  Running warmup request...")
    api_url = f"{scheduler_url}/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": "Hello, respond with one word."}],
        "max_tokens": 10,
        "temperature": 0.1,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    try:
        r = requests.post(api_url, json=payload, timeout=120)
        if r.status_code == 200:
            print("  Warmup complete.")
        else:
            print(f"  Warmup returned status {r.status_code}")
    except Exception as e:
        print(f"  Warmup failed: {e}")


def compute_stats(values: List[float]) -> dict:
    """Compute summary statistics for a list of values."""
    if not values:
        return {"mean": None, "median": None, "stdev": None, "min": None, "max": None}
    if len(values) == 1:
        v = values[0]
        return {"mean": v, "median": v, "stdev": 0, "min": v, "max": v}
    return {
        "mean": round(statistics.mean(values), 4),
        "median": round(statistics.median(values), 4),
        "stdev": round(statistics.stdev(values), 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def run_benchmark_suite(
    model_name: str,
    cluster_config: str,
    prompt_sizes: List[int],
    iterations: int = DEFAULT_ITERATIONS,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    warmup: bool = True,
    scheduler_url: str = SCHEDULER_URL,
) -> dict:
    """Run full benchmark suite for one model + one cluster configuration.

    Returns results dict with per-prompt-size iteration data and statistics.
    """
    print(f"\n{'='*70}")
    print(f"BENCHMARK: {model_name}")
    print(f"Config: {cluster_config} | Max tokens: {max_tokens} | Iterations: {iterations}")
    print(f"Scheduler: {scheduler_url}")
    print(f"{'='*70}")

    # Verify cluster
    print("\nVerifying cluster is online...")
    if not verify_cluster(scheduler_url):
        print("ERROR: Cluster is not responding. Aborting benchmark.")
        return {"error": "Cluster not responding"}

    # Warmup
    if warmup:
        run_warmup(scheduler_url)

    results = {}

    for target_tokens in prompt_sizes:
        print(f"\n--- Prompt size: ~{target_tokens} tokens ---")
        prompt = generate_calibrated_prompt(target_tokens)
        print(f"  Generated prompt: {prompt['actual_chars']} chars "
              f"(targeting ~{target_tokens} tokens)")

        iteration_results = []
        for i in range(iterations):
            print(f"\n  Iteration {i+1}/{iterations}...")
            run_result = run_single_benchmark(
                prompt=prompt,
                scheduler_url=scheduler_url,
                max_tokens=max_tokens,
                temperature=0.1,
            )

            run_result["iteration"] = i + 1
            iteration_results.append(run_result)

            if run_result["error"]:
                print(f"    FAILED: {run_result['error']}")
            else:
                print(f"    TTFT:       {run_result['ttft']:.3f}s")
                print(f"    Total:      {run_result['total_time']:.3f}s")
                print(f"    Prefill:    {run_result['prefill_speed']:.1f} tok/s")
                print(f"    Decode:     {run_result['decode_speed']:.1f} tok/s")
                print(f"    Throughput: {run_result['throughput']:.1f} tok/s")
                print(f"    Tokens:     {run_result['prompt_tokens']}p + "
                      f"{run_result['completion_tokens']}c")

            if i < iterations - 1:
                time.sleep(COOLING_SECONDS)

        # Compute statistics over successful runs
        successful = [r for r in iteration_results if r["error"] is None]

        stats = {}
        for metric in ["ttft", "total_time", "prefill_speed", "decode_speed", "throughput"]:
            values = [r[metric] for r in successful if r[metric] is not None]
            stats[metric] = compute_stats(values)

        # Actual prompt tokens (should be consistent across runs)
        actual_prompt_tokens = None
        for r in successful:
            if r["prompt_tokens"]:
                actual_prompt_tokens = r["prompt_tokens"]
                break

        results[str(target_tokens)] = {
            "target_prompt_tokens": target_tokens,
            "actual_prompt_tokens": actual_prompt_tokens,
            "iterations": iteration_results,
            "statistics": stats,
            "successful_runs": len(successful),
            "total_runs": len(iteration_results),
        }

    return results


# ─── Report Generator ────────────────────────────────────────────────────────

def format_stat(stat: dict, unit: str = "") -> str:
    """Format a stat dict as 'mean +/- stdev unit'."""
    if not stat or stat["mean"] is None:
        return "N/A"
    if stat["stdev"] and stat["stdev"] > 0:
        return f"{stat['mean']:.2f} +/- {stat['stdev']:.2f}{unit}"
    return f"{stat['mean']:.2f}{unit}"


def format_stat_short(stat: dict) -> float:
    """Return just the mean value."""
    if not stat or stat["mean"] is None:
        return None
    return stat["mean"]


def _delta_str(val_a: Optional[float], val_b: Optional[float]) -> str:
    """Compute percent delta string between two values. Empty if either is None."""
    if val_a is None or val_b is None or val_b == 0:
        return ""
    pct = ((val_a - val_b) / abs(val_b)) * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def generate_comparison_report(result_files: List[str]) -> str:
    """Generate formatted comparison report from JSON result files.

    Supports 3-way comparison: full_cluster vs macs_only vs sparks_only.
    """
    CONFIG_LABELS = {
        "full_cluster": "Full Cluster (Macs+Sparks)",
        "macs_only": "Macs Only (2x Mac Studio)",
        "sparks_only": "Sparks Only (2x DGX Spark)",
    }
    CONFIG_ORDER = ["full_cluster", "macs_only", "sparks_only"]

    # Load all results
    all_results = []
    for fpath in result_files:
        with open(fpath, "r") as f:
            data = json.load(f)
            all_results.append(data)

    # Group by model → config
    models = {}
    for data in all_results:
        model = data["metadata"]["model"]
        config = data["metadata"]["cluster_config"]
        if model not in models:
            models[model] = {}
        models[model][config] = data

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("=" * 100)
    lines.append("PARALLAX BENCHMARK COMPARISON REPORT")
    lines.append(f"Generated: {timestamp}")
    lines.append("")

    # Show which configs were tested
    all_configs = set()
    for configs in models.values():
        all_configs.update(configs.keys())
    for cfg in CONFIG_ORDER:
        if cfg in all_configs:
            lines.append(f"  {CONFIG_LABELS.get(cfg, cfg)}")
    lines.append("=" * 100)

    # Per-config pair deltas for summary
    pair_deltas = {}  # (config_a, config_b) → list of improvement %

    metrics_list = [
        ("TTFT (s)", "ttft", True),        # True = lower is better
        ("Total Time (s)", "total_time", True),
        ("Prefill (tok/s)", "prefill_speed", False),
        ("Decode (tok/s)", "decode_speed", False),
        ("Throughput (tok/s)", "throughput", False),
    ]

    for model_name, configs in models.items():
        lines.append(f"\n{'─'*100}")
        lines.append(f"MODEL: {model_name}")
        lines.append(f"{'─'*100}")

        # Determine which configs exist for this model
        available_configs = [c for c in CONFIG_ORDER if c in configs]
        if not available_configs:
            lines.append("  No results available for this model.")
            continue

        # Collect all prompt sizes
        all_ps = set()
        for cfg in available_configs:
            results = configs[cfg].get("results", {})
            all_ps.update(results.keys())
        prompt_sizes = sorted(all_ps, key=int)

        for ps in prompt_sizes:
            # Get stats per config
            config_stats = {}
            config_data = {}
            for cfg in available_configs:
                data = configs[cfg].get("results", {}).get(ps, {})
                config_data[cfg] = data
                config_stats[cfg] = data.get("statistics", {})

            actual_tokens = None
            for cfg in available_configs:
                actual_tokens = config_data[cfg].get("actual_prompt_tokens")
                if actual_tokens:
                    break
            actual_tokens = actual_tokens or ps

            lines.append(f"\n  Prompt: ~{ps} tokens (actual: {actual_tokens})")

            # Success rates
            success_parts = []
            for cfg in available_configs:
                d = config_data[cfg]
                short_name = cfg.replace("_cluster", "").replace("_only", "").capitalize()
                success_parts.append(f"{short_name}: {d.get('successful_runs', '?')}/{d.get('total_runs', '?')}")
            lines.append(f"  Runs: {' | '.join(success_parts)}")
            lines.append("")

            # Build column widths based on how many configs
            n_configs = len(available_configs)
            col_w = max(20, 80 // n_configs)

            # Header
            header_parts = [f"{'Metric':<20}"]
            for cfg in available_configs:
                short = CONFIG_LABELS.get(cfg, cfg)[:col_w-2]
                header_parts.append(f"{short:<{col_w}}")
            # Delta columns (each pair)
            if n_configs >= 2:
                header_parts.append("Deltas")
            lines.append("  " + " ".join(header_parts))
            lines.append("  " + "─" * (20 + col_w * n_configs + 30))

            for label, key, lower_is_better in metrics_list:
                row_parts = [f"{label:<20}"]
                vals = {}
                for cfg in available_configs:
                    stat = config_stats[cfg].get(key, {})
                    row_parts.append(f"{format_stat(stat):<{col_w}}")
                    vals[cfg] = format_stat_short(stat)

                # Deltas: compare each pair
                delta_parts = []
                pairs = []
                if "full_cluster" in vals and "macs_only" in vals:
                    pairs.append(("full_cluster", "macs_only", "Full/Macs"))
                if "full_cluster" in vals and "sparks_only" in vals:
                    pairs.append(("full_cluster", "sparks_only", "Full/Sparks"))
                if "macs_only" in vals and "sparks_only" in vals:
                    pairs.append(("macs_only", "sparks_only", "Macs/Sparks"))

                for cfg_a, cfg_b, pair_label in pairs:
                    d = _delta_str(vals[cfg_a], vals[cfg_b])
                    if d:
                        delta_parts.append(f"{pair_label}:{d}")

                        # Track for summary (normalize: positive = config_a is better)
                        va, vb = vals[cfg_a], vals[cfg_b]
                        if va is not None and vb is not None and vb != 0:
                            raw_pct = ((va - vb) / abs(vb)) * 100
                            # For lower-is-better metrics, flip sign
                            improvement = -raw_pct if lower_is_better else raw_pct
                            pair_key = (cfg_a, cfg_b)
                            pair_deltas.setdefault(pair_key, []).append(
                                (improvement, label, model_name, ps)
                            )

                row_parts.append("  ".join(delta_parts))
                lines.append("  " + " ".join(row_parts))

    # ─── Summary ──────────────────────────────────────────────────────────
    lines.append(f"\n{'='*100}")
    lines.append("SUMMARY")
    lines.append(f"{'='*100}")

    if pair_deltas:
        for (cfg_a, cfg_b), deltas in sorted(pair_deltas.items()):
            label_a = CONFIG_LABELS.get(cfg_a, cfg_a)
            label_b = CONFIG_LABELS.get(cfg_b, cfg_b)
            improvements = [d[0] for d in deltas]
            avg = statistics.mean(improvements)

            if avg >= 0:
                lines.append(f"\n  {label_a} is {abs(avg):.1f}% faster than {label_b} on average")
            else:
                lines.append(f"\n  {label_a} is {abs(avg):.1f}% slower than {label_b} on average")

            best = max(deltas, key=lambda x: x[0])
            worst = min(deltas, key=lambda x: x[0])
            lines.append(f"    Best:  {best[1]} on {best[2]} @{best[3]}tok "
                         f"({'+' if best[0]>=0 else ''}{best[0]:.1f}%)")
            lines.append(f"    Worst: {worst[1]} on {worst[2]} @{worst[3]}tok "
                         f"({'+' if worst[0]>=0 else ''}{worst[0]:.1f}%)")
    else:
        lines.append("\nInsufficient data for comparison summary.")

    lines.append(f"\n{'='*100}")

    return "\n".join(lines)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Parallax Distributed Inference Cluster Benchmark"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Run subcommand
    run_parser = subparsers.add_parser("run", help="Run benchmark for a model + config")
    run_parser.add_argument("--model", type=str, required=True, help="HuggingFace model ID")
    run_parser.add_argument(
        "--cluster-config", type=str, required=True,
        choices=["full_cluster", "macs_only", "sparks_only"],
        help="Cluster configuration being tested",
    )
    run_parser.add_argument(
        "--prompt-sizes", nargs="+", type=int, default=[2500, 6500],
        help="Target prompt token sizes (default: 2500 6500)",
    )
    run_parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    run_parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    run_parser.add_argument("--output-dir", type=str, default="benchmark_results")
    run_parser.add_argument("--no-warmup", action="store_true")
    run_parser.add_argument("--scheduler-url", type=str, default=SCHEDULER_URL)

    # Report subcommand
    report_parser = subparsers.add_parser("report", help="Generate comparison report")
    report_parser.add_argument("files", nargs="+", help="JSON result files to compare")
    report_parser.add_argument("--output-dir", type=str, default="benchmark_results")

    # Legacy --run / --report flags for backward compat with shell script
    parser.add_argument("--run", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--report", nargs="*", help=argparse.SUPPRESS)
    parser.add_argument("--model", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--cluster-config", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--prompt-sizes", nargs="+", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--iterations", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--max-tokens", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--output-dir", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--no-warmup", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--scheduler-url", type=str, help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Handle legacy flags
    if args.command is None:
        if getattr(args, "run", False) and args.model and args.cluster_config:
            args.command = "run"
            args.prompt_sizes = args.prompt_sizes or [2500, 6500]
            args.iterations = args.iterations or DEFAULT_ITERATIONS
            args.max_tokens = args.max_tokens or DEFAULT_MAX_TOKENS
            args.output_dir = args.output_dir or "benchmark_results"
            args.scheduler_url = args.scheduler_url or SCHEDULER_URL
        elif getattr(args, "report", None) is not None:
            args.command = "report"
            args.files = args.report
            args.output_dir = args.output_dir or "benchmark_results"
        else:
            parser.print_help()
            sys.exit(1)

    if args.command == "run":
        # Run benchmark
        results = run_benchmark_suite(
            model_name=args.model,
            cluster_config=args.cluster_config,
            prompt_sizes=args.prompt_sizes,
            iterations=args.iterations,
            max_tokens=args.max_tokens,
            warmup=not args.no_warmup,
            scheduler_url=args.scheduler_url,
        )

        # Save results
        os.makedirs(args.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_slug = args.model.replace("/", "_")
        output_file = os.path.join(
            args.output_dir,
            f"{args.cluster_config}_{model_slug}_{timestamp}.json",
        )

        output_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "model": args.model,
                "cluster_config": args.cluster_config,
                "scheduler_url": args.scheduler_url,
                "max_tokens": args.max_tokens,
                "iterations": args.iterations,
                "prompt_sizes": args.prompt_sizes,
            },
            "results": results,
        }

        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    elif args.command == "report":
        if not args.files:
            print("ERROR: No result files specified.")
            sys.exit(1)

        report = generate_comparison_report(args.files)
        print(report)

        # Save report
        os.makedirs(args.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(args.output_dir, f"comparison_report_{timestamp}.txt")
        with open(report_file, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
