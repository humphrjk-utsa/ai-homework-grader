"""Training and custom model management models."""
from datetime import datetime

from app.extensions import db


class TrainingJob(db.Model):
    __tablename__ = 'training_jobs'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    base_model = db.Column(db.String(200), nullable=False)
    training_config = db.Column(db.JSON, default=dict)  # epochs, lr, lora_rank, batch_size
    status = db.Column(db.String(20), nullable=False, default='pending')
    # pending → preparing → training → completed → failed
    progress_percent = db.Column(db.Float, default=0)

    output_model_path = db.Column(db.String(500))
    training_metrics = db.Column(db.JSON)  # loss curves, eval metrics
    training_samples = db.Column(db.Integer, default=0)

    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    created_by = db.relationship('User', backref='training_jobs')
    course = db.relationship('Course', backref='training_jobs')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'created_by_id': self.created_by_id,
            'base_model': self.base_model,
            'training_config': self.training_config,
            'status': self.status,
            'progress_percent': self.progress_percent,
            'output_model_path': self.output_model_path,
            'training_metrics': self.training_metrics,
            'training_samples': self.training_samples,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class CustomModel(db.Model):
    __tablename__ = 'custom_models'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))  # nullable = global model

    name = db.Column(db.String(200), nullable=False)
    model_id = db.Column(db.String(500), nullable=False)  # HuggingFace ID or local path
    model_type = db.Column(db.String(20), nullable=False, default='base')
    # base | finetuned | custom

    server_url = db.Column(db.String(500))  # vLLM endpoint when deployed
    container_id = db.Column(db.String(100))  # Docker container ID
    status = db.Column(db.String(20), nullable=False, default='available')
    # available | deploying | running | stopped | error

    deployment_config = db.Column(db.JSON, default=dict)
    # gpu_ids, quantization, max_model_len, tensor_parallel_size

    training_job_id = db.Column(db.Integer, db.ForeignKey('training_jobs.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = db.relationship('Organization', backref='custom_models')
    course = db.relationship('Course', backref='custom_models')
    training_job = db.relationship('TrainingJob', backref='output_model')

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'course_id': self.course_id,
            'name': self.name,
            'model_id': self.model_id,
            'model_type': self.model_type,
            'server_url': self.server_url,
            'container_id': self.container_id,
            'status': self.status,
            'deployment_config': self.deployment_config,
            'training_job_id': self.training_job_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
