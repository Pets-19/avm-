"""
Train XGBoost model for property price prediction.
Implements feature engineering, model training, and evaluation.
"""
import os
import logging
from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PropertyPriceModel:
    """XGBoost model for property price prediction."""
    
    def __init__(self):
        """Initialize the model."""
        self.model = None
        self.feature_columns = None
        self.label_encoders = {}
        self.feature_stats = {}
        
    def engineer_features(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        Engineer features from raw data.
        
        Args:
            df: Raw property data
            is_training: Whether this is training data (to fit encoders)
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering features...")
        
        df = df.copy()
        
        # Extract date features
        if 'instance_date' in df.columns:
            df['instance_date'] = pd.to_datetime(df['instance_date'])
            df['transaction_year'] = df['instance_date'].dt.year
            df['transaction_month'] = df['instance_date'].dt.month
            df['transaction_quarter'] = df['instance_date'].dt.quarter
            df['days_since_2020'] = (df['instance_date'] - pd.Timestamp('2020-01-01')).dt.days
        
        # Price per square foot
        if 'actual_area' in df.columns and 'trans_value' in df.columns:
            df['price_per_sqft'] = df['trans_value'] / df['actual_area'].replace(0, np.nan)
            df['price_per_sqft'] = df['price_per_sqft'].fillna(df['price_per_sqft'].median())
        
        # Log transformations for skewed features
        if 'actual_area' in df.columns:
            df['log_area'] = np.log1p(df['actual_area'])
        
        # Room density
        if 'rooms_en' in df.columns and 'actual_area' in df.columns:
            # Extract numeric room count
            df['room_count'] = df['rooms_en'].str.extract(r'(\d+)').astype(float)
            df['room_density'] = df['room_count'] / (df['actual_area'] / 1000)
            df['room_density'] = df['room_density'].fillna(0)
        
        # Binary features
        binary_cols = ['is_offplan_en', 'is_free_hold_en']
        for col in binary_cols:
            if col in df.columns:
                df[col] = df[col].map({'Yes': 1, 'No': 0}).fillna(0)
        
        # Categorical encoding
        categorical_cols = [
            'area_en', 'prop_type_en', 'group_en', 'procedure_en',
            'rooms_en', 'parking', 'nearest_metro_en', 'nearest_mall_en', 
            'nearest_landmark_en', 'project_en',
            'usage_en', 'prop_sb_type_en'
        ]
        
        for col in categorical_cols:
            if col in df.columns:
                if is_training:
                    # Fit encoder on training data
                    self.label_encoders[col] = LabelEncoder()
                    # Handle missing values
                    df[col] = df[col].fillna('Unknown')
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Use fitted encoder
                    if col in self.label_encoders:
                        df[col] = df[col].fillna('Unknown')
                        # Handle unseen categories
                        known_classes = set(self.label_encoders[col].classes_)
                        df[f'{col}_encoded'] = df[col].apply(
                            lambda x: self.label_encoders[col].transform([x])[0] 
                            if x in known_classes else -1
                        )
        
        # Interaction features
        if 'area_en_encoded' in df.columns and 'prop_type_en_encoded' in df.columns:
            df['area_proptype_interaction'] = df['area_en_encoded'] * df['prop_type_en_encoded']
        
        if 'actual_area' in df.columns and 'room_count' in df.columns:
            df['area_rooms_interaction'] = df['actual_area'] * df['room_count']
        
        logger.info(f"✅ Feature engineering complete. Total features: {len(df.columns)}")
        
        return df
    
    def select_features(self, df: pd.DataFrame, target_col: str = 'trans_value') -> Tuple[pd.DataFrame, pd.Series]:
        """
        Select relevant features for training.
        
        Args:
            df: DataFrame with engineered features
            target_col: Name of target column
            
        Returns:
            Tuple of (X, y)
        """
        logger.info("Selecting features...")
        
        # Define feature columns
        feature_cols = [
            # Numeric features
            'actual_area', 'log_area', 'procedure_area',
            'transaction_year', 'transaction_month', 'transaction_quarter', 'days_since_2020',
            'room_count', 'room_density',
            'total_buyer', 'total_seller',
            
            # Binary features
            'is_offplan_en', 'is_free_hold_en',
            
            # Encoded categorical features
            'area_en_encoded', 'prop_type_en_encoded', 'group_en_encoded',
            'procedure_en_encoded', 'rooms_en_encoded', 'parking_encoded',
            'nearest_metro_en_encoded', 'nearest_mall_en_encoded',
            'nearest_landmark_en_encoded', 'project_en_encoded',
            'usage_en_encoded', 'prop_sb_type_en_encoded',
            
            # Interaction features
            'area_proptype_interaction', 'area_rooms_interaction'
        ]
        
        # Filter to only available columns
        available_features = [col for col in feature_cols if col in df.columns]
        
        # Store feature columns for later use
        self.feature_columns = available_features
        
        X = df[available_features]
        y = df[target_col]
        
        # Handle any remaining NaN values
        X = X.fillna(X.median())
        
        logger.info(f"✅ Selected {len(available_features)} features")
        logger.info(f"Features: {available_features}")
        
        return X, y
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, 
              X_val: pd.DataFrame = None, y_val: pd.Series = None) -> Dict[str, Any]:
        """
        Train XGBoost model.
        
        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features (optional)
            y_val: Validation target (optional)
            
        Returns:
            Dictionary with training metrics
        """
        logger.info("Training XGBoost model...")
        
        # XGBoost parameters optimized for real estate
        params = {
            'objective': 'reg:squarederror',
            'max_depth': 8,
            'learning_rate': 0.05,
            'n_estimators': 500,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'n_jobs': -1,
            'verbosity': 1
        }
        
        # Create model
        self.model = xgb.XGBRegressor(**params)
        
        # Train with early stopping if validation set provided
        if X_val is not None and y_val is not None:
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_train, y_train), (X_val, y_val)],
                verbose=False
            )
            logger.info(f"✅ Training complete")
        else:
            self.model.fit(X_train, y_train)
            logger.info("✅ Training complete")
        
        # Calculate training metrics
        y_train_pred = self.model.predict(X_train)
        
        metrics = {
            'train_mae': mean_absolute_error(y_train, y_train_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'train_r2': r2_score(y_train, y_train_pred),
            'train_mape': mean_absolute_percentage_error(y_train, y_train_pred) * 100
        }
        
        if X_val is not None and y_val is not None:
            y_val_pred = self.model.predict(X_val)
            metrics.update({
                'val_mae': mean_absolute_error(y_val, y_val_pred),
                'val_rmse': np.sqrt(mean_squared_error(y_val, y_val_pred)),
                'val_r2': r2_score(y_val, y_val_pred),
                'val_mape': mean_absolute_percentage_error(y_val, y_val_pred) * 100
            })
        
        return metrics
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """
        Evaluate model on test set.
        
        Args:
            X_test: Test features
            y_test: Test target
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating model on test set...")
        
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred) * 100
        
        # Calculate error percentiles
        errors = np.abs(y_test - y_pred)
        error_percentiles = {
            'p50': np.percentile(errors, 50),
            'p75': np.percentile(errors, 75),
            'p90': np.percentile(errors, 90),
            'p95': np.percentile(errors, 95)
        }
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'mape': mape,
            'error_percentiles': error_percentiles
        }
        
        logger.info(f"\n{'='*60}")
        logger.info("📊 Model Performance Metrics")
        logger.info(f"{'='*60}")
        logger.info(f"MAE:  AED {mae:,.0f} ({mae/y_test.mean()*100:.2f}% of avg price)")
        logger.info(f"RMSE: AED {rmse:,.0f}")
        logger.info(f"R²:   {r2:.4f}")
        logger.info(f"MAPE: {mape:.2f}%")
        logger.info(f"\nError Percentiles:")
        logger.info(f"  50th: AED {error_percentiles['p50']:,.0f}")
        logger.info(f"  75th: AED {error_percentiles['p75']:,.0f}")
        logger.info(f"  90th: AED {error_percentiles['p90']:,.0f}")
        logger.info(f"  95th: AED {error_percentiles['p95']:,.0f}")
        logger.info(f"{'='*60}\n")
        
        # Check if meets target accuracy
        target_mae = 100000  # 100K AED
        target_r2 = 0.85
        
        if mae < target_mae and r2 > target_r2:
            logger.info("✅ Model meets target accuracy!")
        else:
            logger.warning("⚠️ Model does not meet target accuracy")
            logger.warning(f"   Target MAE: < {target_mae:,} (Got: {mae:,.0f})")
            logger.warning(f"   Target R²:  > {target_r2} (Got: {r2:.4f})")
        
        return metrics
    
    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get feature importance from trained model.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature importance
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        })
        importance_df = importance_df.sort_values('importance', ascending=False).head(top_n)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Top {top_n} Most Important Features")
        logger.info(f"{'='*60}")
        for idx, row in importance_df.iterrows():
            logger.info(f"{row['feature']:40s}: {row['importance']:.4f}")
        logger.info(f"{'='*60}\n")
        
        return importance_df
    
    def save(self, model_path: str = "models/xgboost_model_v1.pkl",
             encoders_path: str = "models/label_encoders_v1.pkl",
             features_path: str = "models/feature_columns_v1.pkl"):
        """
        Save model, encoders, and feature columns.
        
        Args:
            model_path: Path to save model
            encoders_path: Path to save label encoders
            features_path: Path to save feature columns
        """
        logger.info("Saving model artifacts...")
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        joblib.dump(self.model, model_path)
        logger.info(f"✅ Model saved to {model_path}")
        
        # Save encoders
        joblib.dump(self.label_encoders, encoders_path)
        logger.info(f"✅ Encoders saved to {encoders_path}")
        
        # Save feature columns
        joblib.dump(self.feature_columns, features_path)
        logger.info(f"✅ Feature columns saved to {features_path}")
    
    @classmethod
    def load(cls, model_path: str = "models/xgboost_model_v1.pkl",
             encoders_path: str = "models/label_encoders_v1.pkl",
             features_path: str = "models/feature_columns_v1.pkl"):
        """
        Load trained model, encoders, and feature columns.
        
        Args:
            model_path: Path to model file
            encoders_path: Path to encoders file
            features_path: Path to feature columns file
            
        Returns:
            Loaded PropertyPriceModel instance
        """
        logger.info("Loading model artifacts...")
        
        instance = cls()
        instance.model = joblib.load(model_path)
        instance.label_encoders = joblib.load(encoders_path)
        instance.feature_columns = joblib.load(features_path)
        
        logger.info(f"✅ Model loaded from {model_path}")
        logger.info(f"✅ Encoders loaded from {encoders_path}")
        logger.info(f"✅ Feature columns loaded from {features_path}")
        
        return instance


def main():
    """Main training pipeline."""
    logger.info("🚀 Starting ML model training pipeline...")
    
    # Load data
    data_path = "data/properties_training.csv"
    if not os.path.exists(data_path):
        logger.error(f"❌ Data file not found: {data_path}")
        logger.error("Please run export_training_data.py first")
        return
    
    logger.info(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    logger.info(f"✅ Loaded {len(df):,} records")
    
    # Remove outliers
    logger.info("Removing outliers...")
    initial_count = len(df)
    df = df[
        (df['trans_value'] > 100000) &  # Minimum 100K AED
        (df['trans_value'] < 50000000) &  # Maximum 50M AED
        (df['actual_area'] > 100) &  # Minimum 100 sqft
        (df['actual_area'] < 30000)  # Maximum 30K sqft
    ]
    logger.info(f"✅ Removed {initial_count - len(df):,} outliers ({(initial_count - len(df))/initial_count*100:.1f}%)")
    
    # Initialize model
    model = PropertyPriceModel()
    
    # Engineer features
    df_featured = model.engineer_features(df, is_training=True)
    
    # Select features
    X, y = model.select_features(df_featured, target_col='trans_value')
    
    # Split data: 70% train, 15% validation, 15% test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, random_state=42  # 0.176 * 0.85 ≈ 0.15
    )
    
    logger.info(f"\n{'='*60}")
    logger.info("Dataset Split:")
    logger.info(f"  Training:   {len(X_train):,} samples ({len(X_train)/len(X)*100:.1f}%)")
    logger.info(f"  Validation: {len(X_val):,} samples ({len(X_val)/len(X)*100:.1f}%)")
    logger.info(f"  Test:       {len(X_test):,} samples ({len(X_test)/len(X)*100:.1f}%)")
    logger.info(f"{'='*60}\n")
    
    # Train model
    train_metrics = model.train(X_train, y_train, X_val, y_val)
    
    logger.info(f"\n{'='*60}")
    logger.info("Training Metrics:")
    logger.info(f"  Train MAE:  AED {train_metrics['train_mae']:,.0f}")
    logger.info(f"  Train RMSE: AED {train_metrics['train_rmse']:,.0f}")
    logger.info(f"  Train R²:   {train_metrics['train_r2']:.4f}")
    logger.info(f"  Train MAPE: {train_metrics['train_mape']:.2f}%")
    if 'val_mae' in train_metrics:
        logger.info(f"\n  Val MAE:    AED {train_metrics['val_mae']:,.0f}")
        logger.info(f"  Val RMSE:   AED {train_metrics['val_rmse']:,.0f}")
        logger.info(f"  Val R²:     {train_metrics['val_r2']:.4f}")
        logger.info(f"  Val MAPE:   {train_metrics['val_mape']:.2f}%")
    logger.info(f"{'='*60}\n")
    
    # Evaluate on test set
    test_metrics = model.evaluate(X_test, y_test)
    
    # Feature importance
    feature_importance = model.get_feature_importance(top_n=20)
    
    # Save model
    model.save()
    
    # Save metrics
    metrics_path = "models/training_metrics.json"
    import json
    all_metrics = {
        'training_date': datetime.now().isoformat(),
        'dataset_size': len(df),
        'train_size': len(X_train),
        'val_size': len(X_val),
        'test_size': len(X_test),
        'train_metrics': train_metrics,
        'test_metrics': test_metrics,
        'feature_count': len(model.feature_columns),
        'top_features': feature_importance.to_dict('records')
    }
    
    with open(metrics_path, 'w') as f:
        json.dump(all_metrics, f, indent=2)
    logger.info(f"✅ Metrics saved to {metrics_path}")
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("🎉 Training Complete!")
    logger.info("="*60)
    logger.info(f"Model saved to: models/xgboost_model_v1.pkl")
    logger.info(f"Test MAE: AED {test_metrics['mae']:,.0f} ({test_metrics['mape']:.2f}%)")
    logger.info(f"Test R²: {test_metrics['r2']:.4f}")
    logger.info("="*60)
    logger.info("\n🎯 Next Steps:")
    logger.info("1. Review model metrics in models/training_metrics.json")
    logger.info("2. Integrate model into app.py")
    logger.info("3. Test hybrid predictions with sample properties")


if __name__ == "__main__":
    main()
