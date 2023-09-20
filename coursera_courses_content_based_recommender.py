# -*- coding: utf-8 -*-
"""Proyek Kedua Machine Learning Terapan : Coursera Courses Content Based Recommender.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Zk1pKqvg-t4DdWn5t1v6X531ABXarqUR

# Data Collection
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from tensorflow.keras.layers import Input, Add, Activation, Lambda, Embedding, Reshape, Dot

# %matplotlib inline

!gdown --id "1FuRZhGKHEYLN4qoEzEKF2A7tuAG0fPyj"

courses = pd.read_csv("/content/Coursera.csv")
courses.head(10)

"""# Data Understanding

"""

courses.shape

courses.info()

courses.describe()

courses['Course Name']

courses['University'].value_counts()

courses['Difficulty Level'].value_counts()

courses['Course Rating'].value_counts()

courses['Skills'].value_counts()

courses.head(5)

"""# Data Preparation

"""

import numpy as np
import itertools

# Drop outliers menggunakan IQR
Q1 = courses.quantile(0.25)
Q3 = courses.quantile(0.75)
IQR=Q3-Q1
course=courses[~((courses<(Q1-1.5*IQR))|(courses>(Q3+1.5*IQR))).any(axis=1)]

# Cek ukuran dataset setelah kita drop outliers
course.shape

# Mengatasi missing value
course.isnull().sum()

# Mengambil kolom yang diperlukan
courses = course[['Course Name','Course Rating', 'Course Description', 'Skills']]

# Mengubah nama kolom
courses = courses.rename(columns={
    'Course Name': 'courseName',
    'Course Rating': 'rating',
    'Course Description': 'description',
    'Skills': 'skills'
})

courses = courses.merge(courses[['courseName', 'description']], on='courseName')
courses.head()

# Exclude rating yang ingin dihapus dari dataset
courses = courses[courses['rating'] != 'Not Calibrated']

# Reset index dataframe untuk menghindari error
courses = courses.reset_index(drop = True)

# Convert "rating" column to int64 data type
courses['rating'] = pd.to_numeric(courses['rating'])

courses.head(5)

course_list = courses.courseName.str.split("|").tolist()
course = list(set(itertools.chain(*course_list)))
course = list(set(course))

skills_list = courses.skills.str.split("|").tolist()
skills = list(set(itertools.chain(*skills_list)))
skills = list(set(skills))

"""# Model Development dengan Content Based Filtering

TF-IDF Vectorizer
"""

from sklearn.feature_extraction.text import TfidfVectorizer

# Inisialisasi TfidfVectorizer
tf = TfidfVectorizer(token_pattern=r"(?u)\b\w[\w-]*\w\b")

# Melakukan perhitungan idf pada data cuisine
tf.fit(courses['courseName'])

# Mapping array dari fitur index integer ke fitur nama
tf.get_feature_names_out()

# Melakukan fit lalu ditransformasikan ke bentuk matrix
tfidf_matrix = tf.fit_transform(courses['courseName'])

# Melihat ukuran matrix tfidf
tfidf_matrix.shape

# Mengubah vektor tf-idf dalam bentuk matriks dengan fungsi todense()
tfidf_matrix.todense()

# Membuat dataframe untuk melihat tf-idf matrix
pd.DataFrame(
    tfidf_matrix.todense(),
    columns=tf.get_feature_names_out(),
    index=courses.skills
).sample(10, axis=1).sample(10, axis=0)

"""Cosine Similarity"""

from sklearn.metrics.pairwise import cosine_similarity

# Menghitung cosine similarity pada matrix tf-idf
cosine_sim = cosine_similarity(tfidf_matrix)
cosine_sim

# Membuat dataframe dari variabel cosine_sim dengan baris dan kolom berupa nama course
cosine_sim_df = pd.DataFrame(cosine_sim, index=courses['courseName'], columns=courses['courseName'])
print('Shape:', cosine_sim_df.shape)

# Melihat similarity matrix pada setiap course
cosine_sim_df.sample(10, axis=1).sample(10, axis=0)

print(cosine_sim_df.sample(5, axis=1).sample(10, axis=0).to_markdown())

"""Euclidean Distance"""

# Menghitung euclidean distance pada matrix tf-idf
euclidean_dist = euclidean_distances(tfidf_matrix)

# Membuat dataframe dari variabel euclidean_dist dengan baris dan kolom berupa nama course
euclidean_dist_df = pd.DataFrame(euclidean_dist, index=courses.courseName, columns=courses.courseName)

euclidean_dist_df.sample(5, axis=1).sample(10, axis=0)

print(euclidean_dist_df.sample(5, axis=1).sample(10, axis=0).to_markdown())

"""# Model Development dengan Collaborative Filtering"""

# Import library
import pandas as pd
import numpy as np
from zipfile import ZipFile
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path
import matplotlib.pyplot as plt

# Mengubah courseName menjadi list tanpa nilai yang sama
course_name_list_id = courses['courseName'].unique().tolist()
print('list courseName: ', course_name_list_id)

# Melakukan encoding courseName (cn)
cn_to_cn_encoded = {x: i for i, x in enumerate(course_name_list_id)}
print('encoded courseName : ', cn_to_cn_encoded)

# Melakukan proses encoding angka ke ke courseName (cn)
cn_encoded_to_cn = {i: x for i, x in enumerate(course_name_list_id)}
print('encoded angka ke courseName: ', cn_encoded_to_cn)

# Mengubah skills menjadi list tanpa nilai yang sama
skill_list_id = courses['skills'].unique().tolist()
print('list skills: ', skill_list_id)

# Melakukan encoding skills
skill_to_skill_encoded = {x: i for i, x in enumerate(skill_list_id)}
print('encoded skills : ', skill_to_skill_encoded)

# Melakukan proses encoding angka ke ke skills
skill_encoded_to_skill = {i: x for i, x in enumerate(skill_list_id)}
print('encoded angka ke skills: ', skill_encoded_to_skill)

# Mapping courseName list ke dataframe courses
courses['courses_df'] = courses['courseName'].map(cn_to_cn_encoded)

# Mapping skills ke dataframe skills
courses['skills_df'] = courses['skills'].map(skill_to_skill_encoded)

courses

courses.info()

# Mendapatkan jumlah courseName
num_courses = len(cn_to_cn_encoded)

# Mendapatkan jumlah skills
num_skills = len(skill_to_skill_encoded)

# Nilai minimum rating
min_rating = min(courses['rating'])

# Nilai maksimal rating
max_rating = max(courses['rating'])

print('Number of Course: {}, Number of Skill: {}, Min rating: {}, Max rating: {}'.format(
    num_courses, num_skills, min_rating, max_rating
))

"""Split Data to Train & Test"""

# Mengacak dataset
df = courses.sample(frac=1, random_state=42)
df

# Membuat variabel x untuk mencocokkan dataframe courses dan skills menjadi satu value
x = df[['courses_df', 'skills_df']].values

# Membuat variabel y untuk membuat rating menjadi skala 0 sampai 1
y = df['rating'].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values

# Membagi menjadi 90% data train dan 10% data validasi
train_indices = int(0.9 * df.shape[0])
x_train, x_val, y_train, y_val = (
    x[:train_indices],
    x[train_indices:],
    y[:train_indices],
    y[train_indices:]
)

print(x, y)

"""# Training Model"""

class RecommenderNet(tf.keras.Model):

  # Insialisasi fungsi
  def __init__(self, num_courses, num_skills, embedding_size, **kwargs):
    super(RecommenderNet, self).__init__(**kwargs)
    self.num_courses = num_courses
    self.num_skills = num_skills
    self.embedding_size = embedding_size
    self.course_embedding = keras.layers.Embedding( # layer embedding course
        num_courses,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )
    self.course_bias = keras.layers.Embedding(num_courses, 1) # layer embedding course bias
    self.skill_embedding = keras.layers.Embedding( # layer embeddings skill
        num_skills,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )
    self.skill_bias = keras.layers.Embedding(num_skills, 1) # layer embedding skill bias

  def call(self, inputs):
    course_vector = self.course_embedding(inputs[:,0]) # memanggil layer embedding 1
    course_bias = self.course_bias(inputs[:, 0]) # memanggil layer embedding 2
    skill_vector = self.skill_embedding(inputs[:, 1]) # memanggil layer embedding 3
    skill_bias = self.skill_bias(inputs[:, 1]) # memanggil layer embedding 4

    dot_course_skill = tf.tensordot(course_vector, skill_vector, 2)

    x = dot_course_skill + course_bias + skill_bias

    return tf.nn.sigmoid(x) # activation sigmoid

model = RecommenderNet(num_courses, num_skills, 50)

model.compile(
    loss = tf.keras.losses.BinaryCrossentropy(),
    optimizer = keras.optimizers.Adam(learning_rate=0.001),
    metrics=[tf.keras.metrics.RootMeanSquaredError()]
)

# Memulai training
history = model.fit(
    x = x_train,
    y = y_train,
    batch_size = 64,
    epochs = 5,
    validation_data = (x_val, y_val),
)

"""Metric Visualization"""

plt.plot(history.history['root_mean_squared_error'])
plt.plot(history.history['val_root_mean_squared_error'])
plt.title('model_metrics')
plt.ylabel('root_mean_squared_error')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""Get course recommendation"""

courses

# Mengambil sample course
course_sample = df.courses_df.sample(1).iloc[0]

# Mengambil course sesuai sample course
courses_enrolled = courses[courses.courses_df == course_sample]
courses_enrolled

# Mengambil course yang tidak di-enroll
# Operator bitwise (~), https://docs.python.org/3/reference/expressions.html
courses_not_enrolled = courses[~courses['courseName'].isin(courses_enrolled.courseName.values)]['courseName']
print("Course not enrolled:", courses_not_enrolled)
courses_not_enrolled = list(
    set(courses_not_enrolled)
    .intersection(set(cn_to_cn_encoded.keys()))
)

# Encoding course_not_enrolled dengan sample skill
courses_not_enrolled = [[cn_to_cn_encoded.get(x)] for x in courses_not_enrolled]
courses_not_enrolled

# Encode course_sample
skills_encoder = skill_to_skill_encoded.get(course_sample)
if skills_encoder is None and isinstance(course_sample, np.int64):
  skills_encoder = course_sample
skills_courses_array = np.hstack(
    ([[skills_encoder]] * len(courses_not_enrolled), courses_not_enrolled)
)
skills_courses_array

# Prediksi model
ratings = model.predict(skills_courses_array).flatten()

"""# Model Evaluation

Content Based Filtering
"""

# Membuat fungsi prediction
course_columns = ['courseName','rating', 'skills']
def get_recommendations(title, similarity_data=cosine_sim_df, similar_type='cosine', items=courses[course_columns], k=10):

    # Mengambil data dengan similarity terbesar (cosine) dan terkecil (euclidean) dari index yang ada
    if (similar_type == 'cosine'):
        index = similarity_data.loc[:,title].to_numpy().argpartition(
        range(-1, -k, -1))
        closest = similarity_data.columns[index[-1:-(k+2):-1]]
        score = similarity_data.iloc[index[-1:-(k+2):-1],
                                     similarity_data.columns.get_loc(title)
                                    ].reset_index(drop=True)
    else:
        index = similarity_data.loc[:,title].to_numpy().argpartition(
        range(k+1))
        closest = similarity_data.columns[index[:(k+2)]]
        score = similarity_data.iloc[index[:(k+2)],
                                     similarity_data.columns.get_loc(title)
                                    ].reset_index(drop=True)

    # Drop courseName agar course yang dicari tidak muncul dalam daftar rekomendasi
    closest = closest.drop(title, errors='ignore')
    result = pd.DataFrame(closest).merge(items).head(k)
    result['rating'] = score
    return result

# Mengambil contoh course
courses.loc[courses.courseName.isin([
    'Software Security',
]), course_columns]

"""Cosine Similarity"""

print(get_recommendations('Software Security').to_markdown())

"""Euclidean Distance"""

print(get_recommendations('Software Security', euclidean_dist_df, 'euclidean').to_markdown())

"""Colaborative Filtering"""

fig, ax = plt.subplots(2, figsize=(16, 8))

mt = history.history['root_mean_squared_error']
mv = history.history['val_root_mean_squared_error']

ax[0].plot(mt)
ax[0].plot(mv)

for plot in ax.flat:
    plot.set(xlabel='rmse', ylabel='val-rmse')

plt.show()

top_ratings_indices = ratings.argsort()[-10:][::-1]
recommended_course_ids = [
    cn_encoded_to_cn.get(courses_not_enrolled[x][0]) for x in top_ratings_indices
]

print('Menampilkan rekomendasi course: {}'.format(course_sample))
print('===' * 9)
print('Menampilkan course dengan rating tinggi')
print('----' * 8)

top_course_by_rating = (
    courses_enrolled.sort_values(
        by = 'rating',
        ascending=False
    )
    .head(15)
    .rating.values
)

courses_rows = courses[courses['rating'].isin(top_course_by_rating)]
for row in courses_rows.itertuples():
    print(row.courseName)

print('----' * 8)
print('Top 10 rekomendasi course Coursera')
print('----' * 8)

recommended_courses = courses[courses['rating'].isin(recommended_course_ids)]
for row in recommended_courses.itertuples():
    print(row.courseName)