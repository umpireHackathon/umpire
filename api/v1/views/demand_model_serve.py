import pandas as pd
import joblib

# Load model and feature structure
model = joblib.load("rf_demand_model.joblib")
feature_columns = joblib.load("rf_demand_columns.joblib")
day_categories = joblib.load("day_categories.joblib")

# Example user input
input_dict = {"agency_id": 23, "day_name": "monday"}
df_input = pd.DataFrame([input_dict])

# Ensure categorical day ordering
df_input['day_name'] = pd.Categorical(df_input['day_name'], categories=day_categories, ordered=True)

# One-hot encode
df_input = pd.get_dummies(df_input, columns=['day_name'])

# Ensure all expected columns are present
for col in feature_columns:
    if col not in df_input.columns:
        df_input[col] = 0

# Reorder
df_input = df_input[feature_columns]

# Predict
pred = model.predict(df_input)[0]
print(f"Predicted number of trips: {pred:.0f}")
