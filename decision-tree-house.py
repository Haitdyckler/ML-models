import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
from sklearn import tree

# Load the dataset
df = pd.read_csv('USA_Housing_Dataset.csv')

print("Dataset Shape:", df.shape)
print("\nFirst few rows:")
print(df.head())

# ============================================
# ADVANCED FEATURE ENGINEERING
# ============================================
print("\n" + "="*50)
print("ADVANCED FEATURE ENGINEERING")
print("="*50)

# Convert date
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['quarter'] = df['date'].dt.quarter
df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)

# Basic derived features
df['price_per_sqft'] = df['price'] / df['sqft_living']
df['total_rooms'] = df['bedrooms'] + df['bathrooms']
df['house_age'] = 2014 - df['yr_built']
df['years_since_renovation'] = np.where(df['yr_renovated'] > 0, 2014 - df['yr_renovated'], 0)
df['is_renovated'] = (df['yr_renovated'] > 0).astype(int)
df['has_basement'] = (df['sqft_basement'] > 0).astype(int)
df['basement_ratio'] = df['sqft_basement'] / df['sqft_living']
df['lot_to_living_ratio'] = df['sqft_lot'] / df['sqft_living']

# Advanced features - INTERACTION TERMS (key for decision trees!)
df['sqft_living_squared'] = df['sqft_living'] ** 2
df['sqft_living_cubed'] = df['sqft_living'] ** 3
df['sqft_living_log'] = np.log1p(df['sqft_living'])
df['bedrooms_bathrooms_interaction'] = df['bedrooms'] * df['bathrooms']
df['sqft_bedrooms_ratio'] = df['sqft_living'] / (df['bedrooms'] + 1)
df['sqft_bathrooms_ratio'] = df['sqft_living'] / (df['bathrooms'] + 1)
df['quality_score'] = df['view'] * df['condition'] * df['waterfront']
df['luxury_indicator'] = ((df['sqft_living'] > 3000) & (df['bathrooms'] > 3)).astype(int)
df['age_condition_interaction'] = df['house_age'] * df['condition']
df['size_view_interaction'] = df['sqft_living'] * df['view']

# Location-based features (very important!)
df['is_seattle'] = (df['city'] == 'Seattle').astype(int)
df['is_bellevue'] = (df['city'] == 'Bellevue').astype(int)
df['is_redmond'] = (df['city'] == 'Redmond').astype(int)

# Encode city by average price (target encoding - powerful!)
city_price_mean = df.groupby('city')['price'].mean().to_dict()
df['city_avg_price'] = df['city'].map(city_price_mean)

# Encode city by frequency
city_freq = df['city'].value_counts().to_dict()
df['city_freq'] = df['city'].map(city_freq)

# Binned features (decision trees love these!)
df['price_category'] = pd.qcut(df['sqft_living'], q=5, labels=False, duplicates='drop')
df['age_category'] = pd.cut(df['house_age'], bins=[0, 10, 30, 50, 120], labels=False)
df['lot_size_category'] = pd.qcut(df['sqft_lot'], q=4, labels=False, duplicates='drop')

print("Advanced features created:")
print(f"  - Polynomial features: sqft_living^2, sqft_living^3, log(sqft_living)")
print(f"  - Interaction terms: bedrooms*bathrooms, size*view, age*condition")
print(f"  - Location features: city_avg_price, is_seattle, is_bellevue")
print(f"  - Categorical bins: price_category, age_category, lot_size_category")

# Remove extreme outliers more aggressively
print(f"\nOriginal dataset size: {len(df)}")
df = df[
    (df['price'] > 100000) & 
    (df['price'] < df['price'].quantile(0.98)) &
    (df['sqft_living'] > 500) &
    (df['bedrooms'] > 0) &
    (df['bedrooms'] < 10)
]
print(f"After removing outliers: {len(df)}")

# Select target
target_col = 'price'
y = df[target_col]

# Select features
exclude_cols = [target_col, 'date', 'street', 'country', 'price_per_sqft', 
                'statezip', 'city', 'price_category']
feature_cols = [col for col in df.columns if col not in exclude_cols]
X = df[feature_cols].select_dtypes(include=[np.number])

print(f"\nFinal feature count: {X.shape[1]}")
print(f"Total samples: {len(X)}")

# Split data with stratification for better distribution
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTraining set: {X_train.shape[0]} samples")
print(f"Testing set: {X_test.shape[0]} samples")

# ============================================
# ENHANCED HYPERPARAMETER TUNING
# ============================================
print("\n" + "="*50)
print("ENHANCED HYPERPARAMETER TUNING")
print("="*50)

# More granular parameter grid
param_grid = {
    'max_depth': [12, 15, 18, 20, 25, 30],
    'min_samples_split': [20, 30, 40, 50, 60],
    'min_samples_leaf': [3, 5, 7, 10],
    'max_features': ['sqrt', 'log2', None],
    'min_impurity_decrease': [0.0, 0.0001, 0.001]
}

dt_base = DecisionTreeRegressor(random_state=42, splitter='best')

grid_search = GridSearchCV(
    estimator=dt_base,
    param_grid=param_grid,
    cv=5,
    scoring='r2',
    n_jobs=-1,
    verbose=1
)

print("Searching through parameter combinations...")
grid_search.fit(X_train, y_train)

print("\nBest parameters found:")
for param, value in grid_search.best_params_.items():
    print(f"  {param}: {value}")
print(f"\nBest cross-validation R² score: {grid_search.best_score_:.4f}")

# Best model
best_dt = grid_search.best_estimator_

# ============================================
# MODEL EVALUATION
# ============================================
print("\n" + "="*50)
print("OPTIMIZED DECISION TREE PERFORMANCE")
print("="*50)

y_pred_train = best_dt.predict(X_train)
y_pred_test = best_dt.predict(X_test)

train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_mae = mean_absolute_error(y_test, y_pred_test)

print(f"\nTraining Metrics:")
print(f"  R² Score: {train_r2:.4f}")
print(f"  RMSE: ${np.sqrt(mean_squared_error(y_train, y_pred_train)):,.2f}")
print(f"  MAE: ${mean_absolute_error(y_train, y_pred_train):,.2f}")

print(f"\nTesting Metrics:")
print(f"  R² Score: {test_r2:.4f}")
print(f"  RMSE: ${test_rmse:,.2f}")
print(f"  MAE: ${test_mae:,.2f}")
print(f"  Overfitting Gap: {train_r2 - test_r2:.4f}")

print(f"\nVariance Explained: {test_r2*100:.1f}%")
print(f"Variance Unexplained: {(1-test_r2)*100:.1f}%")

# Calculate percentage improvement from baseline
baseline_r2 = 0.5229
improvement = ((test_r2 - baseline_r2) / baseline_r2) * 100
print(f"\nImprovement from baseline (R²=0.5229): {improvement:+.1f}%")

# ============================================
# FEATURE IMPORTANCE ANALYSIS
# ============================================
print("\n" + "="*50)
print("TOP 20 MOST IMPORTANT FEATURES")
print("="*50)

feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': best_dt.feature_importances_
}).sort_values('Importance', ascending=False)

print(feature_importance.head(20).to_string(index=False))

# ============================================
# PREDICTION ACCURACY ANALYSIS
# ============================================
print("\n" + "="*50)
print("PREDICTION ACCURACY BREAKDOWN")
print("="*50)

residuals = y_test - y_pred_test
percent_errors = np.abs(residuals / y_test) * 100

print(f"Predictions within 10% of actual: {(percent_errors <= 10).sum()} ({(percent_errors <= 10).mean()*100:.1f}%)")
print(f"Predictions within 20% of actual: {(percent_errors <= 20).sum()} ({(percent_errors <= 20).mean()*100:.1f}%)")
print(f"Predictions within 30% of actual: {(percent_errors <= 30).sum()} ({(percent_errors <= 30).mean()*100:.1f}%)")

# ============================================
# VISUALIZATIONS
# ============================================
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# 1. Actual vs Predicted
axes[0, 0].scatter(y_test, y_pred_test, alpha=0.6, edgecolors='k', s=50)
axes[0, 0].plot([y_test.min(), y_test.max()], 
                [y_test.min(), y_test.max()], 
                'r--', lw=3, label='Perfect Prediction')
axes[0, 0].set_xlabel('Actual Price ($)', fontsize=12)
axes[0, 0].set_ylabel('Predicted Price ($)', fontsize=12)
axes[0, 0].set_title(f'Actual vs Predicted (R²={test_r2:.4f})', fontsize=14, fontweight='bold')
axes[0, 0].legend(fontsize=10)
axes[0, 0].grid(True, alpha=0.3)

# 2. Residual Plot
axes[0, 1].scatter(y_pred_test, residuals, alpha=0.6, edgecolors='k', s=50, color='coral')
axes[0, 1].axhline(y=0, color='r', linestyle='--', lw=3)
axes[0, 1].set_xlabel('Predicted Price ($)', fontsize=12)
axes[0, 1].set_ylabel('Residuals ($)', fontsize=12)
axes[0, 1].set_title('Residual Plot', fontsize=14, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)

# 3. Top 15 Feature Importance
top_features = feature_importance.head(15)
axes[0, 2].barh(range(len(top_features)), top_features['Importance'], color='steelblue')
axes[0, 2].set_yticks(range(len(top_features)))
axes[0, 2].set_yticklabels(top_features['Feature'], fontsize=9)
axes[0, 2].set_xlabel('Importance', fontsize=12)
axes[0, 2].set_title('Top 15 Feature Importances', fontsize=14, fontweight='bold')
axes[0, 2].invert_yaxis()

# 4. Error Distribution
axes[1, 0].hist(residuals, bins=50, edgecolor='black', alpha=0.7, color='lightblue')
axes[1, 0].set_xlabel('Prediction Error ($)', fontsize=12)
axes[1, 0].set_ylabel('Frequency', fontsize=12)
axes[1, 0].set_title('Distribution of Prediction Errors', fontsize=14, fontweight='bold')
axes[1, 0].axvline(x=0, color='r', linestyle='--', lw=3)
axes[1, 0].grid(True, alpha=0.3, axis='y')

# 5. Percentage Error Distribution
axes[1, 1].hist(percent_errors, bins=50, edgecolor='black', alpha=0.7, color='lightgreen')
axes[1, 1].set_xlabel('Percentage Error (%)', fontsize=12)
axes[1, 1].set_ylabel('Frequency', fontsize=12)
axes[1, 1].set_title('Percentage Error Distribution', fontsize=14, fontweight='bold')
axes[1, 1].axvline(x=20, color='r', linestyle='--', lw=2, label='20% threshold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3, axis='y')

# 6. Performance Metrics Comparison
metrics = ['R² Score', 'Train R²', 'Gap']
values = [test_r2, train_r2, train_r2 - test_r2]
colors_metrics = ['green', 'blue', 'orange']
bars = axes[1, 2].bar(metrics, values, color=colors_metrics, alpha=0.7, edgecolor='black', width=0.6)
axes[1, 2].set_ylabel('Score', fontsize=12)
axes[1, 2].set_title('Model Performance Metrics', fontsize=14, fontweight='bold')
axes[1, 2].set_ylim([0, 1])
axes[1, 2].grid(True, alpha=0.3, axis='y')
for i, v in enumerate(values):
    axes[1, 2].text(i, v + 0.02, f'{v:.3f}', ha='center', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.show()

# ============================================
# SAMPLE PREDICTIONS
# ============================================
print("\n" + "="*50)
print("SAMPLE PREDICTIONS")
print("="*50)

sample_indices = [0, 10, 50, 100, 200]
for idx in sample_indices:
    if idx < len(X_test):
        sample = X_test.iloc[idx:idx+1]
        prediction = best_dt.predict(sample)[0]
        actual = y_test.iloc[idx]
        error = prediction - actual
        pct_error = (error / actual) * 100
        
        print(f"\nSample {idx+1}:")
        print(f"  Actual Price: ${actual:,.2f}")
        print(f"  Predicted Price: ${prediction:,.2f}")
        print(f"  Error: ${error:,.2f} ({pct_error:+.1f}%)")

# ============================================
# DECISION TREE VISUALIZATION
# ============================================
print("\n" + "="*50)
print("DECISION TREE VISUALIZATION (First 3 Levels)")
print("="*50)

plt.figure(figsize=(25, 15))
tree.plot_tree(
    best_dt, 
    feature_names=X.columns.tolist(), 
    filled=True,
    rounded=True,
    max_depth=3,  # Show first 3 levels
    fontsize=10,
    proportion=True,
    precision=0,
    impurity=False
)
plt.title("Decision Tree Structure (First 3 Levels)", fontsize=20, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()

print("\nTree visualization displayed!")
print(f"Full tree has {best_dt.get_depth()} levels and {best_dt.get_n_leaves()} leaf nodes")
print("\nHow to read the tree:")
print("  • Each box represents a decision node")
print("  • Top line shows the splitting rule (e.g., 'sqft_living <= 2500')")
print("  • 'samples' shows percentage of data in that node")
print("  • 'value' shows the predicted price for that node")
print("  • Color intensity indicates prediction value (darker = higher price)")

# ============================================
# FINAL INSIGHTS
# ============================================
print("\n" + "="*50)
print("FINAL INSIGHTS & ANALYSIS")
print("="*50)

print(f"""
✓ ACHIEVED R² SCORE: {test_r2:.4f}
  → Explains {test_r2*100:.1f}% of house price variance
  → Improvement from baseline: {improvement:+.1f}%

✓ TOP 5 PREDICTIVE FEATURES:
  1. {feature_importance.iloc[0]['Feature']} ({feature_importance.iloc[0]['Importance']:.3f})
  2. {feature_importance.iloc[1]['Feature']} ({feature_importance.iloc[1]['Importance']:.3f})
  3. {feature_importance.iloc[2]['Feature']} ({feature_importance.iloc[2]['Importance']:.3f})
  4. {feature_importance.iloc[3]['Feature']} ({feature_importance.iloc[3]['Importance']:.3f})
  5. {feature_importance.iloc[4]['Feature']} ({feature_importance.iloc[4]['Importance']:.3f})

✓ PREDICTION ACCURACY:
  → Within 20% accuracy: {(percent_errors <= 20).mean()*100:.1f}% of predictions
  → Average absolute error: ${test_mae:,.0f}
  → Root mean squared error: ${test_rmse:,.0f}

✓ MODEL CHARACTERISTICS:
  → Tree depth: {best_dt.get_depth()} levels
  → Number of leaves: {best_dt.get_n_leaves()}
  → Number of features used: {(best_dt.feature_importances_ > 0).sum()}/{len(X.columns)}
""")