## 8. Related Work

### 8.1 Automated Grading Systems

**Traditional Approaches**:
- **AutoGradr** (Ala-Mutka, 2005): Test case-based grading
- **Web-CAT** (Edwards, 2003): Unit test execution
- **Gradescope** (Singh et al., 2017): Rubric-based manual grading with AI assistance

**Limitations**: Focus on correctness testing, limited feedback generation

### 8.2 LLM-based Grading

**Recent Work**:
- **CodeBERT** (Feng et al., 2020): Code understanding with transformers
- **GPT-4 for Grading** (OpenAI, 2023): General-purpose LLM for assessment
- **Codex** (Chen et al., 2021): Code generation and evaluation

**Our Contribution**: Hybrid validation + specialized dual-LLM architecture

### 8.3 Educational AI Systems

**Intelligent Tutoring Systems**:
- **Carnegie Learning** (Koedinger et al., 1997): Adaptive learning
- **ASSISTments** (Heffernan & Heffernan, 2014): Formative assessment

**Difference**: Our system focuses on summative assessment with rich feedback

### 8.4 Parallel LLM Inference

**Distributed Inference**:
- **vLLM** (Kwon et al., 2023): Efficient LLM serving
- **Ray** (Moritz et al., 2018): Distributed computing framework

**Our Approach**: Task-level parallelism (different models, different tasks)

---

## 9. Implementation Details

### 9.1 Technology Stack

**Backend**:
- Python 3.9+
- Streamlit (web interface)
- SQLite (database)
- nbformat (notebook parsing)

**AI Frameworks**:
- Ollama (model serving)
- MLX (Apple Silicon optimization)
- Custom distributed client

**Validation**:
- pandas (data analysis)
- numpy (numerical comparison)
- Custom validators

### 9.2 System Requirements

**Minimum**:
- CPU: 8-core processor
- RAM: 32GB
- Storage: 100GB SSD
- OS: macOS, Linux, Windows

**Recommended**:
- CPU: Apple M2 Ultra or equivalent
- RAM: 64GB+
- Storage: 500GB NVMe SSD
- GPU: Optional (NVIDIA RTX 3090 or better)

### 9.3 Deployment Options

**Single Machine**:
- Ollama + local models
- Suitable for: <50 students
- Cost: $2,000-$4,000

**Multi-Machine (Distributed)**:
- Multiple Mac Studios networked
- Suitable for: 100-500 students
- Cost: $12,000-$18,000

**Cloud (Future)**:
- AWS/Azure GPU instances
- Suitable for: Any scale
- Cost: Pay-per-use

