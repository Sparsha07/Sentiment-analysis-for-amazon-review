# -*- coding: utf-8 -*-
"""Sentiment analysis for amazon review.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mfgAY-OsyA12Mlji4WVMjNT5kdOhzWWX
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('ggplot')
import nltk
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('maxent_ne_chunker_tab')
nltk.download('words')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('vader_lexicon')

dfs = pd.read_csv('/content/Reviews.csv')

dfs.head()

dfs['Text'].values[1]

dfs.shape

#EDA
ax=dfs['Score'].value_counts().sort_index().plot(kind='bar', title='Count of Reviews by Stars', figsize=(10,5))
ax.set_xlabel('Review Stars')
plt.show()

ex =dfs['Text'].values[50]
print(ex)

tokens=nltk.word_tokenize(ex)
tokens[:10]

tagged = nltk.pos_tag(tokens)
tagged[:10]

entities=nltk.chunk.ne_chunk(tagged)
entities.pprint()

from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm
sia = SentimentIntensityAnalyzer()

sia.polarity_scores('I am so not sad')

sia.polarity_scores('I am so happy')

sia.polarity_scores(ex)

from tqdm import tqdm

# Ensure 'Text' column has valid strings
dfs['Text'] = dfs['Text'].fillna('').astype(str)

# Initialize results dictionary
results = {}

# Iterate through DataFrame rows with progress bar
for i, row in tqdm(dfs.iterrows(), total=len(dfs)):
    try:
        text = row['Text']
        myid = row['Id']

        # Compute VADER sentiment scores
        results[myid] = sia.polarity_scores(text)
    except Exception as e:
        print(f"Error processing row with Id {row['Id']}: {e}")

results

f = pd.DataFrame(results)
print(f)

# Create the df DataFrame with sentiment scores as columns
vaders = pd.DataFrame(results).T  # Transpose to have sentiment scores as columns
vaders = vaders.reset_index().rename(columns={'index': 'Id'})  # Rename index column to 'Id'

# Ensure both 'Id' columns are the same data type
dfs['Id'] = dfs['Id'].astype(str)
vaders['Id'] = vaders['Id'].astype(str)

# Now, merge the two DataFrames on the 'Id' column
vaders = vaders.merge(dfs, how='left', on='Id')  # Use 'on' to specify the column to merge on

# Verify the result
print(vaders.head())

sns.barplot (data=vaders,x='Score',y='compound')
ax.set_xlabel('Review Stars')
plt.show()

ax=sns.barplot (data=vaders,x='Score',y='compound')
ax.set_xlabel('compound score by amazon star review')
plt.show()

# Ensure columns exist and have no missing values
required_columns = ['Score', 'pos', 'neu', 'neg']
vaders = vaders.dropna(subset=required_columns)

# Initialize subplots
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

# Plot the data
sns.barplot(data=vaders, x='Score', y='pos', ax=axs[0])
sns.barplot(data=vaders, x='Score', y='neu', ax=axs[1])
sns.barplot(data=vaders, x='Score', y='neg', ax=axs[2])

# Add titles
axs[0].set_title('Positive')
axs[1].set_title('Neutral')
axs[2].set_title('Negative')

# Adjust layout and show plot
plt.tight_layout()
plt.show()

from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax

MODEL=f'cardiffnlp/twitter-roberta-base-sentiment'
tokenizer=AutoTokenizer.from_pretrained(MODEL)
model=AutoModelForSequenceClassification.from_pretrained(MODEL)

print(ex)
sia.polarity_scores(ex)

encoded_text=tokenizer(ex,return_tensors='pt')
output = model(**encoded_text)
scores=output[0][0].detach().numpy()
scores=softmax(scores)
scores_dict={
    'roberta_neg':scores[0],
    'roberta_neu':scores[1],
    'roberta_pos':scores[2]
}
print(scores_dict)

def polarity_scores_roberta(example):
    encoded_text=tokenizer(example,return_tensors='pt')
    output = model(**encoded_text)

from tqdm import tqdm

# Initialize an empty dictionary to store the results
results = {}

# Iterate through the DataFrame rows
for i, row in tqdm(dfs.iterrows(), total=len(dfs)):
    try:
        # Extract text and ID
        text = row['Text']
        myid = row['Id']

        # Compute VADER sentiment scores
        vader_result = sia.polarity_scores(text)
        vader_result_rename = {f"vader_{key}": value for key, value in vader_result.items()}

        # Compute RoBERTa sentiment scores
        roberta_result = polarity_scores_roberta(text)

        # Validate RoBERTa result
        if not isinstance(roberta_result, dict):
            roberta_result = {}  # Fallback to empty dictionary

        # Combine VADER and RoBERTa results into a single dictionary
        combined_result = {**vader_result_rename, **roberta_result}

        # Store the combined result in the results dictionary
        results[myid] = combined_result

    # Handle runtime errors
    except RuntimeError as e:
        print(f"Error processing row with Id {myid}: {e}")

results_df = pd.DataFrame(results).T
results_df = results_df.reset_index().rename(columns={'index': 'Id'})
results_df = results_df.merge(dfs, how='left', on='Id')

results_df.head()

results_df.columns

sns.pairplot(data=results_df,
             vars=['vader_neg', 'vader_neu', 'vader_pos',
                  'roberta_neg', 'roberta_neu', 'roberta_pos'],
            hue='Score',
            palette='tab10')
plt.show()

results_df.query('Score == 1') \
    .sort_values('roberta_pos', ascending=False)['Text'].values[0]

results_df.query('Score == 1') \
    .sort_values('vader_pos', ascending=False)['Text'].values[0]

results_df.query('Score == 5') \
    .sort_values('roberta_neg', ascending=False)['Text'].values[0]

from transformers import pipeline

sent_pipeline = pipeline("sentiment-analysis")

sent_pipeline('I love sentiment analysis!')

sent_pipeline('Make sure to like and subscribe!')

sent_pipeline('booo')