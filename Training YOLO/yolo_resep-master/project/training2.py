from sklearn.model_selection import train_test_split
# Contoh data dan label
data = [
    "C:/Users/dhafiyanayla/Downloads/dataset/Buah/Alpukat/image_1.jpg",
    "C:/Users/dhafiyanayla/Downloads/dataset/Buah/Alpukat/image_2.jpg",
    "C:/Users/dhafiyanayla/Downloads/dataset/Buah/Alpukat/image_3.jpg",
    "C:/Users/dhafiyanayla/Downloads/dataset/Buah/Alpukat/image_4.jpg",
    "C:/Users/dhafiyanayla/Downloads/dataset/Buah/Alpukat/image_5.jpg"

]  # Data Anda

labels = [1]  # Label bahan makanan

# Membagi dataset menjadi pelatihan (70%) dan pengujian (30%)
train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size=0.3, random_state=42)

# Membagi dataset menjadi pelatihan (60%), validasi (20%), dan pengujian (20%)
train_data, temp_data, train_labels, temp_labels = train_test_split(data, labels, test_size=0.4, random_state=42)
val_data, test_data, val_labels, test_labels = train_test_split(temp_data, temp_labels, test_size=0.5, random_state=42)
