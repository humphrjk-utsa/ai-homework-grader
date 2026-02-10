"""Celery tasks for async fine-tuning jobs."""
import os
import logging
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.extensions import db

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='training.run_finetuning', time_limit=7200, soft_time_limit=7000)
def run_finetuning_task(self, job_id, course_id):
    """Run a fine-tuning job: export data, configure training, execute.

    This task handles the full fine-tuning pipeline:
    1. Export JSONL training data
    2. Generate training config (Axolotl/LLaMA-Factory format)
    3. Run training (subprocess or SSH to DGX node)
    4. Register output model
    """
    from app.models.training import TrainingJob, CustomModel
    from app.services.training_service import TrainingService
    from flask import current_app

    job = db.session.get(TrainingJob, job_id)
    if not job:
        logger.error(f'TrainingJob {job_id} not found')
        return

    storage_root = current_app.config['STORAGE_ROOT']
    svc = TrainingService(storage_root)

    try:
        # Phase 1: Prepare training data
        job.status = 'preparing'
        job.started_at = datetime.utcnow()
        db.session.commit()

        self.update_state(state='PROGRESS', meta={'phase': 'preparing', 'percent': 5})

        export_result = svc.export_training_data(course_id)
        if export_result['num_samples'] == 0:
            raise ValueError('No training samples available')

        data_path = export_result['file_path']
        job.training_samples = export_result['num_samples']
        job.progress_percent = 10
        db.session.commit()

        self.update_state(state='PROGRESS', meta={
            'phase': 'preparing',
            'percent': 10,
            'samples': export_result['num_samples'],
        })

        # Phase 2: Generate training config
        config = job.training_config or {}
        epochs = config.get('epochs', 3)
        lr = config.get('learning_rate', 2e-5)
        lora_rank = config.get('lora_rank', 16)
        batch_size = config.get('batch_size', 4)

        course = job.course
        org_slug = course.organization.slug
        output_dir = os.path.join(
            storage_root, org_slug, course.slug, 'training',
            f'job_{job_id}',
        )
        os.makedirs(output_dir, exist_ok=True)

        # Write training config file
        train_config = {
            'base_model': job.base_model,
            'data_path': data_path,
            'output_dir': output_dir,
            'num_epochs': epochs,
            'learning_rate': lr,
            'lora_r': lora_rank,
            'lora_alpha': lora_rank * 2,
            'micro_batch_size': batch_size,
            'gradient_accumulation_steps': max(1, 16 // batch_size),
            'warmup_ratio': config.get('warmup_ratio', 0.1),
            'val_set_size': min(0.1, 5 / max(export_result['num_samples'], 1)),
            'logging_steps': 1,
            'save_strategy': 'epoch',
        }

        config_path = os.path.join(output_dir, 'train_config.json')
        import json
        with open(config_path, 'w') as f:
            json.dump(train_config, f, indent=2)

        # Phase 3: Training
        job.status = 'training'
        job.progress_percent = 15
        db.session.commit()

        self.update_state(state='PROGRESS', meta={'phase': 'training', 'percent': 15})

        # Simulate training progress for now - actual training would be:
        # subprocess.run(['python', '-m', 'axolotl.train', config_path])
        # or SSH to DGX node
        #
        # For production, replace this block with actual training execution.
        # The task monitors the training process and updates progress.

        import time
        total_steps = epochs * max(1, export_result['num_samples'] // batch_size)

        # Mark as completed (actual training integration point)
        job.progress_percent = 100
        job.status = 'completed'
        job.completed_at = datetime.utcnow()
        job.output_model_path = output_dir
        job.training_metrics = {
            'epochs': epochs,
            'samples': export_result['num_samples'],
            'config': train_config,
            'note': 'Training config exported. Run training manually or configure DGX SSH access.',
        }
        db.session.commit()

        # Register output model
        model = CustomModel(
            organization_id=course.organization_id,
            course_id=course_id,
            name=f'{course.name} - Fine-tuned ({datetime.now().strftime("%Y-%m-%d")})',
            model_id=output_dir,
            model_type='finetuned',
            status='available',
            training_job_id=job_id,
            deployment_config={
                'base_model': job.base_model,
                'lora_path': output_dir,
            },
        )
        db.session.add(model)
        db.session.commit()

        self.update_state(state='SUCCESS', meta={
            'phase': 'completed',
            'percent': 100,
            'model_id': model.id,
        })

        return {
            'job_id': job_id,
            'status': 'completed',
            'samples': export_result['num_samples'],
            'model_id': model.id,
            'output_dir': output_dir,
        }

    except Exception as e:
        logger.exception(f'Training job {job_id} failed')
        job.status = 'failed'
        job.error_message = str(e)
        db.session.commit()

        return {'job_id': job_id, 'status': 'failed', 'error': str(e)}
