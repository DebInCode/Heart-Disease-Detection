import numpy as np
import pandas as pd
import pickle
import warnings
from pathlib import Path
from typing import Tuple, Dict, Union, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HeartDiseasePredictor:
    """
    A comprehensive heart disease prediction class that loads trained models
    and provides prediction functionality with input validation and risk assessment.
    """
    
    def __init__(self, model_path: str = None, scaler_path: str = None):
        """
        Initialize the HeartDiseasePredictor with trained model and scaler.
        
        Args:
            model_path: Path to the trained model pickle file
            scaler_path: Path to the scaler pickle file
        """
        self.model = None
        self.scaler = None
        self.feature_names = [
            "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"
        ]
        
        # Set default paths if not provided
        if model_path is None:
            model_path = Path(__file__).parent.parent / "models" / "heart_rf_model.pkl"
        if scaler_path is None:
            scaler_path = Path(__file__).parent.parent / "models" / "scaler.pkl"
        
        self.load_model_and_scaler(model_path, scaler_path)
    
    def load_model_and_scaler(self, model_path: str, scaler_path: str) -> bool:
        """
        Load the trained model and scaler from pickle files.
        
        Args:
            model_path: Path to the model file
            scaler_path: Path to the scaler file
            
        Returns:
            bool: True if loading successful, False otherwise
        """
        try:
            # Load the model
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded successfully from {model_path}")
            
            # Load the scaler
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info(f"Scaler loaded successfully from {scaler_path}")
            
            return True
            
        except FileNotFoundError as e:
            logger.error(f"Model or scaler file not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading model or scaler: {e}")
            return False
    
    def validate_input(self, input_data: Union[np.ndarray, List, Dict]) -> Tuple[np.ndarray, bool]:
        """
        Validate and preprocess input data.
        
        Args:
            input_data: Input data as numpy array, list, or dictionary
            
        Returns:
            Tuple[np.ndarray, bool]: (processed_data, is_valid)
        """
        try:
            # Convert dictionary to array if needed
            if isinstance(input_data, dict):
                # Ensure all required features are present
                missing_features = set(self.feature_names) - set(input_data.keys())
                if missing_features:
                    logger.error(f"Missing features: {missing_features}")
                    return None, False
                
                # Convert to array in correct order
                input_array = np.array([input_data[feature] for feature in self.feature_names])
            
            # Convert list to array if needed
            elif isinstance(input_data, list):
                input_array = np.array(input_data)
            
            # Already numpy array
            elif isinstance(input_data, np.ndarray):
                input_array = input_data
            else:
                logger.error(f"Unsupported input type: {type(input_data)}")
                return None, False
            
            # Reshape if needed (single sample)
            if input_array.ndim == 1:
                input_array = input_array.reshape(1, -1)
            
            # Check dimensions
            if input_array.shape[1] != len(self.feature_names):
                logger.error(f"Expected {len(self.feature_names)} features, got {input_array.shape[1]}")
                return None, False
            
            # Check for NaN or infinite values
            if np.any(np.isnan(input_array)) or np.any(np.isinf(input_array)):
                logger.error("Input contains NaN or infinite values")
                return None, False
            
            return input_array, True
            
        except Exception as e:
            logger.error(f"Error validating input: {e}")
            return None, False
    
    def predict_heart_disease(self, input_data: Union[np.ndarray, List, Dict]) -> Tuple[int, float]:
        """
        Predict heart disease for given input data.
        
        Args:
            input_data: Input features as numpy array, list, or dictionary
            
        Returns:
            Tuple[int, float]: (prediction, probability)
                - prediction: 0 (no disease) or 1 (disease)
                - probability: Probability of heart disease (class 1)
        """
        if self.model is None or self.scaler is None:
            logger.error("Model or scaler not loaded")
            return None, None
        
        # Validate input
        input_array, is_valid = self.validate_input(input_data)
        if not is_valid:
            return None, None
        
        try:
            # Scale the input
            input_scaled = self.scaler.transform(input_array)
            
            # Make prediction
            prediction = self.model.predict(input_scaled)[0]
            
            # Get probability
            if hasattr(self.model, 'predict_proba'):
                probability = self.model.predict_proba(input_scaled)[0][1]  # Probability of class 1
            else:
                # For models without predict_proba, use decision function
                if hasattr(self.model, 'decision_function'):
                    decision_score = self.model.decision_function(input_scaled)[0]
                    probability = 1 / (1 + np.exp(-decision_score))  # Sigmoid transformation
                else:
                    probability = 1.0 if prediction == 1 else 0.0
            
            return int(prediction), float(probability)
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return None, None
    
    def predict_batch(self, input_data: Union[np.ndarray, List[List], List[Dict]]) -> Tuple[List[int], List[float]]:
        """
        Predict heart disease for multiple samples.
        
        Args:
            input_data: List of input features
            
        Returns:
            Tuple[List[int], List[float]]: (predictions, probabilities)
        """
        if self.model is None or self.scaler is None:
            logger.error("Model or scaler not loaded")
            return None, None
        
        try:
            # Convert to numpy array
            if isinstance(input_data, list):
                if isinstance(input_data[0], dict):
                    # Convert list of dictionaries to array
                    input_array = np.array([[sample[feature] for feature in self.feature_names] 
                                           for sample in input_data])
                else:
                    input_array = np.array(input_data)
            else:
                input_array = input_data
            
            # Validate dimensions
            if input_array.shape[1] != len(self.feature_names):
                logger.error(f"Expected {len(self.feature_names)} features, got {input_array.shape[1]}")
                return None, None
            
            # Scale the input
            input_scaled = self.scaler.transform(input_array)
            
            # Make predictions
            predictions = self.model.predict(input_scaled)
            
            # Get probabilities
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(input_scaled)[:, 1]  # Probability of class 1
            else:
                if hasattr(self.model, 'decision_function'):
                    decision_scores = self.model.decision_function(input_scaled)
                    probabilities = 1 / (1 + np.exp(-decision_scores))  # Sigmoid transformation
                else:
                    probabilities = [1.0 if pred == 1 else 0.0 for pred in predictions]
            
            return predictions.tolist(), probabilities.tolist()
            
        except Exception as e:
            logger.error(f"Error making batch prediction: {e}")
            return None, None
    
    def get_risk_level(self, probability: float) -> str:
        """
        Convert probability to risk level.
        
        Args:
            probability: Probability of heart disease
            
        Returns:
            str: Risk level description
        """
        if probability < 0.2:
            return "Low Risk"
        elif probability < 0.5:
            return "Moderate Risk"
        elif probability < 0.8:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance if the model supports it.
        
        Returns:
            Dict[str, float]: Feature importance scores
        """
        if self.model is None:
            return {}
        
        try:
            if hasattr(self.model, 'feature_importances_'):
                importance_dict = dict(zip(self.feature_names, self.model.feature_importances_))
                return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            elif hasattr(self.model, 'coef_'):
                # For linear models
                importance_dict = dict(zip(self.feature_names, np.abs(self.model.coef_[0])))
                return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            else:
                logger.warning("Model does not support feature importance")
                return {}
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
    
    def get_prediction_explanation(self, input_data: Union[np.ndarray, List, Dict]) -> Dict:
        """
        Get detailed prediction explanation.
        
        Args:
            input_data: Input features
            
        Returns:
            Dict: Detailed prediction information
        """
        prediction, probability = self.predict_heart_disease(input_data)
        
        if prediction is None:
            return {}
        
        explanation = {
            'prediction': prediction,
            'probability': probability,
            'risk_level': self.get_risk_level(probability),
            'interpretation': 'Heart Disease Detected' if prediction == 1 else 'No Heart Disease Detected'
        }
        
        # Add feature importance if available
        feature_importance = self.get_feature_importance()
        if feature_importance:
            explanation['top_features'] = dict(list(feature_importance.items())[:5])
        
        return explanation

# Convenience function for simple predictions
def predict_heart_disease(input_data: Union[np.ndarray, List, Dict]) -> Tuple[int, float]:
    """
    Convenience function for making heart disease predictions.
    
    Args:
        input_data: Input features as numpy array, list, or dictionary
        
    Returns:
        Tuple[int, float]: (prediction, probability)
    """
    predictor = HeartDiseasePredictor()
    return predictor.predict_heart_disease(input_data)

# Example usage and testing
if __name__ == "__main__":
    # Create predictor instance
    predictor = HeartDiseasePredictor()
    
    # Example input data (you can modify these values)
    example_input = {
        'age': 63,
        'sex': 1,
        'cp': 1,
        'trestbps': 145,
        'chol': 233,
        'fbs': 1,
        'restecg': 2,
        'thalach': 150,
        'exang': 0,
        'oldpeak': 2.3,
        'slope': 3,
        'ca': 0,
        'thal': 6
    }
    
    # Make prediction
    prediction, probability = predictor.predict_heart_disease(example_input)
    
    if prediction is not None:
        print(f"Prediction: {prediction}")
        print(f"Probability: {probability:.4f}")
        print(f"Risk Level: {predictor.get_risk_level(probability)}")
        
        # Get detailed explanation
        explanation = predictor.get_prediction_explanation(example_input)
        print(f"\nDetailed Explanation:")
        for key, value in explanation.items():
            print(f"{key}: {value}")
        
        # Test with different risk levels
        print(f"\n" + "="*50)
        print("TESTING DIFFERENT RISK SCENARIOS")
        print("="*50)
        
        # High risk example
        high_risk_input = {
            'age': 70,
            'sex': 1,
            'cp': 4,  # asymptomatic
            'trestbps': 180,
            'chol': 300,
            'fbs': 1,
            'restecg': 2,
            'thalach': 120,
            'exang': 1,
            'oldpeak': 4.0,
            'slope': 3,
            'ca': 3,
            'thal': 7
        }
        
        high_pred, high_prob = predictor.predict_heart_disease(high_risk_input)
        print(f"\nHigh Risk Example:")
        print(f"Prediction: {high_pred}")
        print(f"Probability: {high_prob:.4f}")
        print(f"Risk Level: {predictor.get_risk_level(high_prob)}")
        
        # Low risk example
        low_risk_input = {
            'age': 45,
            'sex': 0,
            'cp': 3,  # non-anginal pain
            'trestbps': 120,
            'chol': 180,
            'fbs': 0,
            'restecg': 0,
            'thalach': 180,
            'exang': 0,
            'oldpeak': 0.0,
            'slope': 1,
            'ca': 0,
            'thal': 3
        }
        
        low_pred, low_prob = predictor.predict_heart_disease(low_risk_input)
        print(f"\nLow Risk Example:")
        print(f"Prediction: {low_pred}")
        print(f"Probability: {low_prob:.4f}")
        print(f"Risk Level: {predictor.get_risk_level(low_prob)}")
        
    else:
        print("Prediction failed. Please check the input data and model files.")
