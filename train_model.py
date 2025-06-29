import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
import pickle
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data():
    """
    Load and prepare the heart disease dataset
    """
    try:
        # Load the data
        data_path = "../data/heart.csv"
        df = pd.read_csv(data_path)
        
        print(f"Dataset loaded successfully!")
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for missing values
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            print(f"Warning: Missing values found:\n{missing_values[missing_values > 0]}")
        else:
            print("No missing values found in the dataset.")
        
        # Check class distribution
        class_dist = df['target'].value_counts()
        print(f"\nClass distribution:")
        print(f"Positive cases (Heart Disease): {class_dist[1]} ({class_dist[1]/len(df)*100:.1f}%)")
        print(f"Negative cases (No Disease): {class_dist[0]} ({class_dist[0]/len(df)*100:.1f}%)")
        
        # Define features and target
        feature_columns = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", 
                          "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
        target_column = "target"
        
        X = df[feature_columns]
        y = df[target_column]
        
        print(f"\nFeatures shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        
        return X, y, feature_columns
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None, None, None

def evaluate_model(model, X_test, y_test, model_name):
    """
    Evaluate a model and return metrics
    """
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\n{model_name} Results:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    
    return {
        'model_name': model_name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'model': model
    }

def find_best_model(X, y):
    """
    Train and compare multiple models to find the best one
    """
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}")
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define models to test
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42),
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'SVM': SVC(random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'K-Nearest Neighbors': KNeighborsClassifier()
    }
    
    results = []
    
    print("\n" + "="*60)
    print("MODEL COMPARISON")
    print("="*60)
    
    # Train and evaluate each model
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Train the model
        model.fit(X_train_scaled, y_train)
        
        # Evaluate the model
        result = evaluate_model(model, X_test_scaled, y_test, name)
        results.append(result)
    
    # Find the best model based on F1-score (balanced metric)
    best_result = max(results, key=lambda x: x['f1_score'])
    
    print("\n" + "="*60)
    print("BEST MODEL SELECTION")
    print("="*60)
    print(f"Best model: {best_result['model_name']}")
    print(f"Best F1-Score: {best_result['f1_score']:.4f}")
    print(f"Best Accuracy: {best_result['accuracy']:.4f}")
    
    return best_result['model'], scaler, results

def hyperparameter_tuning(X, y, best_model_name):
    """
    Perform hyperparameter tuning for the best model
    """
    print(f"\n" + "="*60)
    print(f"HYPERPARAMETER TUNING FOR {best_model_name.upper()}")
    print("="*60)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create pipeline with scaler and model
    if best_model_name == 'Random Forest':
        model = RandomForestClassifier(random_state=42)
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
    elif best_model_name == 'Gradient Boosting':
        model = GradientBoostingClassifier(random_state=42)
        param_grid = {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'min_samples_split': [2, 5, 10]
        }
    elif best_model_name == 'Logistic Regression':
        model = LogisticRegression(random_state=42, max_iter=1000)
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear', 'saga']
        }
    elif best_model_name == 'SVM':
        model = SVC(random_state=42)
        param_grid = {
            'C': [0.1, 1, 10],
            'kernel': ['rbf', 'linear'],
            'gamma': ['scale', 'auto', 0.1, 0.01]
        }
    else:
        print(f"Hyperparameter tuning not implemented for {best_model_name}")
        return None, None
    
    # Create pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', model)
    ])
    
    # Grid search with cross-validation
    grid_search = GridSearchCV(
        pipeline, 
        param_grid, 
        cv=5, 
        scoring='f1',
        n_jobs=-1,
        verbose=1
    )
    
    # Fit the grid search
    grid_search.fit(X_train, y_train)
    
    # Get best model
    best_model = grid_search.best_estimator_
    best_params = grid_search.best_params_
    
    print(f"\nBest parameters: {best_params}")
    print(f"Best cross-validation F1-score: {grid_search.best_score_:.4f}")
    
    # Evaluate on test set
    y_pred = best_model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    test_f1 = f1_score(y_test, y_pred)
    
    print(f"Test set accuracy: {test_accuracy:.4f}")
    print(f"Test set F1-score: {test_f1:.4f}")
    
    return best_model, grid_search.best_score_

def save_model_and_scaler(model, scaler, model_name):
    """
    Save the trained model and scaler
    """
    try:
        # Save the model
        model_path = f"heart_rf_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"Model saved to: {model_path}")
        
        # Save the scaler
        scaler_path = "scaler.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        print(f"Scaler saved to: {scaler_path}")
        
        return True
        
    except Exception as e:
        print(f"Error saving model: {str(e)}")
        return False

def main():
    """
    Main function to train the heart disease prediction model
    """
    print("="*60)
    print("HEART DISEASE PREDICTION MODEL TRAINING")
    print("="*60)
    
    # Load and prepare data
    X, y, feature_columns = load_and_prepare_data()
    
    if X is None:
        print("Failed to load data. Exiting...")
        return
    
    # Find the best model
    best_model, scaler, all_results = find_best_model(X, y)
    
    # Perform hyperparameter tuning
    best_model_name = "Random Forest"  # Default, will be updated based on results
    for result in all_results:
        if result['model'] == best_model:
            best_model_name = result['model_name']
            break
    
    tuned_model, cv_score = hyperparameter_tuning(X, y, best_model_name)
    
    # Use tuned model if available, otherwise use the best from initial comparison
    final_model = tuned_model if tuned_model is not None else best_model
    
    # Save the model and scaler
    success = save_model_and_scaler(final_model, scaler, best_model_name)
    
    if success:
        print("\n" + "="*60)
        print("TRAINING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Best model: {best_model_name}")
        print(f"Cross-validation F1-score: {cv_score:.4f}" if cv_score else "N/A")
        print("Model and scaler saved successfully!")
        
        # Final evaluation on a fresh split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        X_test_scaled = scaler.transform(X_test)
        y_pred = final_model.predict(X_test_scaled)
        
        print(f"\nFinal Model Performance:")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"Precision: {precision_score(y_test, y_pred):.4f}")
        print(f"Recall: {recall_score(y_test, y_pred):.4f}")
        print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")
        
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['No Disease', 'Heart Disease']))
        
    else:
        print("Failed to save model. Please check file permissions.")

if __name__ == "__main__":
    main() 