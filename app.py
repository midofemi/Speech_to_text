from flask import Flask, request, jsonify, render_template

from STT.pipeline.training_pipeline import TrainingPipeline
from STT.pipeline.prediction_pipeline import Prediction
from STT.entity.config_entity import PredictionPipelineConfig
from STT.cloud_storage.s3_operations import S3Sync
from STT.constants import S3_BUCKET_URI

import os

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route("/train", methods=['GET'])
def train():
    train_pipeline = TrainingPipeline()

    train_pipeline.run_pipeline()

    return "Training completed"

@app.route('/predict', methods=['POST', 'GET'])
def predictroute():
    config = PredictionPipelineConfig()

    os.makedirs(config.prediction_artifact_dir, exist_ok=True)
    os.makedirs(config.app_artifacts, exist_ok=True)

    s3_op = S3Sync()
    s3_op.sync_folder_from_s3(folder=config.model_download_path, aws_bucket_url=config.s3_model_path)

    audio = request.files['audio']
    wave_sounds_path = config.wave_sounds_path
    audio.save(wave_sounds_path)

    app_artifacts = config.app_artifacts
    os.makedirs(app_artifacts, exist_ok=True)

    if request.method == 'POST':

        pred = Prediction(wave_sounds_path, config.model_download_path)
        result = pred.prediction()
        
        return render_template('result.html', Result = result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
