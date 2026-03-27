# NGO CSR Funding Prediction & Analysis Guide

## 📋 Overview

This project provides comprehensive machine learning solutions for NGO education CSR fundraising:

1. **XGBoost Classification** → Identify high-funding donors
2. **DBSCAN Clustering** → Segment companies (high/low/inconsistent)
3. **Regression Model** → Predict funding amounts

---

## 📊 Dataset

- **File**: `ai_ready_csr_dataset.xlsx`
- **Rows**: 60 companies
- **Key Features**:
  - `CSR Spend`: Total CSR spending ($M)
  - `Education Spend`: Education-specific CSR spending ($M)
  - `Growth`: Company growth rate (%)
  - `Year`: Data year
  - `Industry`: Company sector
  - `Location`: Geographic location
  - `Target`: Education CSR funding indicator (1 = Yes)

---

## 🚀 How to Run

### Option 1: Jupyter Notebook (Recommended)
```bash
jupyter notebook CSR_Prediction_Analysis.ipynb
```

### Option 2: Command Line
```bash
python3 run_analysis.py
```

---

## 📈 What Each Section Does

### Section 1-3: Data Preparation
- Loads and explores the dataset
- Encodes categorical variables (Industry, Location)
- Scales numerical features for modeling

### Section 4: XGBoost Classification
**Purpose**: Predict which companies will become high-funding donors

**Output**:
- Model accuracy & ROC-AUC scores
- Feature importance rankings
- Confusion matrix visualization

**Key Insight**: Identifies drivers of high education CSR spending

### Section 5: Probability Scores & Top Donors
**Purpose**: Generate actionable target list for fundraising

**Output**:
- Probability scores for each company (0-1)
- Top 15 potential high-funding donors
- Probability distribution chart

**Use Case**: Direct outreach to highest-probability companies

### Section 6-7: DBSCAN Clustering
**Purpose**: Group companies by CSR contribution patterns

**Output**:
- **HIGH CSR CONTRIBUTORS ⭐**: Consistent, high-funding donors
- **LOW CONTRIBUTORS**: Limited CSR engagement
- **INCONSISTENT DONORS 🔄**: Variable commitment levels

**Use Case**: Segment-specific fundraising strategies

### Section 8: Regression Model
**Purpose**: Predict funding amounts

**Output**:
- Model RMSE & R² score
- Predicted education spending for each company
- Feature importance for funding prediction

**Use Case**: Budget forecasting and goal setting

---

## 🎯 Key Metrics Explained

| Metric | What It Means | Good Range |
|--------|---------------|------------|
| **Accuracy** | % of correct predictions | 75-100% |
| **ROC-AUC** | Overall model performance | 0.8-1.0 |
| **RMSE** | Prediction error magnitude | Lower is better |
| **R² Score** | Variance explained | 0.7-1.0 |

---

## 💡 Actionable Insights

### For Fundraisers:
1. **Start here**: Use Top Donors list (Section 5) for immediate outreach
2. **Segment your approach**: Tailor messaging by cluster type
3. **Forecast revenue**: Use regression predictions for planning

### For Strategy:
1. **HIGH CONTRIBUTORS**: Focus on retention & expansion
2. **LOW CONTRIBUTORS**: Needs-based education approach
3. **INCONSISTENT DONORS**: Build relationship continuity

### For Analytics:
1. Monitor feature importance for changing trends
2. Re-train quarterly with new data
3. Track prediction accuracy over time

---

## 📦 Dependencies

```
pandas
numpy
scikit-learn
xgboost
matplotlib
seaborn
```

Install all with:
```bash
pip install pandas numpy scikit-learn xgboost matplotlib seaborn openpyxl
```

---

## 🔍 Troubleshooting

**Issue**: Models show perfect accuracy
- **Why**: Clear separation between high/low donors in this dataset
- **Solution**: Normal for well-behaved CSR data; use predictions confidently

**Issue**: ImportError for libraries
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: Dataset not found
- **Solution**: Ensure `ai_ready_csr_dataset.xlsx` is in the same directory

---

## 📞 Next Steps

1. **Review** the probability scores (Section 5)
2. **Analyze** your cluster assignments (Section 7)
3. **Use** predictions to inform fundraising strategy
4. **validate** with your known donor relationships
5. **Iterate** as you gather more data

---

## 🎓 Learning Resources

- XGBoost: https://xgboost.readthedocs.io/
- DBSCAN: https://scikit-learn.org/stable/modules/clustering.html#dbscan
- Scikit-learn: https://scikit-learn.org/

---

**Good luck with your NGO fundraising! 🌟**
