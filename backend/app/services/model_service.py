"""
ModelService: Deploy and manage vLLM model containers.

Supports deploying models as vLLM Docker containers on DGX Sparks or
local machines with GPU access.
"""
import os
import json
import logging
import subprocess

from app.extensions import db

logger = logging.getLogger(__name__)

# Built-in models that are always available
BUILTIN_MODELS = [
    {
        'name': 'Qwen3 Coder 30B (FP8)',
        'model_id': 'Qwen/Qwen3-Coder-30B-A3B-Instruct',
        'model_type': 'base',
        'description': 'Fast code analysis model. Recommended for code review tasks.',
    },
    {
        'name': 'GPT-OSS 120B (MXFP4)',
        'model_id': 'openai/gpt-oss-120b',
        'model_type': 'base',
        'description': 'Large reasoning model. Best for comprehensive feedback generation.',
    },
]

# Default vLLM Docker image
VLLM_IMAGE = 'nvcr.io/nvidia/vllm:26.01-py3'


class ModelService:
    def __init__(self, storage_root: str):
        self.storage_root = storage_root

    def list_models(self, organization_id: int, course_id: int = None) -> list:
        """List all available models (built-in + custom + fine-tuned)."""
        from app.models.training import CustomModel

        models = []

        # Built-in models
        for m in BUILTIN_MODELS:
            models.append({
                **m,
                'id': None,
                'status': 'available',
                'deployment_config': {},
                'is_builtin': True,
            })

        # Custom/fine-tuned models for this org
        query = CustomModel.query.filter_by(organization_id=organization_id)
        if course_id:
            # Include org-wide models (course_id=None) plus course-specific
            query = query.filter(
                db.or_(CustomModel.course_id == course_id, CustomModel.course_id.is_(None))
            )

        for cm in query.all():
            d = cm.to_dict()
            d['is_builtin'] = False
            models.append(d)

        return models

    def register_model(self, organization_id: int, data: dict):
        """Register a new custom model."""
        from app.models.training import CustomModel

        model = CustomModel(
            organization_id=organization_id,
            course_id=data.get('course_id'),
            name=data['name'],
            model_id=data['model_id'],
            model_type=data.get('model_type', 'custom'),
            deployment_config=data.get('deployment_config', {}),
        )
        db.session.add(model)
        db.session.commit()
        return model

    def deploy_model(self, model_id: int, config: dict = None) -> dict:
        """Deploy a model as a vLLM Docker container.

        Args:
            model_id: CustomModel.id
            config: Override deployment config (gpu_ids, quantization, max_model_len, port)

        Returns:
            dict with container_id, server_url, status
        """
        from app.models.training import CustomModel

        model = db.session.get(CustomModel, model_id)
        if not model:
            raise ValueError(f'Model {model_id} not found')

        if model.status == 'running':
            return {'container_id': model.container_id, 'server_url': model.server_url, 'status': 'running'}

        model.status = 'deploying'
        db.session.commit()

        deploy_cfg = {**(model.deployment_config or {}), **(config or {})}
        port = deploy_cfg.get('port', 8000)
        gpu_ids = deploy_cfg.get('gpu_ids', '0')
        quantization = deploy_cfg.get('quantization')
        max_model_len = deploy_cfg.get('max_model_len', 8192)
        tensor_parallel = deploy_cfg.get('tensor_parallel_size', 1)
        host = deploy_cfg.get('host', 'localhost')

        # Build docker command
        cmd = [
            'docker', 'run', '-d',
            '--gpus', f'"device={gpu_ids}"',
            '-p', f'{port}:8000',
            '-v', f'{os.path.expanduser("~")}/.cache/huggingface:/root/.cache/huggingface',
            '-e', 'HF_HUB_OFFLINE=1',
            '-e', 'TRANSFORMERS_OFFLINE=1',
            '--name', f'vllm-{model.id}',
            VLLM_IMAGE,
            '--model', model.model_id,
            '--max-model-len', str(max_model_len),
            '--tensor-parallel-size', str(tensor_parallel),
        ]

        if quantization:
            cmd.extend(['--quantization', quantization])

        try:
            result = subprocess.run(
                ' '.join(cmd),
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                model.status = 'error'
                db.session.commit()
                raise RuntimeError(f'Docker run failed: {result.stderr}')

            container_id = result.stdout.strip()[:12]
            server_url = f'http://{host}:{port}/v1'

            model.container_id = container_id
            model.server_url = server_url
            model.status = 'running'
            model.deployment_config = deploy_cfg
            db.session.commit()

            return {
                'container_id': container_id,
                'server_url': server_url,
                'status': 'running',
            }

        except subprocess.TimeoutExpired:
            model.status = 'error'
            db.session.commit()
            raise RuntimeError('Docker run timed out')

        except Exception as e:
            model.status = 'error'
            db.session.commit()
            raise

    def stop_model(self, model_id: int) -> dict:
        """Stop a running vLLM container."""
        from app.models.training import CustomModel

        model = db.session.get(CustomModel, model_id)
        if not model:
            raise ValueError(f'Model {model_id} not found')

        if model.container_id:
            try:
                subprocess.run(
                    ['docker', 'stop', model.container_id],
                    capture_output=True,
                    timeout=30,
                )
                subprocess.run(
                    ['docker', 'rm', model.container_id],
                    capture_output=True,
                    timeout=15,
                )
            except Exception as e:
                logger.warning(f'Failed to stop container {model.container_id}: {e}')

        model.status = 'stopped'
        model.container_id = None
        model.server_url = None
        db.session.commit()

        return {'status': 'stopped'}

    def get_running_models(self, organization_id: int) -> list:
        """Get all currently running model containers."""
        from app.models.training import CustomModel

        models = CustomModel.query.filter_by(
            organization_id=organization_id,
            status='running',
        ).all()

        return [m.to_dict() for m in models]

    def set_course_model_config(self, course_id: int, config: dict):
        """Set which models a course uses for grading."""
        from app.models.course import Course

        course = db.session.get(Course, course_id)
        if not course:
            raise ValueError(f'Course {course_id} not found')

        settings = course.settings or {}
        settings['model_config'] = config
        course.settings = settings
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(course, 'settings')
        db.session.commit()

        return settings
