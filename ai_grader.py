import streamlit as st
import pandas as pd
import sqlite3
import nbformat
import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
import pickle
import os
from datetime import datetime
import subprocess
import tempfile
import sys
import requests
import time
import logging
from typing import Dict, Any, Optional

# Import two-model grading system
try:
    from two_model_grader import TwoModelGrader
    TWO_MODEL_AVAILABLE = True
except ImportError:
    TWO_MODEL_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)

def filter_ai_feedback_for_storage(feedback_data: Any) -> Any:
    """
    Filter AI feedback to remove internal monologue before storing in database.
    This ensures clean content is stored at the source.
    """
    if not feedback_data:
        return feedback_data
    
    # Handle different feedback formats
    if isinstance(feedback_data, str):
        try:
            # Try to parse as JSON first
            parsed_data = json.loads(feedback_data)
            return filter_ai_feedback_for_storage(parsed_data)
        except json.JSONDecodeError:
            # If it's just a string, apply basic filtering
            return _filter_text_content(feedback_data)
    
    elif isinstance(feedback_data, dict):
        # Filter dictionary content
        filtered_dict = {}
        
        for key, value in feedback_data.items():
            if key == 'comprehensive_feedback':
                # Apply comprehensive feedback filtering
                filtered_dict[key] = _filter_comprehensive_feedback(value)
            elif key == 'detailed_feedback':
                # Apply detailed feedback filtering
                filtered_dict[key] = _filter_detailed_feedback(value)
            elif key == 'instructor_comments':
                # Apply instructor comments filtering
                filtered_dict[key] = _filter_instructor_comments(value)
            elif isinstance(value, (str, dict, list)):
                # Recursively filter nested content
                filtered_dict[key] = filter_ai_feedback_for_storage(value)
            else:
                # Keep non-text content as is
                filtered_dict[key] = value
        
        return filtered_dict
    
    elif isinstance(feedback_data, list):
        # Filter list content
        return [filter_ai_feedback_for_storage(item) for item in feedback_data]
    
    else:
        # Return non-text content as is
        return feedback_data

def _filter_comprehensive_feedback(comp_feedback: Any) -> Any:
    """Filter comprehensive feedback section"""
    if isinstance(comp_feedback, str):
        # Extract JSON from string if possible
        json_data = _extract_json_from_response(comp_feedback)
        if json_data:
            return _filter_comprehensive_feedback(json_data)
        else:
            return _filter_text_content(comp_feedback)
    
    elif isinstance(comp_feedback, dict):
        filtered = {}
        
        # Filter instructor comments
        if 'instructor_comments' in comp_feedback:
            filtered['instructor_comments'] = _filter_instructor_comments(comp_feedback['instructor_comments'])
        
        # Filter detailed feedback
        if 'detailed_feedback' in comp_feedback:
            filtered['detailed_feedback'] = _filter_detailed_feedback(comp_feedback['detailed_feedback'])
        
        # Keep other fields as is (scores, etc.)
        for key, value in comp_feedback.items():
            if key not in ['instructor_comments', 'detailed_feedback']:
                filtered[key] = value
        
        return filtered
    
    return comp_feedback

def _filter_detailed_feedback(detailed_feedback: Any) -> Any:
    """Filter detailed feedback sections"""
    if not isinstance(detailed_feedback, dict):
        return detailed_feedback
    
    filtered = {}
    
    for section_name, section_content in detailed_feedback.items():
        if isinstance(section_content, list):
            # Filter each item in the list
            filtered_items = []
            for item in section_content:
                if isinstance(item, str) and len(item) > 20:
                    # Check if this looks like instructor feedback vs internal reasoning
                    # Expanded patterns to catch more internal AI dialog
                    if not any(pattern in item.lower() for pattern in [
                        "we need", "let's", "the student", "they have", "first,", "now", 
                        "good.", "thus", "maybe", "overall score:", "business understanding:",
                        "communication clarity:", "data interpretation:", "methodology appropriateness:",
                        "reflection quality:", "now produce", "let's craft",
                        "they answered", "they gave", "they completed", "they did", "they also",
                        "they wrote", "they provided", "they used", "they could", "they should",
                        "part 1:", "part 2:", "part 3:", "part 4:", "part 5:",
                        "q1", "q2", "q3", "q4", "q5",
                        "missing value strategy", "outlier interpretation", "data quality impact",
                        "ethical considerations", "thorough answers"
                    ]):
                        clean_item = _filter_text_content(item)
                        if clean_item and len(clean_item) > 15:
                            filtered_items.append(clean_item)
            
            # If we have clean items, use them; otherwise provide appropriate fallback
            if filtered_items:
                filtered[section_name] = filtered_items[:3]  # Limit to 3 items
            else:
                filtered[section_name] = [_get_fallback_for_section(section_name)]
        else:
            filtered[section_name] = section_content
    
    return filtered

def _filter_instructor_comments(comments: str) -> str:
    """Filter instructor comments to remove AI artifacts - NO FALLBACK"""
    if not isinstance(comments, str):
        return str(comments) if comments else ""
    
    # Remove internal reasoning patterns - EXPANDED LIST
    patterns_to_remove = [
        r"We need to.*?\.",
        r"Let's.*?\.",
        r"First,.*?\.",
        r"Now.*?\.",
        r"The student provided.*?\.",
        r"They have.*?\.",
        r"<\|.*?\|>",
        r"\{.*?\}",
        r"JSON.*?",
        r"Overall score:.*?\.",
        r"Business understanding:.*?\.",
        r"Communication clarity:.*?\.",
        r"Data interpretation:.*?\.",
        r"Methodology appropriateness:.*?\.",
        r"Reflection quality:.*?\.",
        r"Now produce.*?\.",
        r"Let's craft.*?\.",
        r"<think>.*?</think>",
        r"<reasoning>.*?</reasoning>",
        r"\[thinking\].*?\[/thinking\]",
        r"\[internal\].*?\[/internal\]",
    ]
    
    clean_comments = comments
    for pattern in patterns_to_remove:
        clean_comments = re.sub(pattern, '', clean_comments, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up whitespace
    clean_comments = re.sub(r'\s+', ' ', clean_comments).strip()
    
    # If too much was removed, return empty - NO FALLBACK
    if len(clean_comments) < 30:
        logger.warning(f"Instructor comments too short after filtering ({len(clean_comments)} chars) - AI model needs to generate more verbose, personalized feedback")
        return ""
    
    return clean_comments

def _filter_text_content(text: str) -> str:
    """Apply basic text filtering to remove internal AI patterns"""
    if not isinstance(text, str):
        return str(text) if text else ""
    
    # Remove internal AI patterns - EXPANDED LIST
    forbidden_patterns = [
        "we need to", "let's", "first, check", "now evaluate", "now assign",
        "now produce", "let's craft", "the student provided", "they have code",
        "did they complete", "the assignment required", "good.", "thus they",
        "reflection quality:", "business understanding:", "communication clarity:",
        "data interpretation:", "methodology appropriateness:", "overall score:",
        "maybe", "now produce json", "<|end|>", "<|start|>", "assistant", "channel",
        "they answered", "they gave", "they completed", "they did", "they also",
        "they wrote", "they provided", "they used", "they could", "they should",
        "part 1:", "part 2:", "part 3:", "part 4:", "part 5:",
        "q1 (", "q2 (", "q3 (", "q4 (", "q5 (",
        "missing value strategy", "outlier interpretation", "data quality impact",
        "ethical considerations", "thorough answers", "gave thorough"
    ]
    
    lines = text.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip lines with forbidden patterns
        if any(pattern in line.lower() for pattern in forbidden_patterns):
            continue
        
        # Skip very short lines
        if len(line) < 15:
            continue
        
        # Skip lines that start with internal reasoning markers
        if line.startswith(("We ", "Let's ", "First ", "Now ", "The student ", "They ", "Part ")):
            continue
        
        # Skip lines that contain question references
        if re.search(r'\bQ\d+\b', line):
            continue
        
        clean_lines.append(line)
    
    return ' '.join(clean_lines[:3])  # Limit to first 3 clean lines

def _extract_json_from_response(ai_response: str) -> Optional[Dict[str, Any]]:
    """Extract JSON content from AI response, ignoring internal monologue"""
    if not ai_response:
        return None
    
    try:
        # Pattern to find JSON objects
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        json_matches = re.findall(json_pattern, ai_response, re.DOTALL)
        
        if not json_matches:
            return None
        
        # Try to parse each JSON match, starting from the last one
        for json_text in reversed(json_matches):
            try:
                clean_json = json_text.strip()
                if clean_json.endswith('```'):
                    clean_json = clean_json[:-3].strip()
                
                parsed_json = json.loads(clean_json)
                
                # Validate it has expected structure
                if isinstance(parsed_json, dict) and ('detailed_feedback' in parsed_json or 'instructor_comments' in parsed_json):
                    return parsed_json
                    
            except json.JSONDecodeError:
                continue
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting JSON from AI response: {e}")
        return None

def _get_fallback_for_section(section_name: str) -> str:
    """Get appropriate fallback content for each section - SHOULD NOT BE USED"""
    # Fallbacks should not be used - AI must generate personalized feedback
    logger.warning(f"Fallback requested for section '{section_name}' - AI model needs to generate more verbose, personalized feedback")
    return f"[Feedback not available for {section_name} - please regenerate with more verbose AI model]"

class LocalAIClient:
    def __init__(self, model_name=None, base_url="http://localhost:11434"):
        """Initialize connection to local AI model (Ollama)"""
        # Import model configuration
        try:
            from model_config import PRIMARY_GRADING_MODEL, get_model_config
            if model_name is None:
                model_name = PRIMARY_GRADING_MODEL
            self.model_config = get_model_config(model_name)
        except ImportError:
            # Fallback if config file doesn't exist
            if model_name is None:
                model_name = "gemma3:27b"  # Default to gemma for cleaner feedback
            self.model_config = {"temperature": 0.3, "max_tokens": 3000}
        
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.last_response_time = None
        
        # Check model status using session state and live check
        session_key = f"model_loaded_{self.model_name}"
        if hasattr(st, 'session_state') and session_key in st.session_state:
            # Use cached status but verify occasionally
            self.model_loaded_in_memory = st.session_state[session_key]
            # Refresh status every 10th check
            if not hasattr(st.session_state, 'model_check_count'):
                st.session_state.model_check_count = 0
            st.session_state.model_check_count += 1
            if st.session_state.model_check_count % 10 == 0:
                self.model_loaded_in_memory = self._check_model_memory_status()
                st.session_state[session_key] = self.model_loaded_in_memory
        else:
            # First check or no session state available
            self.model_loaded_in_memory = self._check_model_memory_status()
            if hasattr(st, 'session_state'):
                st.session_state[session_key] = self.model_loaded_in_memory
    
    def _check_model_memory_status(self):
        """Check if the model is currently loaded in Ollama's memory"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/ps", timeout=5)
            if response.status_code == 200:
                running_models = response.json().get("models", [])
                for model in running_models:
                    if model.get("name") == self.model_name:
                        return True
            return False
        except:
            return False
    
    def keep_model_loaded(self):
        """Send a keep-alive request to prevent model unloading"""
        try:
            import requests
            # Send a minimal request to keep model in memory
            payload = {
                "model": self.model_name,
                "prompt": "ready",
                "stream": False,
                "options": {
                    "num_predict": 1,  # Minimal response
                    "temperature": 0.1
                }
            }
            requests.post(self.api_url, json=payload, timeout=60)
        except:
            pass
    
    def preload_model(self):
        """Aggressively preload the model into memory"""
        try:
            import requests
            # Force model loading with a simple request
            payload = {
                "model": self.model_name,
                "prompt": "System ready for grading",
                "stream": False,
                "options": {
                    "num_predict": 5,
                    "temperature": 0.1
                }
            }
            response = requests.post(self.api_url, json=payload, timeout=120)
            if response.status_code == 200:
                self.model_loaded_in_memory = True
                return True
        except:
            pass
        return False
        
        # Auto-detect best available model
        self.available_models = self.get_available_models()
        if model_name not in [m.get('name', '') for m in self.available_models]:
            self.model_name = self.select_best_model()
    
    def get_available_models(self):
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get("models", [])
        except:
            pass
        return []
    
    def select_best_model(self):
        """Select the best available model for grading"""
        model_names = [m.get('name', '') for m in self.available_models]
        
        # Preference order for grading tasks
        preferred_models = [
            "gpt-oss:120b",              # Primary choice - very powerful
            "deepseek-r1:70b",           # Excellent reasoning
            "mistral-small3.1:24b-instruct-2503-q8_0",  # Good balance
            "gemma3:27b",                # Good performance
            "qwen3-coder:30b-a3b-fp16",  # Good for code
            "llama4:latest",             # General purpose
            "gemma3:12b-it-fp16"         # Smaller but capable
        ]
        
        for model in preferred_models:
            if model in model_names:
                return model
        
        # Fallback to first available model
        return model_names[0] if model_names else "deepseek-r1:70b"
        
    def is_available(self):
        """Check if the local AI model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                # Check if our preferred model is actually available
                model_names = [m.get('name', '') for m in models]
                return len(models) > 0 and (self.model_name in model_names or len(model_names) > 0)
            return False
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.Timeout:
            return False
        except Exception:
            return False
    
    def check_model_memory_status(self):
        """Check if model is loaded in memory by checking running processes"""
        try:
            response = requests.get(f"{self.base_url}/api/ps", timeout=5)
            if response.status_code == 200:
                running_models = response.json().get("models", [])
                for model in running_models:
                    if model.get("name") == self.model_name:
                        self.model_loaded_in_memory = True
                        return True
            self.model_loaded_in_memory = False
            return False
        except:
            return False
    
    def warm_up_model(self, progress_callback=None):
        """Warm up the model by sending a small prompt to load it into memory"""
        if progress_callback:
            progress_callback("🔥 Loading model into memory...")
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": "Hello",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 5
                }
            }
            
            start_time = time.time()
            response = requests.post(self.api_url, json=payload, timeout=180)
            end_time = time.time()
            
            if response.status_code == 200:
                self.model_loaded_in_memory = True
                self.last_response_time = end_time - start_time
                if progress_callback:
                    progress_callback(f"✅ Model loaded! First response took {self.last_response_time:.1f}s")
                return True, f"Model warmed up in {self.last_response_time:.1f} seconds"
            else:
                return False, f"Error {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            if progress_callback:
                progress_callback("⏰ Model loading timed out, but may still be loading...")
            return False, "Timeout during warmup (model may still be loading)"
        except Exception as e:
            return False, str(e)
    
    def generate_response(self, prompt, max_tokens=None, show_progress=False):
        """Generate response from local AI model"""
        start_time = time.time()
        
        # Use model-specific max_tokens if not specified
        if max_tokens is None:
            max_tokens = self.model_config.get('max_tokens', 3000)
        
        # Check if this is likely the first request (model not in memory)
        if not self.model_loaded_in_memory and show_progress:
            st.info(f"🔄 Loading {self.model_name} from external drive (1.5GB/s - should take ~45-60 seconds)...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # More realistic progress simulation for fast external drive
            for i in range(20):
                progress_bar.progress((i + 1) / 20)
                elapsed = (i + 1) * 3  # 3 seconds per step = 60 seconds total
                status_text.text(f"Loading model... {elapsed}s elapsed")
                time.sleep(0.1)  # Much faster updates
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.model_config.get('temperature', 0.3),
                    "num_predict": max_tokens  # Ollama uses num_predict instead of max_tokens
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=300)  # 5 minutes for very large models
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                # Update memory status based on response time (optimized for fast external drive)
                if response_time < 45:  # Fast response indicates model was in memory
                    self.model_loaded_in_memory = True
                elif response_time > 45:  # Response indicates loading from fast external drive
                    self.model_loaded_in_memory = True  # Now it's loaded
                
                # Update session state
                if hasattr(st, 'session_state'):
                    session_key = f"model_loaded_{self.model_name}"
                    st.session_state[session_key] = self.model_loaded_in_memory
                
                self.last_response_time = response_time
                
                if show_progress:
                    if hasattr(st, 'progress_bar'):
                        st.progress_bar.progress(1.0)
                    if hasattr(st, 'status_text'):
                        st.status_text.text(f"✅ Response received in {response_time:.1f}s")
                
                return response.json().get("response", "")
            elif response.status_code == 404:
                st.error(f"Model '{self.model_name}' not found. Check if external drive is mounted and Ollama can access models.")
                return None
            else:
                st.error(f"AI model returned error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            st.error("AI model response timed out. Large models may take longer to respond.")
            return None
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to Ollama. Make sure Ollama is running and external drive is accessible.")
            return None
        except Exception as e:
            st.error(f"Error communicating with local AI: {str(e)}")
            return None

class AIGrader:
    def __init__(self, grader):
        self.grader = grader
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        
        # Use unified model interface
        try:
            from unified_model_interface import get_unified_ai_client
            self.local_ai = get_unified_ai_client()
            self.use_local_ai = self.local_ai is not None
            self.ai_backend = "Unified"
        except Exception:
            # Fallback to Ollama for backward compatibility
            # Use gemma3:27b by default for cleaner, more verbose feedback
            preferred_model = os.environ.get('HOMEWORK_GRADER_MODEL', 'gemma3:27b')
            self.local_ai = LocalAIClient(model_name=preferred_model)
            self.use_local_ai = self.local_ai.is_available()
            self.ai_backend = "Ollama"
        
    def extract_notebook_features(self, notebook_path, solution_path=None):
        """Extract features from a notebook for AI grading"""
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            features = {
                'total_cells': len(nb.cells),
                'code_cells': 0,
                'markdown_cells': 0,
                'code_length': 0,
                'has_outputs': 0,
                'error_count': 0,
                'comment_ratio': 0,
                'function_count': 0,
                'variable_count': 0,
                'library_imports': 0,
                'plot_count': 0,
                'text_content': ""
            }
            
            all_code = ""
            all_text = ""
            
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    features['code_cells'] += 1
                    code = cell.source
                    all_code += code + "\n"
                    features['code_length'] += len(code)
                    
                    # Check for outputs
                    if cell.get('outputs', []):
                        features['has_outputs'] += 1
                        
                        # Check for errors
                        for output in cell.outputs:
                            if output.get('output_type') == 'error':
                                features['error_count'] += 1
                    
                    # Analyze code content
                    features['comment_ratio'] += len(re.findall(r'#.*', code)) / max(len(code.split('\n')), 1)
                    features['function_count'] += len(re.findall(r'def\s+\w+', code))
                    features['variable_count'] += len(re.findall(r'\w+\s*<-\s*', code))  # R assignment
                    features['library_imports'] += len(re.findall(r'library\(|import\s+', code))
                    features['plot_count'] += len(re.findall(r'plot\(|ggplot|matplotlib', code))
                    
                elif cell.cell_type == 'markdown':
                    features['markdown_cells'] += 1
                    all_text += cell.source + "\n"
            
            features['text_content'] = all_text + all_code
            features['code_to_markdown_ratio'] = features['code_cells'] / max(features['markdown_cells'], 1)
            
            # Compare with solution if available
            if solution_path and os.path.exists(solution_path):
                similarity_score = self.compare_with_solution(notebook_path, solution_path)
                features['solution_similarity'] = similarity_score
            
            return features
            
        except Exception as e:
            st.error(f"Error extracting features from {notebook_path}: {str(e)}")
            return None
    
    def compare_with_solution(self, student_notebook, solution_notebook):
        """Compare student notebook with solution using text similarity"""
        try:
            # Read both notebooks
            with open(student_notebook, 'r', encoding='utf-8') as f:
                student_nb = nbformat.read(f, as_version=4)
            
            with open(solution_notebook, 'r', encoding='utf-8') as f:
                solution_nb = nbformat.read(f, as_version=4)
            
            # Extract code from both
            student_code = ""
            solution_code = ""
            
            for cell in student_nb.cells:
                if cell.cell_type == 'code':
                    student_code += cell.source + "\n"
            
            for cell in solution_nb.cells:
                if cell.cell_type == 'code':
                    solution_code += cell.source + "\n"
            
            # Calculate similarity
            if student_code and solution_code:
                vectorizer = TfidfVectorizer()
                tfidf_matrix = vectorizer.fit_transform([student_code, solution_code])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return similarity
            
            return 0.0
            
        except Exception as e:
            return 0.0
    
    def execute_notebook(self, notebook_path):
        """Execute notebook and capture results"""
        try:
            # Create a temporary copy
            temp_path = notebook_path.replace('.ipynb', '_temp.ipynb')
            
            # Execute using nbconvert
            cmd = [
                sys.executable, '-m', 'jupyter', 'nbconvert',
                '--to', 'notebook',
                '--execute',
                '--output', temp_path,
                notebook_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Read executed notebook
                with open(temp_path, 'r', encoding='utf-8') as f:
                    executed_nb = nbformat.read(f, as_version=4)
                
                # Clean up
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                return executed_nb, True, ""
            else:
                return None, False, result.stderr
                
        except subprocess.TimeoutExpired:
            return None, False, "Execution timeout"
        except Exception as e:
            return None, False, str(e)
    
    def grade_notebook_with_local_ai(self, notebook_path, assignment_id, rubric=None):
        """Grade notebook using detailed analysis with optional AI enhancement"""
        try:
            # First, try detailed rule-based analysis for specific feedback
            from detailed_analyzer import DetailedHomeworkAnalyzer, format_detailed_feedback
            
            # Load assignment rubric from database
            conn = sqlite3.connect(self.grader.db_path)
            assignment_info = pd.read_sql_query("""
                SELECT name, total_points, rubric FROM assignments WHERE id = ?
            """, conn, params=(assignment_id,))
            conn.close()
            
            rubric_data = {}
            if not assignment_info.empty and assignment_info.iloc[0]['rubric']:
                try:
                    rubric_data = json.loads(assignment_info.iloc[0]['rubric'])
                except:
                    pass
            
            # Force Assignment 2 detection if assignment name contains data cleaning keywords
            assignment_name = assignment_info.iloc[0]['name'].lower() if not assignment_info.empty else ''
            if any(keyword in assignment_name for keyword in ['data', 'cleaning', '2']):
                # Ensure assignment_id is passed as string for better detection
                analyzer = DetailedHomeworkAnalyzer(assignment_id=f"assignment_2_{assignment_id}", rubric=rubric_data)
            else:
                analyzer = DetailedHomeworkAnalyzer(assignment_id=assignment_id, rubric=rubric_data)
            detailed_analysis = analyzer.analyze_notebook(notebook_path)
            
            # Extract and create student record if needed
            try:
                student_info = detailed_analysis.get('student_info', {})
                if student_info and student_info.get('name') != 'Unknown':
                    self._ensure_student_exists(student_info)
            except Exception as e:
                # Don't fail the entire grading if student creation fails
                print(f"⚠️ Student creation failed: {e}")
            
            # If AI is available, enhance with AI feedback
            if self.use_local_ai:
                try:
                    ai_result = self._get_ai_enhancement(notebook_path, assignment_id, detailed_analysis)
                    if ai_result:
                        # Combine detailed analysis with AI insights
                        combined_feedback = format_detailed_feedback(detailed_analysis)
                        combined_feedback.extend(["", "🤖 **AI ENHANCEMENT:**"])
                        combined_feedback.extend(ai_result.get('feedback', []))
                        
                        # Extract features for training data
                        features = {
                            'total_score': detailed_analysis['total_score'],
                            'element_scores': detailed_analysis.get('element_scores', {}),
                            'missing_elements_count': len(detailed_analysis.get('missing_elements', [])),
                            'code_issues_count': len(detailed_analysis.get('code_issues', [])),
                            'grading_method': 'detailed_with_ai_enhancement',
                            'ai_enhancement_used': True
                        }
                        
                        return {
                            'score': detailed_analysis['total_score'],
                            'feedback': combined_feedback,
                            'detailed_analysis': detailed_analysis,
                            'ai_enhancement': ai_result,
                            'features': features,
                            'executed_successfully': True,
                            'grading_method': 'detailed_with_ai_enhancement'
                        }
                except Exception as e:
                    st.warning(f"AI enhancement failed: {str(e)}, using detailed analysis only")
            
            # Extract features for training data
            features = {
                'total_score': detailed_analysis['total_score'],
                'element_scores': detailed_analysis.get('element_scores', {}),
                'missing_elements_count': len(detailed_analysis.get('missing_elements', [])),
                'code_issues_count': len(detailed_analysis.get('code_issues', [])),
                'grading_method': 'detailed_analysis'
            }
            
            # Return detailed analysis only
            return {
                'score': detailed_analysis['total_score'],
                'feedback': format_detailed_feedback(detailed_analysis),
                'detailed_analysis': detailed_analysis,
                'features': features,
                'executed_successfully': True,
                'grading_method': 'detailed_analysis'
            }
            
        except Exception as e:
            st.error(f"Error in detailed grading: {str(e)}")
            return self.grade_notebook_fallback(notebook_path, assignment_id)
    
    def _get_ai_enhancement(self, notebook_path, assignment_id, detailed_analysis):
        """Get AI enhancement for detailed analysis"""
        try:
            # Read notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            # Extract code and markdown content
            code_content = ""
            markdown_content = ""
            
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    code_content += cell.source + "\n\n"
                elif cell.cell_type == 'markdown':
                    markdown_content += cell.source + "\n\n"
            
            # Get assignment details for context
            conn = sqlite3.connect(self.grader.db_path)
            assignment_info = pd.read_sql_query("""
                SELECT name, description, rubric, solution_notebook
                FROM assignments WHERE id = ?
            """, conn, params=(assignment_id,))
            conn.close()
            
            if assignment_info.empty:
                return None
            
            assignment = assignment_info.iloc[0]
            
            # Safely parse rubric JSON
            rubric_data = {}
            if assignment['rubric']:
                try:
                    rubric_data = json.loads(assignment['rubric'])
                    if not isinstance(rubric_data, dict):
                        rubric_data = {}
                except (json.JSONDecodeError, TypeError):
                    rubric_data = {}
            
            # Read solution notebook if available
            solution_content = ""
            if assignment['solution_notebook'] and os.path.exists(assignment['solution_notebook']):
                try:
                    with open(assignment['solution_notebook'], 'r', encoding='utf-8') as f:
                        solution_nb = nbformat.read(f, as_version=4)
                    
                    for cell in solution_nb.cells:
                        if cell.cell_type == 'code':
                            solution_content += cell.source + "\n\n"
                except:
                    pass
            
            # Create grading prompt
            prompt = self.create_grading_prompt(
                assignment['name'],
                assignment['description'],
                rubric_data,
                code_content,
                markdown_content,
                solution_content
            )
            
            # Get AI response (show progress if model not in memory)
            show_progress = not self.local_ai.model_loaded_in_memory
            ai_response = self.local_ai.generate_response(prompt, show_progress=show_progress)
            
            if ai_response:
                return self.parse_ai_grading_response(ai_response, rubric_data)
            else:
                # Fall back to rule-based grading
                return self.grade_notebook_fallback(notebook_path, assignment_id)
                
        except Exception as e:
            st.error(f"Error in AI grading: {str(e)}")
            import traceback
            st.error(f"Full error details: {traceback.format_exc()}")
            return self.grade_notebook_fallback(notebook_path, assignment_id)
    
    def create_grading_prompt(self, assignment_name, description, rubric, student_code, student_markdown, solution_code=""):
        """Create a detailed prompt for the AI grader"""
        
        rubric_text = ""
        total_points = 0
        
        if rubric:
            rubric_text = "DETAILED GRADING RUBRIC:\n"
            
            # Extract assignment info
            if 'assignment_info' in rubric:
                info = rubric['assignment_info']
                total_points = info.get('total_points', 37.5)
                rubric_text += f"Assignment: {info.get('title', 'Unknown Assignment')}\n"
                rubric_text += f"Total Points: {total_points}\n"
                rubric_text += f"Learning Objectives: {', '.join(info.get('learning_objectives', []))}\n\n"
            
            # Extract rubric elements with detailed criteria
            if 'rubric_elements' in rubric:
                rubric_text += "RUBRIC ELEMENTS:\n"
                for element_name, element_data in rubric['rubric_elements'].items():
                    max_points = element_data.get('max_points', 0)
                    description = element_data.get('description', '')
                    category = element_data.get('category', 'unknown')
                    
                    rubric_text += f"\n{element_name.upper()} ({max_points} points - {category}):\n"
                    rubric_text += f"  Description: {description}\n"
                    
                    # Add criteria details
                    if 'criteria' in element_data:
                        rubric_text += "  Grading Criteria:\n"
                        for level, criteria in element_data['criteria'].items():
                            points_range = criteria.get('points', 'N/A')
                            criteria_desc = criteria.get('description', '')
                            rubric_text += f"    {level.title()} ({points_range} pts): {criteria_desc}\n"
                    
                    # Add automated checks if available
                    if 'automated_checks' in element_data:
                        rubric_text += "  Key Requirements:\n"
                        for check in element_data['automated_checks']:
                            rubric_text += f"    - {check}\n"
                
                rubric_text += "\n"
            
            # Fallback for simple rubric format
            if not rubric_text or rubric_text == "DETAILED GRADING RUBRIC:\n":
                rubric_text = "GRADING RUBRIC:\n"
                for criterion, details in rubric.items():
                    if isinstance(details, dict):
                        points = details.get('points', 0)
                        desc = details.get('description', '')
                        total_points += points
                        rubric_text += f"- {criterion}: {points} points - {desc}\n"
                    else:
                        rubric_text += f"- {criterion}: {details}\n"
        
        solution_section = ""
        if solution_code:
            solution_section = f"""
REFERENCE SOLUTION (Use as guidance for expected approach and quality):
{solution_code}

IMPORTANT: The reference solution shows the expected approach and quality level. Students may use different valid methods to achieve the same results. Evaluate based on correctness and understanding, not strict adherence to the reference implementation.
"""
        
        prompt = f"""You are an expert data science and programming instructor with extensive experience grading student assignments. You understand both technical execution and conceptual understanding. Provide a thorough, fair, and pedagogically sound evaluation.

ASSIGNMENT: {assignment_name}
DESCRIPTION: {description}

{rubric_text}
TOTAL POINTS: {total_points}

{solution_section}

STUDENT SUBMISSION:

CODE:
{student_code}

EXPLANATORY TEXT:
{student_markdown}

DETAILED GRADING CRITERIA:

1. TECHNICAL EXECUTION (40% weight):
   - Code runs without errors and produces correct outputs
   - Uses appropriate R functions (tidyverse, readr, ggplot2)
   - Implements required data cleaning techniques correctly
   - Handles missing values and outliers appropriately
   - Follows R coding best practices

2. CONCEPTUAL UNDERSTANDING (30% weight):
   - Demonstrates understanding of data cleaning concepts
   - Makes informed decisions about missing value treatment
   - Correctly applies statistical methods (IQR for outliers)
   - Shows reasoning for data quality choices
   - Connects cleaning decisions to business context

3. CODE QUALITY & DOCUMENTATION (20% weight):
   - Clear, readable R code structure
   - Meaningful variable names and comments
   - Proper use of R syntax and functions
   - Good organization of analysis workflow
   - Evidence of testing and verification

4. COMMUNICATION & ANALYSIS (10% weight):
   - Clear explanations of data cleaning methodology
   - Thoughtful interpretation of data quality issues
   - Comprehensive answers to reflection questions
   - Professional presentation and documentation

ASSIGNMENT-SPECIFIC EVALUATION FOCUS:
For Data Cleaning assignments, pay special attention to:
- Data import and initial assessment quality
- Missing value identification and treatment strategies
- Outlier detection using statistical methods (IQR)
- Comparison of different cleaning approaches
- Business context and ethical considerations
- Quality of final dataset selection and justification

GRADING GUIDELINES:
- ACCURACY FIRST: Correct results are paramount, but give partial credit for logical approaches
- RECOGNIZE COMPLETED WORK: Carefully examine student code - don't penalize for work that was actually completed
- MULTIPLE APPROACHES: Accept different valid R methods (base R vs tidyverse, different imputation strategies, etc.)
- PROCESS OVER PERFECTION: Reward clear thinking and methodology even if execution has minor issues
- LEARNING EVIDENCE: Look for signs the student understands data cleaning concepts and can justify decisions
- REAL-WORLD RELEVANCE: Value practical insights about data quality and business implications
- CREATIVE EXPLORATION: Reward students who go beyond requirements or test alternative approaches
- DETAILED ANALYSIS: Provide specific feedback about what worked well and what needs improvement
- ASSIGNMENT-SPECIFIC: Focus on data cleaning skills, not generic programming feedback

SPECIFIC EVALUATION AREAS:
- Data Import/Loading: Successful CSV import, proper data structure recognition
- Initial Data Assessment: Use of head(), str(), summary(), identification of data quality issues
- Missing Value Analysis: Calculation of total_missing, missing_per_column, incomplete_rows identification
- Missing Value Treatment: Implementation of removal (na.omit) and imputation strategies (mode, median)
- Outlier Detection: Correct IQR method implementation (Q1, Q3, thresholds, outlier identification)
- Outlier Treatment: Implementation of removal and/or capping strategies
- Data Visualization: Creation of boxplots or other plots to visualize outliers
- Comparison Analysis: Systematic comparison of different cleaning approaches
- Final Dataset Selection: Justified choice of final cleaned dataset with reasoning
- Reflection Questions: Thoughtful answers about business implications and ethical considerations
- Code Quality: Proper R syntax, meaningful variable names, appropriate comments
- Documentation: Clear explanations of cleaning decisions and methodology

Please evaluate this submission and provide:

1. OVERALL SCORE: A numerical score out of {total_points} points (be precise, use decimals if needed)
2. DETAILED BREAKDOWN: Score for each rubric criterion with specific justification
3. TECHNICAL FEEDBACK: Specific comments on code execution, logic, and methodology
4. CONCEPTUAL FEEDBACK: Assessment of understanding and analytical thinking
5. STRENGTHS: What the student demonstrated well (be specific)
6. IMPROVEMENT AREAS: Concrete suggestions for enhancement
7. NEXT STEPS: Recommendations for continued learning

FORMAT AS JSON:
{{
    "overall_score": <precise_number>,
    "rubric_breakdown": {{
        "criterion_name": {{"score": <number>, "max_points": <number>, "feedback": "detailed_explanation", "strengths": ["specific_strength1"], "improvements": ["specific_improvement1"]}}
    }},
    "technical_assessment": {{
        "code_execution": "assessment of whether code runs and produces correct results",
        "methodology": "evaluation of approach and logic",
        "efficiency": "comments on code efficiency and best practices",
        "error_handling": "how well student dealt with issues"
    }},
    "conceptual_assessment": {{
        "understanding": "evidence of conceptual grasp",
        "analysis_quality": "depth and appropriateness of analysis",
        "business_context": "connection to real-world applications",
        "critical_thinking": "evidence of analytical reasoning"
    }},
    "communication_assessment": {{
        "code_documentation": "quality of comments and code organization",
        "explanatory_text": "clarity and completeness of written explanations",
        "presentation": "overall professional presentation"
    }},
    "overall_strengths": ["strength1", "strength2", "strength3"],
    "priority_improvements": ["improvement1", "improvement2", "improvement3"],
    "learning_recommendations": ["next_step1", "next_step2"],
    "grade_justification": "comprehensive explanation of the overall score"
}}

SCORING PHILOSOPHY: Be generous with partial credit for demonstrated understanding, but maintain high standards for technical accuracy. A student who shows clear thinking but makes minor technical errors should score higher than one who gets lucky with correct output but shows no understanding. Focus on learning evidence over perfect execution.

FEEDBACK REQUIREMENTS:
- Provide DETAILED, SPECIFIC feedback for each rubric element
- Acknowledge ALL completed work, even if implementation differs from expected approach
- Give concrete examples from the student's code when praising or critiquing
- Offer specific suggestions for improvement with actionable next steps
- Maintain encouraging tone while being constructively critical
- Be MORE VERBOSE than typical - students need detailed guidance for learning"""
        
        return prompt
    
    def parse_ai_grading_response(self, ai_response, rubric):
        """Parse the AI's grading response"""
        try:
            # Try to extract JSON from the response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                grading_data = json.loads(json_str)
                
                # Format feedback
                feedback = []
                
                # Add general feedback
                if grading_data.get('general_feedback'):
                    feedback.append(f"📝 {grading_data['general_feedback']}")
                
                # Add strengths
                if grading_data.get('strengths'):
                    feedback.append("✅ Strengths:")
                    for strength in grading_data['strengths']:
                        feedback.append(f"  • {strength}")
                
                # Add improvements
                if grading_data.get('improvements'):
                    feedback.append("🔧 Areas for Improvement:")
                    for improvement in grading_data['improvements']:
                        feedback.append(f"  • {improvement}")
                
                # Add rubric breakdown
                if grading_data.get('rubric_breakdown'):
                    feedback.append("📊 Detailed Breakdown:")
                    rubric_breakdown = grading_data['rubric_breakdown']
                    if isinstance(rubric_breakdown, dict):
                        for criterion, details in rubric_breakdown.items():
                            if isinstance(details, dict):
                                score = details.get('score', 0)
                                max_points = details.get('max_points', 0)
                                criterion_feedback = details.get('feedback', '')
                                feedback.append(f"  • {criterion}: {score}/{max_points} - {criterion_feedback}")
                            else:
                                feedback.append(f"  • {criterion}: {details}")
                
                return {
                    'score': grading_data.get('overall_score', 0),
                    'feedback': feedback,
                    'ai_detailed_response': grading_data,
                    'executed_successfully': True  # Assume success if AI could analyze
                }
            
        except json.JSONDecodeError:
            # If JSON parsing fails, extract key information from text
            pass
        
        # Fallback: extract score from text response
        score_match = re.search(r'score[:\s]*(\d+)', ai_response.lower())
        score = int(score_match.group(1)) if score_match else 75
        
        return {
            'score': score,
            'feedback': [f"🤖 AI Analysis: {ai_response[:500]}..."],
            'ai_raw_response': ai_response,
            'executed_successfully': True
        }
    
    def grade_notebook_fallback(self, notebook_path, assignment_id):
        """Fallback rule-based grading when AI is unavailable"""
        features = self.extract_notebook_features(notebook_path)
        if not features:
            return {
                'score': 0,
                'feedback': ["❌ Could not analyze notebook - file may be corrupted or invalid"],
                'executed_successfully': False
            }
        
        # Execute notebook
        executed_nb, success, error_msg = self.execute_notebook(notebook_path)
        
        # Get assignment rubric for context
        conn = sqlite3.connect(self.grader.db_path)
        assignment_info = pd.read_sql_query("""
            SELECT name, total_points, rubric FROM assignments WHERE id = ?
        """, conn, params=(assignment_id,))
        conn.close()
        
        total_possible = 37.5  # Default
        if not assignment_info.empty:
            total_possible = assignment_info.iloc[0]['total_points'] or 37.5
        
        # Base scoring
        score = 0
        feedback = []
        detailed_feedback = []
        
        feedback.append("🤖 **Rule-Based Grading** (AI unavailable)")
        feedback.append("")
        
        # Execution Analysis (40% of grade)
        execution_points = total_possible * 0.4
        if success:
            score += execution_points
            feedback.append("✅ **Code Execution (40%): EXCELLENT**")
            feedback.append("   • All code cells executed without errors")
            feedback.append("   • Outputs generated successfully")
        else:
            execution_penalty = min(execution_points, features['error_count'] * 5)
            earned = max(0, execution_points - execution_penalty)
            score += earned
            feedback.append(f"⚠️ **Code Execution (40%): {earned:.1f}/{execution_points:.1f}**")
            feedback.append(f"   • Execution errors detected: {features['error_count']}")
            if error_msg:
                feedback.append(f"   • Error details: {error_msg[:100]}...")
        
        # Code Quality Analysis (30% of grade)
        quality_points = total_possible * 0.3
        quality_score = 0
        quality_feedback = []
        
        # Comments analysis
        if features['comment_ratio'] > 0.15:
            quality_score += quality_points * 0.4
            quality_feedback.append("   • Excellent use of comments")
        elif features['comment_ratio'] > 0.05:
            quality_score += quality_points * 0.2
            quality_feedback.append("   • Some comments present, could use more")
        else:
            quality_feedback.append("   • Very few comments - add explanations")
        
        # Code structure
        if features['function_count'] > 0:
            quality_score += quality_points * 0.3
            quality_feedback.append("   • Uses functions appropriately")
        
        # Variable usage (R-specific)
        if features['variable_count'] > 2:
            quality_score += quality_points * 0.3
            quality_feedback.append("   • Good variable usage and assignment")
        elif features['variable_count'] > 0:
            quality_score += quality_points * 0.15
            quality_feedback.append("   • Basic variable usage")
        
        score += quality_score
        feedback.append(f"📝 **Code Quality (30%): {quality_score:.1f}/{quality_points:.1f}**")
        feedback.extend(quality_feedback)
        
        # Content Completeness (30% of grade)
        content_points = total_possible * 0.3
        content_score = 0
        content_feedback = []
        
        if features['code_cells'] >= 5:
            content_score += content_points * 0.4
            content_feedback.append(f"   • Good number of code cells ({features['code_cells']})")
        elif features['code_cells'] > 0:
            content_score += content_points * 0.2
            content_feedback.append(f"   • Some code cells present ({features['code_cells']})")
        
        if features['markdown_cells'] >= 3:
            content_score += content_points * 0.3
            content_feedback.append(f"   • Good explanatory text ({features['markdown_cells']} markdown cells)")
        elif features['markdown_cells'] > 0:
            content_score += content_points * 0.15
            content_feedback.append(f"   • Some explanatory text ({features['markdown_cells']} markdown cells)")
        
        if features['has_outputs'] >= 3:
            content_score += content_points * 0.3
            content_feedback.append("   • Shows multiple outputs and results")
        elif features['has_outputs'] > 0:
            content_score += content_points * 0.15
            content_feedback.append("   • Shows some outputs")
        else:
            content_feedback.append("   • No outputs visible - run your code!")
        
        score += content_score
        feedback.append(f"📊 **Content Completeness (30%): {content_score:.1f}/{content_points:.1f}**")
        feedback.extend(content_feedback)
        
        # Summary and suggestions
        feedback.append("")
        feedback.append("💡 **Suggestions for Improvement:**")
        
        if features['comment_ratio'] < 0.1:
            feedback.append("   • Add more comments explaining your code")
        if features['markdown_cells'] < 3:
            feedback.append("   • Include more explanatory text in markdown cells")
        if not success:
            feedback.append("   • Fix code execution errors before submission")
        if features['library_imports'] == 0:
            feedback.append("   • Make sure to load required packages (tidyverse, readxl)")
        
        # Use trained model if available
        if self.is_trained:
            try:
                feature_vector = self.prepare_feature_vector(features)
                ml_score = self.model.predict([feature_vector])[0]
                # Blend AI score with rule-based score
                score = 0.7 * score + 0.3 * ml_score
                feedback.append(f"🧠 **ML Model Adjustment Applied**")
            except:
                pass  # Fall back to rule-based scoring
        
        final_score = min(total_possible, max(0, score))
        
        return {
            'score': final_score,
            'feedback': feedback,
            'features': features,
            'executed_successfully': success,
            'grading_method': 'rule_based_detailed'
        }
    
    def _ensure_student_exists(self, student_info):
        """Create student record if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.grader.db_path)
            cursor = conn.cursor()
            
            student_name = student_info.get('name', 'Unknown')
            student_id = student_info.get('id', student_name.lower().replace(' ', '_'))
            
            # Check if student already exists
            cursor.execute('SELECT id FROM students WHERE name = ? OR student_id = ?', (student_name, student_id))
            existing = cursor.fetchone()
            
            if not existing:
                # Create new student record
                cursor.execute('''
                    INSERT INTO students (student_id, name, email)
                    VALUES (?, ?, ?)
                ''', (student_id, student_name, f"{student_id}@university.edu"))
                
                conn.commit()
                print(f"✅ Created student record: {student_name} ({student_id})")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Could not create student record: {e}")
    
    def grade_notebook(self, notebook_path, assignment_id):
        """Main grading method - always uses detailed analysis, with optional AI enhancement"""
        # Always use detailed analysis (our comprehensive grader)
        return self.grade_notebook_with_local_ai(notebook_path, assignment_id)
    
    def prepare_feature_vector(self, features):
        """Prepare feature vector for ML model"""
        return [
            features.get('total_cells', 0),
            features.get('code_cells', 0),
            features.get('markdown_cells', 0),
            features.get('code_length', 0),
            features.get('has_outputs', 0),
            features.get('error_count', 0),
            features.get('comment_ratio', 0),
            features.get('function_count', 0),
            features.get('variable_count', 0),
            features.get('library_imports', 0),
            features.get('plot_count', 0),
            features.get('code_to_markdown_ratio', 0),
            features.get('solution_similarity', 0)
        ]
    
    def train_model(self, assignment_id=None, language_filter=None):
        """Train the AI model using human grading data"""
        conn = sqlite3.connect(self.grader.db_path)
        
        query = """
            SELECT td.cell_content, td.human_score, td.features, a.name as assignment_name
            FROM ai_training_data td
            JOIN assignments a ON td.assignment_id = a.id
            WHERE td.human_score IS NOT NULL
        """
        
        params = []
        if assignment_id:
            query += " AND td.assignment_id = ?"
            params.append(assignment_id)
        
        if language_filter:
            # Filter by language type in assignment name
            query += " AND (a.name LIKE ? OR a.name LIKE ?)"
            params.extend([f"%{language_filter}%", f"%{language_filter.lower()}%"])
        
        training_data = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if len(training_data) < 10:
            return False, f"Need at least 10 training examples for {language_filter or 'this scope'} (found {len(training_data)})"
        
        try:
            # Prepare features and targets
            X = []
            y = training_data['human_score'].values
            
            for _, row in training_data.iterrows():
                features = json.loads(row['features'])
                feature_vector = self.prepare_feature_vector(features)
                X.append(feature_vector)
            
            X = np.array(X)
            
            # Train model
            self.model.fit(X, y)
            self.is_trained = True
            
            # Save model
            model_path = os.path.join(self.grader.models_dir, f"grader_model_{assignment_id or 'global'}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'vectorizer': self.vectorizer,
                    'is_trained': True
                }, f)
            
            return True, f"Model trained successfully with {len(training_data)} examples"
            
        except Exception as e:
            return False, f"Training failed: {str(e)}"
    
    def load_model(self, assignment_id=None):
        """Load pre-trained model"""
        model_path = os.path.join(self.grader.models_dir, f"grader_model_{assignment_id or 'global'}.pkl")
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.vectorizer = data['vectorizer']
                    self.is_trained = data['is_trained']
                return True
            except:
                return False
        return False

def grade_submissions_page(grader):
    st.header("🤖 Grade Submissions")
    
    # Initialize AI grader and check status
    ai_grader = AIGrader(grader)
    
    # Show AI model status and selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if ai_grader.use_local_ai:
            st.success(f"🟢 Local AI Model ({ai_grader.local_ai.model_name}) Connected")
            
            # Check and show memory status
            memory_status = ai_grader.local_ai.check_model_memory_status()
            if memory_status:
                st.success("💾 Model loaded in memory - responses will be fast!")
                if ai_grader.local_ai.last_response_time:
                    st.caption(f"Last response: {ai_grader.local_ai.last_response_time:.1f}s")
            else:
                st.warning("💿 Model not in memory - first request will be slow")
                
                # Add warmup button
                if st.button("🔥 Warm Up Model", help="Load model into memory for faster responses"):
                    with st.spinner("Loading model into memory..."):
                        success, message = ai_grader.local_ai.warm_up_model()
                        if success:
                            st.success(message)
                        else:
                            st.warning(message)
                        st.rerun()
            
            # Show model info and performance warning
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_info = next((m for m in models if m.get('name') == ai_grader.local_ai.model_name), None)
                    if model_info:
                        size_gb = model_info.get('size', 0) / (1024**3)
                        st.caption(f"Model size: {size_gb:.1f} GB")
                        
                        if memory_status:
                            st.success("⚡ Fast responses expected (model in memory)")
                        elif size_gb > 50:
                            st.warning("⚠️ Large model - first request: 2-5 minutes, then fast")
                        elif size_gb > 20:
                            st.info("📊 Medium model - first request: 30-60 seconds, then fast")
                        else:
                            st.success("⚡ Fast model - quick loading and responses")
            except:
                pass
        else:
            st.warning("🟡 Local AI Model Not Available")
            st.info("Possible issues:")
            st.info("• Ollama not running (run: ollama serve)")
            st.info("• External drive not mounted")
            st.info("• Model not accessible")
            st.info("Using rule-based grading as fallback.")
    
    with col2:
        if st.button("🔄 Refresh AI Status"):
            ai_grader.use_local_ai = ai_grader.local_ai.is_available()
            st.rerun()
    
    # Model selection for performance tuning
    if ai_grader.use_local_ai:
        st.subheader("🎛️ MLX Model Selection")
        
        # Get available MLX models
        try:
            import os
            import glob
            
            # Look for MLX models in HuggingFace cache (host machine)
            hf_cache = os.path.expanduser("~/.cache/huggingface/hub/")
            mlx_models = {}
            
            print(f"🔍 Looking for MLX models in: {hf_cache}")
            
            if os.path.exists(hf_cache):
                # Find MLX model directories with more flexible matching
                model_dirs = glob.glob(os.path.join(hf_cache, "models--*mlx*"))
                model_dirs.extend(glob.glob(os.path.join(hf_cache, "models--*MLX*")))
                model_dirs.extend(glob.glob(os.path.join(hf_cache, "models--lmstudio-community--*")))
                model_dirs.extend(glob.glob(os.path.join(hf_cache, "models--mlx-community--*")))
                
                print(f"📁 Found {len(model_dirs)} potential MLX model directories")
                
                for model_dir in model_dirs:
                    # Extract model name from directory
                    dir_name = os.path.basename(model_dir)
                    if dir_name.startswith("models--"):
                        # Convert models--org--name format to org/name
                        parts = dir_name[8:].split("--")
                        if len(parts) >= 2:
                            model_name = "/".join(parts)
                            
                            # Categorize by size/type with special handling for Kimi K2
                            if "kimi" in model_name.lower() and "k2" in model_name.lower():
                                category = "🚀 Kimi K2 (Excellent for Analysis)"
                                size_est = "~15GB"
                            elif "120b" in model_name.lower():
                                category = "🐌 Excellent (120B)"
                                size_est = "~70GB"
                            elif "70b" in model_name.lower():
                                category = "⚖️ Great (70B)"
                                size_est = "~40GB"
                            elif "27b" in model_name.lower():
                                category = "⚡ Fast (27B)"
                                size_est = "~15GB"
                            elif "20b" in model_name.lower():
                                category = "⚡ Fast (20B)"
                                size_est = "~12GB"
                            elif "17b" in model_name.lower():
                                category = "⚡ Fast (17B)"
                                size_est = "~10GB"
                            else:
                                category = "🤖 Unknown Size"
                                size_est = "~?GB"
                            
                            display_name = f"{model_name} ({size_est}) - {category}"
                            mlx_models[display_name] = model_name
            
            if mlx_models:
                # Find current model display name
                current_model = getattr(ai_grader.local_ai, 'model_name', 'lmstudio-community/gpt-oss-120b-MLX-8bit')
                current_display = next((k for k, v in mlx_models.items() if v == current_model), list(mlx_models.keys())[0])
                
                selected_model = st.selectbox(
                    "Choose MLX grading model:",
                    options=list(mlx_models.keys()),
                    index=list(mlx_models.keys()).index(current_display) if current_display in mlx_models else 0,
                    help="MLX models are optimized for Apple Silicon. Larger models provide better feedback but use more memory."
                )
                
                if mlx_models[selected_model] != current_model:
                    if st.button("Switch MLX Model"):
                        # Update the MLX client model
                        ai_grader.local_ai.model_name = mlx_models[selected_model]
                        ai_grader.local_ai.model_loaded_in_memory = False  # Force reload
                        st.success(f"Switched to {mlx_models[selected_model]}")
                        st.info("Model will be loaded on next grading request")
                        st.rerun()
                        
                # Show current model info
                st.info(f"**Current Model**: {current_model}")
                if hasattr(ai_grader.local_ai, 'model_loaded_in_memory') and ai_grader.local_ai.model_loaded_in_memory:
                    st.success("✅ Model loaded in memory")
                else:
                    st.warning("💤 Model not loaded (will load on first use)")
                    
            else:
                st.warning("No MLX models found in HuggingFace cache")
                st.info("Available models detected from your system:")
                st.code("""
• lmstudio-community/gpt-oss-120b-MLX-8bit (Current)
• mlx-community/DeepSeek-R1-Distill-Llama-70B-4bit  
• mlx-community/gemma-2-27b-it-4bit
• mlx-community/gemma-2-27b-it-8bit
• mlx-community/Meta-Llama-3.1-70B-Instruct-4bit
• And more...
                """)
                
        except Exception as e:
            st.error(f"Error loading MLX models: {e}")
            st.info("Using default model: lmstudio-community/gpt-oss-120b-MLX-8bit")
    
    # Select assignment
    conn = sqlite3.connect(grader.db_path)
    assignments = pd.read_sql_query("SELECT id, name FROM assignments ORDER BY created_date DESC", conn)
    
    if assignments.empty:
        st.warning("No assignments found.")
        return
    
    assignment_options = {row['name']: row['id'] for _, row in assignments.iterrows()}
    selected_assignment = st.selectbox("Select Assignment", list(assignment_options.keys()))
    assignment_id = assignment_options[selected_assignment]
    
    # Get ungraded submissions
    ungraded = pd.read_sql_query("""
        SELECT id, student_id, notebook_path, submission_date
        FROM submissions
        WHERE assignment_id = ? AND ai_score IS NULL
        ORDER BY submission_date
    """, conn, params=(assignment_id,))
    
    conn.close()
    
    if ungraded.empty:
        st.info("No ungraded submissions found.")
        return
    
    st.write(f"Found {len(ungraded)} ungraded submissions")
    
    # Load any existing model
    ai_grader.load_model(assignment_id)
    
    # Grading options
    col1, col2 = st.columns(2)
    
    # Add session management
    if 'grading_session_active' not in st.session_state:
        st.session_state.grading_session_active = False
    
    # Grading method selection
    st.subheader("🎯 Grading Method")
    grading_method = st.radio(
        "Choose grading approach:",
        ["Single Model (Original)", "Two-Model System (Enhanced)"],
        help="Two-Model System uses separate models for technical analysis and educational feedback"
    )
    
    use_two_model = grading_method == "Two-Model System (Enhanced)"
    
    if use_two_model and not TWO_MODEL_AVAILABLE:
        st.error("❌ Two-Model System not available. Using single model fallback.")
        use_two_model = False
    
    if use_two_model:
        st.success("🎯 Two-Model System: Technical analysis + Educational feedback")
        st.info("📊 Uses Qwen 3.0 Coder for analysis + Gemma-3-27B for feedback")
    else:
        st.info("🤖 Single Model: Traditional AI grading approach")
    
    # Show warning about navigation
    if not st.session_state.grading_session_active:
        st.warning("⚠️ **Important**: Do not navigate away from this page while grading is in progress. This will interrupt the process.")
        st.info("💡 **Tip**: Open a new browser tab if you need to check other things during grading.")
    
    with col1:
        if st.button("🚀 Grade All Submissions", type="primary", disabled=st.session_state.grading_session_active):
            st.session_state.grading_session_active = True
            if use_two_model:
                grade_all_submissions_two_model(grader, ungraded, assignment_id)
            else:
                grade_all_submissions(grader, ai_grader, ungraded, assignment_id)
    
    with col2:
        if st.session_state.grading_session_active:
            if st.button("🛑 Stop Grading", type="secondary"):
                st.session_state.grading_session_active = False
                st.warning("Grading stopped by user")
                st.rerun()
        else:
            if st.button("🔍 Grade Single Submission"):
                st.session_state.show_single_grading = True
                st.session_state.use_two_model_single = use_two_model
    
    # Single submission grading
    if st.session_state.get('show_single_grading', False):
        st.subheader("Grade Single Submission")
        
        student_options = {f"{row['student_id']} ({row['submission_date']})": row for _, row in ungraded.iterrows()}
        selected_student = st.selectbox("Select Student", list(student_options.keys()))
        
        use_two_model_single = st.session_state.get('use_two_model_single', False)
        if use_two_model_single:
            st.info("🎯 Using Two-Model System for this submission")
        
        if st.button("Grade This Submission"):
            submission = student_options[selected_student]
            if use_two_model_single:
                grade_single_submission_two_model(grader, submission, assignment_id)
            else:
                grade_single_submission(grader, ai_grader, submission, assignment_id)

def grade_all_submissions(grader, ai_grader, ungraded, assignment_id):
    """Grade all ungraded submissions"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    conn = sqlite3.connect(grader.db_path)
    cursor = conn.cursor()
    
    graded_count = 0
    
    for i, (_, submission) in enumerate(ungraded.iterrows()):
        # Check if user is still on the page (basic session check)
        try:
            # This will fail if user navigated away and session is invalid
            st.session_state.get('grading_active', True)
        except:
            st.warning("⚠️ Grading interrupted - user navigated away from page")
            break
            
        # Show different messages based on model status and position
        model_name = ai_grader.local_ai.model_name
        is_first_request = (i == 0 and not ai_grader.local_ai.model_loaded_in_memory)
        
        if is_first_request:
            status_text.text(f"🔄 Loading {model_name} into memory and grading {submission['student_id']}... (this will be slow)")
        elif "120b" in model_name.lower():
            remaining = len(ungraded) - i - 1
            if ai_grader.local_ai.model_loaded_in_memory:
                est_seconds = remaining * 30  # Fast responses once loaded
                status_text.text(f"⚡ Grading {submission['student_id']}... ({i+1}/{len(ungraded)}) - Est. {est_seconds}s remaining")
            else:
                est_minutes = remaining * 3  # Still loading from disk
                status_text.text(f"🐌 Grading {submission['student_id']}... ({i+1}/{len(ungraded)}) - Est. {est_minutes} min remaining")
        else:
            status_text.text(f"Grading {submission['student_id']}... ({i+1}/{len(ungraded)})")
        
        # Grade notebook with error handling
        try:
            result = ai_grader.grade_notebook(submission['notebook_path'], assignment_id)
        except Exception as e:
            st.error(f"❌ Error grading {submission['student_id']}: {str(e)}")
            continue  # Skip this submission and continue with others
        
        if result:
            # Filter AI feedback to remove internal monologue before storing
            filtered_feedback = filter_ai_feedback_for_storage(result['feedback'])
            
            # Update database
            cursor.execute("""
                UPDATE submissions
                SET ai_score = ?, ai_feedback = ?
                WHERE id = ?
            """, (result['score'], json.dumps(filtered_feedback), submission['id']))
            
            # Store training data if features available
            if 'features' in result:
                # Use filtered feedback for training data too
                cursor.execute("""
                    INSERT INTO ai_training_data (assignment_id, cell_content, features, ai_score, ai_feedback)
                    VALUES (?, ?, ?, ?, ?)
                """, (assignment_id, submission['notebook_path'], json.dumps(result['features']), result['score'], json.dumps(filtered_feedback)))
            
            # Generate PDF report
            try:
                from report_generator import PDFReportGenerator
                report_generator = PDFReportGenerator()
                
                # Prepare analysis result for report with proper structure
                if 'detailed_analysis' in result:
                    analysis_result = result['detailed_analysis'].copy()
                else:
                    # Create basic structure if detailed_analysis not available
                    analysis_result = {
                        'detailed_feedback': result.get('feedback', ['No detailed feedback available']),
                        'element_scores': {},
                        'missing_elements': [],
                        'code_issues': [],
                        'question_analysis': {},
                        'overall_assessment': 'Automated grading completed.'
                    }
                
                analysis_result['total_score'] = result['score']
                analysis_result['max_score'] = 37.5
                
                # Get student name and assignment name from database
                conn_temp = sqlite3.connect(ai_grader.grader.db_path)
                cursor_temp = conn_temp.cursor()
                
                # Get student name
                cursor_temp.execute('''
                    SELECT st.name FROM students st 
                    JOIN submissions s ON s.student_id = st.id 
                    WHERE s.id = ?
                ''', (submission['id'],))
                student_result = cursor_temp.fetchone()
                student_name = student_result[0] if student_result else f"Student_{submission['student_id']}"
                
                # Get assignment name
                cursor_temp.execute('SELECT name FROM assignments WHERE id = ?', (assignment_id,))
                assignment_result = cursor_temp.fetchone()
                assignment_name = assignment_result[0] if assignment_result else f"Assignment_{assignment_id}"
                
                conn_temp.close()
                
                # Generate report
                report_path = report_generator.generate_report(
                    student_name=student_name,
                    assignment_id=assignment_name,
                    analysis_result=analysis_result
                )
                
                # Show progress with report link
                with results_container:
                    st.write(f"✅ {student_name}: {result['score']:.1f} points - PDF report generated")
                    
            except Exception as e:
                # Show progress without report if generation fails
                with results_container:
                    st.write(f"✅ {submission['student_id']}: {result['score']:.1f} points (Report generation failed: {str(e)})")
            
            graded_count += 1
        
        progress_bar.progress((i + 1) / len(ungraded))
    
    conn.commit()
    conn.close()
    
    # Reset session state
    st.session_state.grading_session_active = False
    
    status_text.text("Grading complete!")
    st.success(f"Successfully graded {graded_count} submissions!")
    
    if st.button("View Results"):
        st.session_state.page = "view_results"
        st.rerun()

def grade_single_submission(grader, ai_grader, submission, assignment_id):
    """Grade a single submission with detailed output"""
    
    # Show different messages based on model size
    model_name = ai_grader.local_ai.model_name
    if "120b" in model_name.lower():
        spinner_text = f"Grading {submission['student_id']} with {model_name} (this may take 2-5 minutes)..."
    elif any(size in model_name.lower() for size in ["70b", "30b", "27b"]):
        spinner_text = f"Grading {submission['student_id']} with {model_name} (30-60 seconds)..."
    else:
        spinner_text = f"Grading {submission['student_id']} with {model_name}..."
    
    with st.spinner(spinner_text):
        result = ai_grader.grade_notebook(submission['notebook_path'], assignment_id)
        
        if result:
            st.success(f"Graded {submission['student_id']}: {result['score']:.1f} points")
            
            # Show detailed feedback
            st.subheader("AI Feedback")
            for feedback_item in result['feedback']:
                st.write(feedback_item)
            
            # Show detailed AI response if available
            if 'ai_detailed_response' in result:
                with st.expander("Detailed AI Analysis"):
                    st.json(result['ai_detailed_response'])
            
            # Update database
            conn = sqlite3.connect(grader.db_path)
            cursor = conn.cursor()
            
            # Filter AI feedback to remove internal monologue before storing
            filtered_feedback = filter_ai_feedback_for_storage(result['feedback'])
            
            cursor.execute("""
                UPDATE submissions
                SET ai_score = ?, ai_feedback = ?
                WHERE id = ?
            """, (result['score'], json.dumps(filtered_feedback), submission['id']))
            
            if 'features' in result:
                cursor.execute("""
                    INSERT INTO ai_training_data (assignment_id, cell_content, features, ai_score, ai_feedback)
                    VALUES (?, ?, ?, ?, ?)
                """, (assignment_id, submission['notebook_path'], json.dumps(result['features']), result['score'], json.dumps(result['feedback'])))
            
            conn.commit()
            conn.close()
            
        else:
            st.error(f"Failed to grade {submission['student_id']}")
    
    st.session_state.show_single_grading = False

def ai_training_page(grader):
    st.header("🧠 AI Training")
    
    st.markdown("""
    This page allows you to train the AI grader using your manual grading data.
    The more you grade manually, the better the AI becomes at predicting your grading style.
    """)
    
    # Select assignment for training
    conn = sqlite3.connect(grader.db_path)
    assignments = pd.read_sql_query("SELECT id, name FROM assignments", conn)
    
    if assignments.empty:
        st.warning("No assignments found.")
        return
    
    assignment_options = {row['name']: row['id'] for _, row in assignments.iterrows()}
    assignment_options["All Assignments"] = None
    
    selected_assignment = st.selectbox("Select Assignment for Training", list(assignment_options.keys()))
    assignment_id = assignment_options[selected_assignment]
    
    # Show training data statistics
    if assignment_id:
        training_count = pd.read_sql_query("""
            SELECT COUNT(*) as count FROM ai_training_data
            WHERE assignment_id = ? AND human_score IS NOT NULL
        """, conn, params=(assignment_id,)).iloc[0]['count']
    else:
        training_count = pd.read_sql_query("""
            SELECT COUNT(*) as count FROM ai_training_data
            WHERE human_score IS NOT NULL
        """, conn).iloc[0]['count']
    
    st.metric("Training Examples Available", training_count)
    
    if training_count < 10:
        st.warning("Need at least 10 manually graded examples to train the AI effectively.")
    
    # Train model
    if st.button("Train AI Model"):
        if training_count >= 10:
            ai_grader = AIGrader(grader)
            success, message = ai_grader.train_model(assignment_id)
            
            if success:
                st.success(message)
            else:
                st.error(message)
        else:
            st.error("Not enough training data. Please grade more submissions manually first.")
    
    conn.close()

def grade_all_submissions_two_model(grader, ungraded, assignment_id):
    """Grade all ungraded submissions using the two-model system"""
    if not TWO_MODEL_AVAILABLE:
        st.error("Two-Model System not available. Please check installation.")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    conn = sqlite3.connect(grader.db_path)
    cursor = conn.cursor()
    
    # Get assignment details
    assignment = pd.read_sql_query(
        "SELECT * FROM assignments WHERE id = ?", 
        conn, params=(assignment_id,)
    ).iloc[0]
    
    # Initialize two-model grader
    try:
        two_model_grader = TwoModelGrader()
        status_text.text("🎯 Two-Model System initialized successfully")
    except Exception as e:
        st.error(f"Failed to initialize Two-Model System: {e}")
        conn.close()
        return
    
    graded_count = 0
    total_submissions = len(ungraded)
    
    for idx, (_, submission) in enumerate(ungraded.iterrows()):
        if not st.session_state.grading_session_active:
            status_text.text("❌ Grading stopped by user")
            break
            
        progress = (idx + 1) / total_submissions
        progress_bar.progress(progress)
        status_text.text(f"🎯 Grading {submission['student_id']} ({idx + 1}/{total_submissions}) - Two-Model System")
        
        try:
            # Load notebook
            with open(submission['notebook_path'], 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=4)
            
            # Grade using two-model system
            result = two_model_grader.grade_submission(
                notebook_path=submission['notebook_path'],
                assignment_name=assignment['name'],
                student_name=submission['student_id']
            )
            
            if result and 'final_score' in result:
                # Filter AI feedback to remove internal monologue before storing
                raw_feedback = result.get('detailed_feedback', 'No feedback available')
                filtered_feedback = filter_ai_feedback_for_storage(raw_feedback)
                
                # Update database
                cursor.execute("""
                    UPDATE submissions 
                    SET ai_score = ?, ai_feedback = ?, final_score = ?, graded_date = ?
                    WHERE id = ?
                """, (
                    result['final_score'],
                    json.dumps(filtered_feedback) if isinstance(filtered_feedback, (dict, list)) else filtered_feedback,
                    result['final_score'],
                    datetime.now(),
                    submission['id']
                ))
                conn.commit()
                graded_count += 1
                
                # Show result
                with results_container:
                    st.success(f"✅ {submission['student_id']}: {result['final_score']:.1f}% (Two-Model)")
                    with st.expander(f"Feedback for {submission['student_id']}"):
                        st.write(result.get('detailed_feedback', 'No feedback available'))
            else:
                st.error(f"❌ Failed to grade {submission['student_id']}")
                
        except Exception as e:
            st.error(f"❌ Error grading {submission['student_id']}: {str(e)}")
            continue
    
    conn.close()
    st.session_state.grading_session_active = False
    
    if graded_count > 0:
        st.success(f"🎯 Two-Model grading complete! Graded {graded_count}/{total_submissions} submissions")
    else:
        st.warning("No submissions were successfully graded")
    
    st.rerun()

def grade_single_submission_two_model(grader, submission, assignment_id):
    """Grade a single submission using the two-model system"""
    if not TWO_MODEL_AVAILABLE:
        st.error("Two-Model System not available. Please check installation.")
        return
    
    conn = sqlite3.connect(grader.db_path)
    
    # Get assignment details
    assignment = pd.read_sql_query(
        "SELECT * FROM assignments WHERE id = ?", 
        conn, params=(assignment_id,)
    ).iloc[0]
    
    with st.spinner(f"🎯 Grading {submission['student_id']} with Two-Model System..."):
        try:
            # Initialize two-model grader
            two_model_grader = TwoModelGrader()
            
            # Grade using two-model system
            result = two_model_grader.grade_submission(
                notebook_path=submission['notebook_path'],
                assignment_name=assignment['name'],
                student_name=submission['student_id']
            )
            
            if result and 'final_score' in result:
                # Filter AI feedback to remove internal monologue before storing
                raw_feedback = result.get('detailed_feedback', 'No feedback available')
                filtered_feedback = filter_ai_feedback_for_storage(raw_feedback)
                
                # Update database
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE submissions 
                    SET ai_score = ?, ai_feedback = ?, final_score = ?, graded_date = ?
                    WHERE id = ?
                """, (
                    result['final_score'],
                    json.dumps(filtered_feedback) if isinstance(filtered_feedback, (dict, list)) else filtered_feedback,
                    result['final_score'],
                    datetime.now(),
                    submission['id']
                ))
                conn.commit()
                
                # Show detailed results
                st.success(f"✅ **{submission['student_id']}** graded successfully!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Final Score", f"{result['final_score']:.1f}%")
                with col2:
                    st.metric("Grading Method", "Two-Model System")
                
                # Show detailed feedback
                st.subheader("📝 Detailed Feedback")
                st.write(result.get('detailed_feedback', 'No feedback available'))
                
                # Show technical analysis if available
                if 'technical_analysis' in result:
                    with st.expander("🔧 Technical Analysis Details"):
                        st.write(result['technical_analysis'])
                
                # Show educational feedback if available  
                if 'educational_feedback' in result:
                    with st.expander("📚 Educational Feedback Details"):
                        st.write(result['educational_feedback'])
                
            else:
                st.error(f"❌ Failed to grade {submission['student_id']}")
                
        except Exception as e:
            st.error(f"❌ Error grading {submission['student_id']}: {str(e)}")
    
    conn.close()
    st.session_state.show_single_grading = False
    st.rerun()