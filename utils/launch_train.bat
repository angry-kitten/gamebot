rem python Tensorflow\models\research\object_detection\model_main_tf2.py --model_dir=Tensorflow\workspace\models\my_ssd_mobnet --pipeline_config_path=Tensorflow\workspace\models\my_ssd_mobnet\pipeline.config --num_train_steps=30000

rem python Tensorflow\models\research\object_detection\model_main_tf2.py --model_dir=Tensorflow\workspace\models\my_d6 --pipeline_config_path=Tensorflow\workspace\models\my_d6\pipeline.config --num_train_steps=30000

rem set TF_GPU_ALLOCATOR=cuda_malloc_async
rem python Tensorflow\models\research\object_detection\model_main_tf2.py --model_dir=Tensorflow\workspace\models\my_rn152 --pipeline_config_path=Tensorflow\workspace\models\my_rn152\pipeline.config --num_train_steps=2000

python Tensorflow\models\research\object_detection\model_main_tf2.py --model_dir=Tensorflow\workspace\models\my_mn640 --pipeline_config_path=Tensorflow\workspace\models\my_mn640\pipeline.config --num_train_steps=500000
