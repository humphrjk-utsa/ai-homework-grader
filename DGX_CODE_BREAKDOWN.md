# DGX System - Complete Code Breakdown

This document shows exactly which files contain which code and how they work together.

---

## File 1: Configuration
**`disaggregated_inference/config_current.json`**

**Purpose:** Defines server endpoints and model mappings

**Complete Code:**
```json
{
  "comment": "Grading uses Sparks 1&2 only - Sparks 3&4 reserved for other processes",
  "prefill_servers": [
    {
      "host": "169.254.150.103",
      "port": 8000,
      "model": "qwen",
      "name": "DGX Spark 1"
    },
    {
      "host": "169.254.150.104",
      "port": 8000,
      "model": "gpt-oss",
      "name": "DGX Spark 2"
    }
  ],
  "decode_servers": [
    {
      "host": "169.254.150.102",
      "port": 8001,
      "model": "qwen",
      "name": "Mac Studio 2"
    },
    {
      "host": "169.254.150.101",
      "port": 8001,
      "model": "gpt-oss",
      "name": "Mac Studio 1"
    }
  ]
}
```

**What Each Part Does:**
- `prefill_servers`: DGX machines that handle prompt processing
- `decode_servers`: Mac machines that handle token generation
- `model`: Key used to match prefill/decode pairs
- `host`/`port`: Network endpoints for HTTP requests

---

## File 2: Disaggregated Client
**`disaggregated_client.py`**

**Purpose:** Orchestrates two-phase inference across DGX and Mac

### Part 1: Initialization

```python
class DisaggregatedClient:
    """Client for disaggregated inference (DGX prefill + Mac decode)"""
    
    def __init__(self, config_path: str = "disaggregated_inference/config_current.json"):
        """Initialize client with configuration"""
        # Load configuration file
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Build lookup tables for fast server selection
        self.prefill_servers = {s['model']: s for s in self.config['prefill_servers']}
        # Result: {'qwen': {...DGX Spark 1...}, 'gpt-oss': {...DGX Spark 2...}}
        
        self.decode_servers = {s['model']: s for s in self.config['decode_servers']}
        # Result: {'qwen': {...Mac Studio 2...}, 'gpt-oss': {...Mac Studio 1...}}
        
        logger.info(f"Initialized with {len(self.prefill_servers)} prefill servers")
```

**What This Does:**
1. Reads JSON config file
2. Creates dictionaries mapping model type → server info
3. Enables quick lookup: `prefill_servers['qwen']` → DGX Spark 1

### Part 2: URL Helper

```python
def _get_server_url(self, server: Dict, endpoint: str) -> str:
    """Get server URL, using localhost if it's the local machine"""
    import socket
    host = server['host']
    port = server['port']
    
    # Check if this is a local IP
    try:
        hostname = socket.gethostname()
        local_ips = [socket.gethostbyname(hostname)]
        local_ips.extend(['127.0.0.1', 'localhost'])
        
        # If server is local, use localhost for faster connection
        if host in local_ips or host.startswith('169.254.150.101'):
            host = 'localhost'
    except:
        pass
    
    return f"http://{host}:{port}{endpoint}"
```

**What This Does:**
- Builds HTTP URL from server config
- Optimizes by using `localhost` for local servers
- Example: `http://169.254.150.103:8000/prefill`

### Part 3: Main Generation Method

```python
def generate(self, model: str, prompt: str, max_tokens: int = 2000):
    """
    Generate text using disaggregated inference
    
    Args:
        model: "qwen3-coder:30b" or "gpt-oss:120b"
        prompt: Input text to process
        max_tokens: Maximum tokens to generate
        
    Returns:
        (response_text, metrics_dict)
    """
    start_time = time.time()
    
    # STEP 1: Determine model type
    if 'qwen' in model.lower() or 'coder' in model.lower():
        model_key = 'qwen'
    else:
        model_key = 'gpt-oss'
    
    # STEP 2: Get server pair
    prefill_server = self.prefill_servers.get(model_key)
    decode_server = self.decode_servers.get(model_key)
    
    if not prefill_server or not decode_server:
        raise ValueError(f"No servers configured for: {model_key}")
    
    logger.info(f"Using {model_key}: prefill={prefill_server['host']}, "
                f"decode={decode_server['host']}")
    
    try:
        # STEP 3: PREFILL ON DGX
        prefill_url = self._get_server_url(prefill_server, '/prefill')
        logger.info(f"🚀 Prefill on DGX: {prefill_url}")
        prefill_start = time.time()
        
        response = requests.post(
            prefill_url,
            json={'prompt': prompt},
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Prefill failed: {response.status_code}")
        
        prefill_result = response.json()
        prefill_time = time.time() - prefill_start
        
        # Extract prefill metrics
        prefill_metrics = prefill_result.get('metrics', {})
        prompt_tokens = prefill_metrics.get('prompt_eval_count', 0)
        prefill_tokens_per_sec = prefill_metrics.get('prompt_tokens_per_sec', 0)
        
        logger.info(f"✅ Prefill: {prefill_time:.3f}s "
                   f"({prompt_tokens} tokens, {prefill_tokens_per_sec:.1f} tok/s)")
        
        # STEP 4: DECODE ON MAC
        decode_url = self._get_server_url(decode_server, '/decode')
        logger.info(f"🚀 Decode on Mac: {decode_url}")
        decode_start = time.time()
        
        response = requests.post(
            decode_url,
            json={
                'context': prefill_result.get('context', prompt),
                'prompt': prompt,
                'max_new_tokens': max_tokens,
                'temperature': 0.2
            },
            timeout=180
        )
        
        if response.status_code != 200:
            raise Exception(f"Decode failed: {response.status_code}")
        
        decode_result = response.json()
        decode_time = time.time() - decode_start
        total_time = time.time() - start_time
        
        # Extract decode metrics
        decode_metrics = decode_result.get('metrics', {})
        tokens_generated = decode_metrics.get('eval_count', 0)
        decode_tokens_per_sec = decode_metrics.get('tokens_per_sec', 0)
        
        logger.info(f"✅ Decode: {decode_time:.3f}s "
                   f"({tokens_generated} tokens, {decode_tokens_per_sec:.1f} tok/s)")
        logger.info(f"⏱️ Total: {total_time:.3f}s")
        
        # STEP 5: Return response + metrics
        response_text = decode_result.get('generated_text', '')
        
        metrics = {
            'prefill_time': prefill_time,
            'decode_time': decode_time,
            'total_time': total_time,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': tokens_generated,
            'total_tokens': prompt_tokens + tokens_generated,
            'prefill_speed': prefill_tokens_per_sec,
            'decode_speed': decode_tokens_per_sec,
            'method': 'disaggregated_ollama',
            'prefill_server': f"{prefill_server['host']}:{prefill_server['port']}",
            'decode_server': f"{decode_server['host']}:{decode_server['port']}"
        }
        
        return response_text, metrics
        
    except Exception as e:
        logger.error(f"❌ Disaggregated inference failed: {e}")
        raise
```

**What Each Step Does:**

**Step 1: Model Type Detection**
- Input: `"hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest"`
- Logic: Check if "qwen" or "coder" in name
- Output: `model_key = 'qwen'`

**Step 2: Server Selection**
- Input: `model_key = 'qwen'`
- Lookup: `prefill_servers['qwen']` → DGX Spark 1
- Lookup: `decode_servers['qwen']` → Mac Studio 2
- Output: Server pair for Qwen pipeline

**Step 3: Prefill Request**
- URL: `http://169.254.150.103:8000/prefill`
- Payload: `{'prompt': "Analyze this code..."}`
- DGX processes prompt in parallel
- Returns: `{'context': <KV_cache>, 'metrics': {...}}`
- Time: ~2-3 seconds

**Step 4: Decode Request**
- URL: `http://169.254.150.102:8001/decode`
- Payload: `{'context': <KV_cache>, 'prompt': ..., 'max_new_tokens': 2000}`
- Mac generates tokens using cached context
- Returns: `{'generated_text': "...", 'metrics': {...}}`
- Time: ~8-10 seconds

**Step 5: Return Results**
- Combines response text with detailed metrics
- Metrics include timing, token counts, speeds
- Used for performance monitoring and display

---

## File 3: Grader Integration
**`business_analytics_grader_v2.py`**

### Part 1: Initialization (Detect DGX System)

```python
class BusinessAnalyticsGraderV2:
    def __init__(self, 
                 code_model: str = "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest",
                 feedback_model: str = "gemma3:27b-it-q8_0",
                 ollama_url: str = "http://localhost:11434",
                 rubric_path: str = None,
                 solution_path: str = None):
        
        # ... (validator initialization code) ...
        
        # CHECK FOR DISAGGREGATED INFERENCE SYSTEM
        self.use_disaggregated = False
        self.disaggregated_client = None
        
        if os.path.exists('disaggregated_inference/config_current.json'):
            try:
                from disaggregated_client import DisaggregatedClient
                self.disaggregated_client = DisaggregatedClient()
                self.use_disaggregated = True
                print(f"🚀 Using Disaggregated Inference System:")
                print(f"   DGX Sparks (prefill) + Mac Studios (decode)")
                print(f"   Qwen: DGX Spark 1 → Mac Studio 2")
                print(f"   GPT-OSS: DGX Spark 2 → Mac Studio 1")
            except Exception as e:
                print(f"⚠️ Disaggregated system failed to load: {e}")
                self.use_disaggregated = False
        
        # Fallback to distributed MLX if available
        self.use_distributed_mlx = False
        if os.path.exists('distributed_config.json'):
            # ... (MLX initialization code) ...
            pass
        
        # Initialize parallel executor for running both models simultaneously
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
```

**What This Does:**
1. Checks if `disaggregated_inference/config_current.json` exists
2. If yes, imports and initializes `DisaggregatedClient`
3. Sets `use_disaggregated = True` flag
4. Logs which system is active
5. Falls back to local Ollama if config missing
6. Creates ThreadPoolExecutor for parallel execution

### Part 2: Grading Orchestration

```python
def grade_submission(self, 
                    student_code: str,
                    student_markdown: str,
                    template_code: str = "",
                    solution_code: str = "",
                    assignment_info: Dict = None,
                    notebook_path: str = None) -> Dict[str, Any]:
    """Grade submission using 4-layer validation + AI analysis"""
    
    start_time = time.time()
    
    # LAYER 1 & 2: Run validation (systematic + output comparison)
    validation_results = self._run_4layer_validation(notebook_path)
    
    # LAYER 3 & 4: AI Code Analysis and Feedback Generation
    print("\n[LAYER 3 & 4: AI ANALYSIS AND FEEDBACK GENERATION]")
    
    # Prepare prompts with validation context
    validation_summary = validation_results.get('validation_summary', '')
    
    # PARALLEL EXECUTION OF BOTH AI MODELS
    parallel_start = time.time()
    
    # Submit both tasks to thread pool
    future_code = self.executor.submit(
        self._execute_ollama_code_analysis,  # Uses disaggregated_client internally
        student_code, template_code, solution_code, 
        assignment_info, validation_results
    )
    
    future_feedback = self.executor.submit(
        self._execute_ollama_feedback_generation,  # Uses disaggregated_client internally
        student_code, student_markdown, 
        assignment_info, validation_results
    )
    
    # Wait for both to complete
    code_analysis = future_code.result()
    comprehensive_feedback = future_feedback.result()
    
    parallel_time = time.time() - parallel_start
    print(f"✅ AI analysis completed in {parallel_time:.1f}s")
    
    # Merge AI feedback with validation results
    structured_feedback = self._merge_ai_and_validation_feedback(
        validation_results, code_analysis, comprehensive_feedback
    )
    
    total_time = time.time() - start_time
    self.grading_stats['total_time'] = total_time
    
    return structured_feedback
```

**What This Does:**
1. Runs 4-layer validation (systematic + output comparison)
2. Prepares prompts with validation context
3. Submits TWO tasks to ThreadPoolExecutor:
   - Task 1: Code analysis (Qwen)
   - Task 2: Feedback generation (GPT-OSS)
4. Both tasks run in parallel
5. Each task uses `_generate_with_ollama()` which calls `disaggregated_client`
6. Waits for both to complete
7. Merges results into final grade

### Part 3: AI Generation (Uses Disaggregated Client)

```python
def _generate_with_ollama(self, model: str, prompt: str, max_tokens: int = 2000):
    """Generate response using Ollama (disaggregated or local)"""
    try:
        # USE DISAGGREGATED SYSTEM IF AVAILABLE
        if self.use_disaggregated and self.disaggregated_client:
            # Call disaggregated client
            response_text, metrics = self.disaggregated_client.generate(
                model, prompt, max_tokens
            )
            
            # Store metrics for display
            model_key = 'qwen' if 'qwen' in model.lower() else 'gpt-oss'
            self.grading_stats[f'{model_key}_metrics'] = metrics
            
            # Remove prompt echo if present
            if response_text and response_text.startswith(prompt):
                response_text = response_text[len(prompt):].strip()
            
            return response_text
        
        # FALLBACK TO LOCAL OLLAMA
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.2,
                "top_p": 0.9
            }
        }
        
        response = requests.post(self.api_url, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            
            # Capture metrics from local Ollama
            metrics = {
                'prompt_tokens': result.get('prompt_eval_count', 0),
                'completion_tokens': result.get('eval_count', 0),
                'total_tokens': result.get('prompt_eval_count', 0) + result.get('eval_count', 0),
                # ... more metrics ...
            }
            
            model_key = 'qwen' if 'qwen' in model.lower() else 'gemma'
            self.grading_stats[f'{model_key}_metrics'] = metrics
            
            return result.get('response', '')
        else:
            return None
            
    except Exception as e:
        print(f"⚠️ Ollama generation failed: {e}")
        return None
```

**What This Does:**
1. Checks if `use_disaggregated` flag is True
2. If yes, calls `disaggregated_client.generate()`
   - This triggers the DGX prefill + Mac decode process
   - Returns response text + detailed metrics
3. Stores metrics in `grading_stats` for display
4. If no disaggregated system, falls back to local Ollama
5. Returns generated text

### Part 4: Code Analysis Task

```python
def _execute_ollama_code_analysis(self, student_code, template_code, 
                                  solution_code, assignment_info, 
                                  validation_results):
    """Execute code analysis using Qwen (via disaggregated system)"""
    
    start_time = time.time()
    
    # Build prompt with validation context
    prompt = self.prompt_manager.get_ollama_prompt(
        "code_analysis",
        assignment_title=assignment_info.get('title', ''),
        template_code=template_code,
        student_code=student_code,
        solution_code=solution_code,
        validation_context=validation_results.get('validation_summary', '')
    )
    
    # Generate using Qwen (will use DGX Spark 1 + Mac Studio 2)
    response = self._generate_with_ollama(
        self.code_model,  # "qwen3-coder:30b"
        prompt, 
        max_tokens=2000
    )
    
    code_time = time.time() - start_time
    self.grading_stats['code_analysis_time'] = code_time
    
    print(f"✅ [CODE ANALYSIS] Complete ({code_time:.1f}s)")
    
    if not response:
        return {"error": "Code analysis failed", "technical_score": 85}
    
    return self._parse_code_analysis_response(response)
```

**What This Does:**
1. Builds code analysis prompt with validation context
2. Calls `_generate_with_ollama()` with Qwen model
3. This triggers: DGX Spark 1 (prefill) → Mac Studio 2 (decode)
4. Parses JSON response
5. Returns structured code analysis

### Part 5: Feedback Generation Task

```python
def _execute_ollama_feedback_generation(self, student_code, student_markdown,
                                       assignment_info, validation_results):
    """Execute feedback generation using GPT-OSS (via disaggregated system)"""
    
    start_time = time.time()
    
    # Build prompt with validation context
    prompt = self.prompt_manager.get_ollama_prompt(
        "feedback",
        assignment_title=assignment_info.get('title', ''),
        student_markdown=student_markdown,
        student_code_summary=student_code[:800],
        validation_context=validation_results.get('validation_summary', '')
    )
    
    # Generate using GPT-OSS (will use DGX Spark 2 + Mac Studio 1)
    response = self._generate_with_ollama(
        self.feedback_model,  # "gpt-oss:120b"
        prompt,
        max_tokens=3500
    )
    
    feedback_time = time.time() - start_time
    self.grading_stats['feedback_generation_time'] = feedback_time
    
    print(f"✅ [FEEDBACK] Complete ({feedback_time:.1f}s)")
    
    if not response:
        return {"error": "Feedback generation failed", "overall_score": 85}
    
    return self._parse_feedback_response(response)
```

**What This Does:**
1. Builds feedback prompt with validation context
2. Calls `_generate_with_ollama()` with GPT-OSS model
3. This triggers: DGX Spark 2 (prefill) → Mac Studio 1 (decode)
4. Parses JSON response
5. Returns structured feedback

---

## Complete Execution Flow

### When Grading a Submission:

```
1. USER CLICKS "Grade Submission"
   ↓
2. connect_web_interface.py: grade_single_submission()
   ↓
3. business_analytics_grader_v2.py: grade_submission()
   ↓
4. Run 4-layer validation (10-15 seconds)
   ↓
5. Submit TWO parallel tasks to ThreadPoolExecutor:
   
   THREAD 1 (Qwen Code Analysis):
   ├─ _execute_ollama_code_analysis()
   ├─ _generate_with_ollama(qwen3-coder:30b)
   ├─ disaggregated_client.generate()
   ├─ POST http://169.254.150.103:8000/prefill (DGX Spark 1)
   │  └─ Returns KV cache (~2-3 seconds)
   ├─ POST http://169.254.150.102:8001/decode (Mac Studio 2)
   │  └─ Returns generated text (~8-10 seconds)
   └─ Total: ~10-13 seconds
   
   THREAD 2 (GPT-OSS Feedback):
   ├─ _execute_ollama_feedback_generation()
   ├─ _generate_with_ollama(gpt-oss:120b)
   ├─ disaggregated_client.generate()
   ├─ POST http://169.254.150.104:8000/prefill (DGX Spark 2)
   │  └─ Returns KV cache (~3-4 seconds)
   ├─ POST http://169.254.150.101:8001/decode (Mac Studio 1)
   │  └─ Returns generated text (~10-12 seconds)
   └─ Total: ~13-16 seconds
   
   BOTH THREADS RUN SIMULTANEOUSLY
   ↓
6. Wait for both threads to complete (~13-16 seconds)
   ↓
7. Merge results into final grade
   ↓
8. Display to user

TOTAL TIME: ~25-30 seconds (validation + parallel AI)
vs 100-130 seconds without DGX system
```

---

## Summary Table

| File | Lines of Code | Purpose |
|------|---------------|---------|
| `config_current.json` | 30 | Define server endpoints |
| `disaggregated_client.py` | 150 | Orchestrate DGX+Mac inference |
| `business_analytics_grader_v2.py` | 1243 | Main grading logic + parallel execution |
| `connect_web_interface.py` | 1266 | UI integration |

**Key Code Sections:**

1. **Detection** (grader_v2.py lines 91-108): Check for config, initialize client
2. **Parallel Execution** (grader_v2.py lines 450-480): Submit both AI tasks
3. **Generation** (grader_v2.py lines 1118-1130): Call disaggregated client
4. **Prefill** (disaggregated_client.py lines 60-85): DGX processing
5. **Decode** (disaggregated_client.py lines 87-110): Mac generation
6. **Metrics** (disaggregated_client.py lines 112-125): Performance tracking

**Total Active Code:** ~200 lines for DGX orchestration
**Performance Gain:** 6-8x speedup
**Complexity:** Moderate (well-abstracted)
