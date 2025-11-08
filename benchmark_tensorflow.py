#!/usr/bin/env python3
"""
TensorFlow Deep Learning Benchmark for DGX Sparks
Tests GPU performance with real ML workloads
"""

import tensorflow as tf
import time
import numpy as np

def benchmark_tensorflow():
    """Benchmark TensorFlow GPU performance"""
    
    print("="*80)
    print("TENSORFLOW GPU BENCHMARK")
    print("="*80)
    
    # Check GPU availability
    gpus = tf.config.list_physical_devices('GPU')
    if not gpus:
        print("❌ No GPU detected!")
        return
    
    print(f"✅ TensorFlow version: {tf.__version__}")
    print(f"✅ GPUs detected: {len(gpus)}")
    for i, gpu in enumerate(gpus):
        print(f"   GPU {i}: {gpu.name}")
    print()
    
    # Test 1: Matrix Operations
    print("Test 1: Large Matrix Multiplication")
    print("-" * 80)
    
    with tf.device('/GPU:0'):
        for size in [1000, 5000, 10000]:
            a = tf.random.normal([size, size])
            b = tf.random.normal([size, size])
            
            # Warm up
            _ = tf.matmul(a, b)
            
            # Benchmark
            start = time.time()
            for _ in range(10):
                c = tf.matmul(a, b)
            elapsed = time.time() - start
            
            gflops = (2 * size**3 * 10) / (elapsed * 1e9)
            print(f"  {size}x{size}: {elapsed/10:.4f}s per matmul, {gflops:.2f} GFLOPS")
    
    print()
    
    # Test 2: CNN Training (Computer Vision)
    print("Test 2: CNN Training (Computer Vision)")
    print("-" * 80)
    
    # Create a simple CNN model
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(224, 224, 3)),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(128, 3, activation='relu'),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    
    # Create dummy data
    batch_size = 32
    x_train = np.random.random((batch_size * 10, 224, 224, 3)).astype('float32')
    y_train = np.random.randint(0, 10, (batch_size * 10,))
    
    # Warm up
    model.fit(x_train[:batch_size], y_train[:batch_size], epochs=1, verbose=0)
    
    # Benchmark
    start = time.time()
    history = model.fit(x_train, y_train, batch_size=batch_size, epochs=5, verbose=0)
    elapsed = time.time() - start
    
    print(f"  5 epochs training: {elapsed:.2f}s")
    print(f"  {elapsed/5:.2f}s per epoch")
    print(f"  {(batch_size * 10 * 5)/elapsed:.2f} images/sec")
    
    print()
    
    # Test 3: ResNet50 Inference (Real Model)
    print("Test 3: ResNet50 Inference (Computer Vision)")
    print("-" * 80)
    
    # Load pre-trained ResNet50
    resnet = tf.keras.applications.ResNet50(weights=None, input_shape=(224, 224, 3))
    
    # Create batch of images
    batch_size = 32
    images = tf.random.normal([batch_size, 224, 224, 3])
    
    # Warm up
    _ = resnet(images, training=False)
    
    # Benchmark
    iterations = 100
    start = time.time()
    for _ in range(iterations):
        _ = resnet(images, training=False)
    elapsed = time.time() - start
    
    print(f"  {iterations} inference batches: {elapsed:.2f}s")
    print(f"  {(batch_size * iterations)/elapsed:.2f} images/sec")
    print(f"  {elapsed/(iterations)*1000:.2f}ms per batch")
    
    print()
    
    # Test 4: LSTM Training (NLP/Sequence)
    print("Test 4: LSTM Training (NLP/Sequence)")
    print("-" * 80)
    
    # Create LSTM model
    lstm_model = tf.keras.Sequential([
        tf.keras.layers.Embedding(10000, 128, input_length=100),
        tf.keras.layers.LSTM(128, return_sequences=True),
        tf.keras.layers.LSTM(64),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    lstm_model.compile(optimizer='adam', loss='binary_crossentropy')
    
    # Create dummy sequence data
    x_seq = np.random.randint(0, 10000, (1000, 100))
    y_seq = np.random.randint(0, 2, (1000,))
    
    # Warm up
    lstm_model.fit(x_seq[:32], y_seq[:32], epochs=1, verbose=0)
    
    # Benchmark
    start = time.time()
    lstm_model.fit(x_seq, y_seq, batch_size=32, epochs=3, verbose=0)
    elapsed = time.time() - start
    
    print(f"  3 epochs training: {elapsed:.2f}s")
    print(f"  {elapsed/3:.2f}s per epoch")
    
    print()
    
    # GPU Memory Info
    print("GPU Memory Info")
    print("-" * 80)
    gpu_info = tf.config.experimental.get_memory_info('GPU:0')
    print(f"  Current Memory: {gpu_info['current'] / 1e9:.2f} GB")
    print(f"  Peak Memory: {gpu_info['peak'] / 1e9:.2f} GB")
    
    print()
    print("="*80)
    print("BENCHMARK COMPLETE - GPU IS WORKING FOR DEEP LEARNING!")
    print("="*80)

if __name__ == "__main__":
    try:
        benchmark_tensorflow()
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
