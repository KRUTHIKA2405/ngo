import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve, accuracy_score
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.calibration import calibration_curve

import xgboost as xgb

# Set random seed for reproducibility
np.random.seed(42)

# Create visualizations directory
import os
os.makedirs('visualizations', exist_ok=True)

print("✅ All libraries imported successfully!")

# Load the dataset
df = pd.read_excel('ai_ready_csr_dataset.xlsx')

print("📊 Dataset Loaded Successfully!")
print(f"Shape: {df.shape}")

# Create a copy for processing
df_processed = df.copy()

# Encode categorical variables
le_industry = LabelEncoder()
le_location = LabelEncoder()

df_processed['Industry_Encoded'] = le_industry.fit_transform(df_processed['Industry'])
df_processed['Location_Encoded'] = le_location.fit_transform(df_processed['Location'])

# Prepare features for modeling
X = df_processed[['CSR Spend', 'Education Spend', 'Growth', 'Year', 'Industry_Encoded', 'Location_Encoded']]
y = df_processed['Target']

# Feature scaling
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# Create a binary target: High Education Funding (top quartile) vs Normal/Low
education_spending_threshold = df_processed['Education Spend'].quantile(0.75)
y_classification = (df_processed['Education Spend'] >= education_spending_threshold).astype(int)

# Split data into training and testing sets (80-20 split)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_classification, test_size=0.2, random_state=42, stratify=y_classification)

# Train XGBoost Classifier
xgb_model = xgb.XGBClassifier(
    objective='binary:logistic',
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42,
    eval_metric='logloss'
)

xgb_model.fit(X_train, y_train, verbose=False)

# Make predictions
y_pred_train = xgb_model.predict(X_train)
y_pred_test = xgb_model.predict(X_test)
y_pred_proba = xgb_model.predict_proba(X_test)[:, 1]

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred_test)

# Feature Importance
feature_importance = pd.DataFrame({
    'Feature': X_scaled.columns,
    'Importance': xgb_model.feature_importances_
}).sort_values('Importance', ascending=False)

# Plot Confusion Matrix and Feature Importance
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Confusion Matrix
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0])
axes[0].set_title('Confusion Matrix - XGBoost', fontsize=12, fontweight='bold')
axes[0].set_ylabel('True Label')
axes[0].set_xlabel('Predicted Label')

# Feature Importance
axes[1].barh(feature_importance['Feature'], feature_importance['Importance'], color='steelblue')
axes[1].set_title('Feature Importance - XGBoost', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Importance Score')

plt.tight_layout()
plt.savefig('visualizations/xgboost_classification.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ XGBoost Classification visualization saved!")

# Get probability scores for all companies
X_all_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
y_classification_all = (df_processed['Education Spend'] >= education_spending_threshold).astype(int)
prob_scores = xgb_model.predict_proba(X_all_scaled)[:, 1]

# Create results dataframe
results_df = df[['Company', 'Industry', 'CSR Spend', 'Education Spend', 'Growth']].copy()
results_df['High_Funding_Probability'] = prob_scores
results_df['Prediction'] = xgb_model.predict(X_all_scaled)
results_df = results_df.sort_values('High_Funding_Probability', ascending=False)

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Bar plot of top 15 donors
top_15 = results_df.head(15)
axes[0].barh(range(len(top_15)), top_15['High_Funding_Probability'], color='darkgreen', alpha=0.7)
axes[0].set_yticks(range(len(top_15)))
axes[0].set_yticklabels(top_15['Company'])
axes[0].set_xlabel('High Education CSR Funding Probability', fontsize=11, fontweight='bold')
axes[0].set_title('Top 15 Potential High-Funding Education CSR Donors', fontsize=12, fontweight='bold')
axes[0].axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='Threshold (0.5)')
axes[0].legend()
axes[0].invert_yaxis()

# Distribution of probability scores
axes[1].hist(results_df['High_Funding_Probability'], bins=20, color='steelblue', alpha=0.7, edgecolor='black')
axes[1].axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='Threshold (0.5)')
axes[1].set_xlabel('Probability Score', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Number of Companies', fontsize=11, fontweight='bold')
axes[1].set_title('Distribution of High Education CSR Funding Probability', fontsize=12, fontweight='bold')
axes[1].legend()

plt.tight_layout()
plt.savefig('visualizations/donor_probability_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ Donor probability analysis visualization saved!")

# Apply DBSCAN clustering
X_clustering = df_processed[['CSR Spend', 'Education Spend', 'Growth']].copy()
X_clustering_scaled = scaler.fit_transform(X_clustering)

# DBSCAN with eps=0.5, min_samples=2
dbscan = DBSCAN(eps=0.5, min_samples=2)
clusters = dbscan.fit_predict(X_clustering_scaled)

n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
n_noise = list(clusters).count(-1)

# Add clusters to dataframe
df_clustering = df_processed[['Company', 'Industry', 'CSR Spend', 'Education Spend', 'Growth']].copy()
df_clustering['Cluster'] = clusters
df_clustering['Probability'] = prob_scores

# Visualize clusters using PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_clustering_scaled)

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# PCA Visualization
colors = plt.cm.Set3(np.linspace(0, 1, n_clusters + 1))
noise_color = 'red'

for cluster_id in sorted(set(clusters)):
    if cluster_id == -1:
        # Noise/outliers
        mask = clusters == cluster_id
        axes[0].scatter(X_pca[mask, 0], X_pca[mask, 1], c='red', marker='x', s=200, 
                       label=f'Noise (Outliers)', alpha=0.8, linewidths=2)
    else:
        mask = clusters == cluster_id
        axes[0].scatter(X_pca[mask, 0], X_pca[mask, 1], c=[colors[cluster_id]], 
                       label=f'Cluster {cluster_id}', s=100, alpha=0.7, edgecolors='black')

axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)', fontsize=11, fontweight='bold')
axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)', fontsize=11, fontweight='bold')
axes[0].set_title('DBSCAN Clusters - PCA Visualization', fontsize=12, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Color by probability score
scatter = axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=prob_scores, cmap='RdYlGn', 
                         s=100, alpha=0.7, edgecolors='black')
axes[1].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)', fontsize=11, fontweight='bold')
axes[1].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)', fontsize=11, fontweight='bold')
axes[1].set_title('Companies Colored by Education CSR Probability', fontsize=12, fontweight='bold')
cbar = plt.colorbar(scatter, ax=axes[1])
cbar.set_label('Probability Score', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/dbscan_clustering.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ DBSCAN clustering visualization saved!")

# Use Education Spend as the target for regression
X_reg = X_scaled.copy()
y_reg = df_processed['Education Spend'].copy()

# Split data
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)

# Train XGBoost Regression model
xgb_regressor = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)

xgb_regressor.fit(X_train_reg, y_train_reg, verbose=False)

# Make predictions
y_pred_train_reg = xgb_regressor.predict(X_train_reg)
y_pred_test_reg = xgb_regressor.predict(X_test_reg)

# Feature importance for regression
feature_importance_reg = pd.DataFrame({
    'Feature': X_scaled.columns,
    'Importance': xgb_regressor.feature_importances_
}).sort_values('Importance', ascending=False)

# Predict education spending for all companies
y_pred_all = xgb_regressor.predict(X_all_scaled)

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Actual vs Predicted
axes[0, 0].scatter(y_test_reg, y_pred_test_reg, alpha=0.6, color='steelblue', edgecolors='black')
axes[0, 0].plot([y_test_reg.min(), y_test_reg.max()], [y_test_reg.min(), y_test_reg.max()], 'r--', lw=2)
axes[0, 0].set_xlabel('Actual Education Spend ($M)', fontsize=11, fontweight='bold')
axes[0, 0].set_ylabel('Predicted Education Spend ($M)', fontsize=11, fontweight='bold')
axes[0, 0].set_title('Actual vs Predicted Education Spending', fontsize=12, fontweight='bold')
axes[0, 0].grid(True, alpha=0.3)

# Residuals
residuals = y_test_reg - y_pred_test_reg
axes[0, 1].scatter(y_pred_test_reg, residuals, alpha=0.6, color='coral', edgecolors='black')
axes[0, 1].axhline(y=0, color='r', linestyle='--', lw=2)
axes[0, 1].set_xlabel('Predicted Values ($M)', fontsize=11, fontweight='bold')
axes[0, 1].set_ylabel('Residuals ($M)', fontsize=11, fontweight='bold')
axes[0, 1].set_title('Residual Plot', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)

# Feature Importance
axes[1, 0].barh(feature_importance_reg['Feature'], feature_importance_reg['Importance'], color='darkgreen', alpha=0.7)
axes[1, 0].set_title('Feature Importance - Regression Model', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('Importance Score')

# Distribution of predictions
axes[1, 1].hist(y_pred_all, bins=15, color='purple', alpha=0.7, edgecolor='black', label='Predicted')
axes[1, 1].hist(df['Education Spend'], bins=15, color='orange', alpha=0.5, edgecolor='black', label='Actual')
axes[1, 1].set_xlabel('Education Spending ($M)', fontsize=11, fontweight='bold')
axes[1, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
axes[1, 1].set_title('Distribution: Actual vs Predicted Education Spending', fontsize=12, fontweight='bold')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('visualizations/regression_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ Regression analysis visualization saved!")

# ROC Curve & Model Performance Metrics
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1. ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, xgb_model.predict_proba(X_test)[:, 1])
roc_auc = roc_auc_score(y_test, xgb_model.predict_proba(X_test)[:, 1])

axes[0, 0].plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC Curve (AUC = {roc_auc:.2f})')
axes[0, 0].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
axes[0, 0].set_xlabel('False Positive Rate', fontsize=11, fontweight='bold')
axes[0, 0].set_ylabel('True Positive Rate', fontsize=11, fontweight='bold')
axes[0, 0].set_title('ROC Curve - XGBoost Classifier', fontsize=12, fontweight='bold')
axes[0, 0].legend(loc='lower right', fontsize=10)
axes[0, 0].grid(True, alpha=0.3)

# 2. Probability Distribution by Class
high_funding_probs = prob_scores[y_classification_all == 1]
low_funding_probs = prob_scores[y_classification_all == 0]

axes[0, 1].hist(low_funding_probs, bins=15, alpha=0.6, label='Low Funding (0)', color='coral', edgecolor='black')
axes[0, 1].hist(high_funding_probs, bins=15, alpha=0.6, label='High Funding (1)', color='green', edgecolor='black')
axes[0, 1].set_xlabel('Probability Score', fontsize=11, fontweight='bold')
axes[0, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
axes[0, 1].set_title('Probability Distribution by Funding Class', fontsize=12, fontweight='bold')
axes[0, 1].legend(fontsize=10)
axes[0, 1].axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='Decision Threshold')
axes[0, 1].grid(True, alpha=0.3, axis='y')

# 3. Calibration Curve (Reliability Diagram)
prob_true, prob_pred = calibration_curve(y_test, xgb_model.predict_proba(X_test)[:, 1], n_bins=5)

axes[1, 0].plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfectly Calibrated')
axes[1, 0].plot(prob_pred, prob_true, marker='o', linewidth=2, markersize=8, color='steelblue', label='XGBoost')
axes[1, 0].set_xlabel('Mean Predicted Probability', fontsize=11, fontweight='bold')
axes[1, 0].set_ylabel('Fraction of Positives', fontsize=11, fontweight='bold')
axes[1, 0].set_title('Calibration Curve - Model Reliability', fontsize=12, fontweight='bold')
axes[1, 0].legend(fontsize=10)
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].set_xlim([0, 1])
axes[1, 0].set_ylim([0, 1])

# 4. Learning Curve (Training vs Validation Performance)
train_sizes = [0.2, 0.4, 0.6, 0.8, 0.9]
train_scores = []
val_scores = []

for size in train_sizes:
    X_temp, _, y_temp, _ = train_test_split(X_train, y_train, train_size=size, random_state=42)
    temp_model = xgb.XGBClassifier(objective='binary:logistic', n_estimators=50, 
                                   max_depth=5, learning_rate=0.1, random_state=42, eval_metric='logloss')
    temp_model.fit(X_temp, y_temp, verbose=False)
    train_scores.append(accuracy_score(y_temp, temp_model.predict(X_temp)))
    val_scores.append(accuracy_score(y_test, temp_model.predict(X_test)))

axes[1, 1].plot(train_sizes, train_scores, marker='o', linewidth=2, markersize=8, label='Training Accuracy', color='green')
axes[1, 1].plot(train_sizes, val_scores, marker='s', linewidth=2, markersize=8, label='Validation Accuracy', color='orange')
axes[1, 1].set_xlabel('Training Set Fraction', fontsize=11, fontweight='bold')
axes[1, 1].set_ylabel('Accuracy Score', fontsize=11, fontweight='bold')
axes[1, 1].set_title('Learning Curve - Model Generalization', fontsize=12, fontweight='bold')
axes[1, 1].legend(fontsize=10)
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_ylim([0, 1.05])

plt.tight_layout()
plt.savefig('visualizations/model_performance_metrics.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ Model performance metrics visualization saved!")

# Additional visualizations from later cells

# 3D Scatter Plot for Clustering
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Color by cluster
for cluster_id in sorted(set(clusters)):
    mask = clusters == cluster_id
    if cluster_id == -1:
        ax.scatter(X_clustering_scaled[mask, 0], X_clustering_scaled[mask, 1], X_clustering_scaled[mask, 2], 
                  c='red', marker='x', s=100, label='Noise', alpha=0.8)
    else:
        ax.scatter(X_clustering_scaled[mask, 0], X_clustering_scaled[mask, 1], X_clustering_scaled[mask, 2], 
                  c=[colors[cluster_id]], s=100, label=f'Cluster {cluster_id}', alpha=0.7)

ax.set_xlabel('CSR Spend (scaled)', fontsize=10, fontweight='bold')
ax.set_ylabel('Education Spend (scaled)', fontsize=10, fontweight='bold')
ax.set_zlabel('Growth (scaled)', fontsize=10, fontweight='bold')
ax.set_title('3D Clustering Visualization - DBSCAN', fontsize=12, fontweight='bold')
ax.legend()

plt.savefig('visualizations/3d_clustering.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ 3D clustering visualization saved!")

# Box plots for cluster comparison
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

features_to_plot = ['CSR Spend', 'Education Spend', 'Growth']
titles = ['CSR Spend by Cluster', 'Education Spend by Cluster', 'Growth by Cluster']

for i, (feature, title) in enumerate(zip(features_to_plot, titles)):
    cluster_data = []
    cluster_labels = []
    
    for cluster_id in sorted(set(clusters)):
        mask = clusters == cluster_id
        if cluster_id == -1:
            cluster_data.append(df_clustering[mask][feature])
            cluster_labels.append('Noise')
        else:
            cluster_data.append(df_clustering[mask][feature])
            cluster_labels.append(f'Cluster {cluster_id}')
    
    axes[i].boxplot(cluster_data, labels=cluster_labels)
    axes[i].set_title(title, fontsize=12, fontweight='bold')
    axes[i].set_ylabel(feature + (' (%)' if feature == 'Growth' else ' ($M)'), fontsize=11, fontweight='bold')
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/cluster_boxplots.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ Cluster boxplots visualization saved!")

# Heatmap of correlations
correlation_matrix = df_processed[['CSR Spend', 'Education Spend', 'Growth', 'Year', 'Industry_Encoded', 'Location_Encoded']].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
plt.title('Feature Correlation Heatmap', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

plt.savefig('visualizations/correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ Correlation heatmap visualization saved!")

print("\n🎉 All visualizations have been generated and saved in the 'visualizations/' folder!")
print("You can now view the PNG files directly in your file explorer or image viewer.")