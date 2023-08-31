import os
import shutil
from sklearn.model_selection import train_test_split


# Path ke folder utama dataset
dataset_path = 'C:/Users/dhafiyanayla/Downloads/dataset'

# Path ke folder tempat Anda ingin menyimpan set pelatihan, validasi, dan pengujian yang terbagi
split_data_path = 'C:/Users/dhafiyanayla/downloads/foodsystem'
os.makedirs(split_data_path, exist_ok=True)

# Daftar nama kelas (misal: ['sayur', 'buah'])
class_names = os.listdir(dataset_path)


# Loop melalui setiap kelas
for class_name in class_names:
    class_path = os.path.join(dataset_path, class_name)  # Memastikan class_path adalah direktori
    if os.path.isdir(class_path):
        files = os.listdir(class_path)
    
    # Split dataset menjadi set pelatihan, validasi, dan pengujian
    train_files, test_files = train_test_split(files, test_size=0.2, random_state=42)
    train_files, validation_files = train_test_split(train_files, test_size=0.25, random_state=42)
    
    # Path ke folder tujuan untuk setiap kelas
    train_class_path = os.path.join(split_data_path, 'train', class_name)
    validation_class_path = os.path.join(split_data_path, 'validation', class_name)
    test_class_path = os.path.join(split_data_path, 'test', class_name)
    
    # Buat folder untuk setiap kelas di set pelatihan, validasi, dan pengujian
    os.makedirs(train_class_path, exist_ok=True)
    os.makedirs(validation_class_path, exist_ok=True)
    os.makedirs(test_class_path, exist_ok=True)
    
    # Pindahkan gambar ke folder yang sesuai
    for file in train_files:
        src_path = os.path.join(class_path, file)
        dst_path = os.path.join(train_class_path, file)
        shutil.copytree(src_path, dst_path)

    for file in validation_files:
        src_path = os.path.join(class_path, file)
        dst_path = os.path.join(validation_class_path, file)
        shutil.copytree(src_path, dst_path)

    for file in test_files:
        src_path = os.path.join(class_path, file)
        dst_path = os.path.join(test_class_path, file)
        shutil.copytree(src_path, dst_path)
