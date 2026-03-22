import pandas as pd
import numpy as np
import re
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Stop words français
FRENCH_STOP_WORDS = [
    'au', 'aux', 'avec', 'ce', 'ces', 'dans', 'de', 'des', 'du', 'elle', 'en',
    'et', 'eux', 'il', 'je', 'la', 'le', 'leur', 'lui', 'ma', 'mais', 'me',
    'même', 'mes', 'moi', 'mon', 'ne', 'nos', 'notre', 'nous', 'on', 'ou',
    'par', 'pas', 'pour', 'qu', 'que', 'qui', 'sa', 'se', 'ses', 'son', 'sur',
    'ta', 'te', 'tes', 'toi', 'ton', 'tu', 'un', 'une', 'vos', 'votre', 'vous',
    'c', 'd', 'j', 'l', 'à', 'm', 'n', 's', 't', 'y'
]

class DataPreprocessor:
    """Prétraitement des données touristiques"""
    
    def __init__(self):
        self.preprocessor = None
        self.feature_names = None
        
    def clean_data(self, df):
        """Nettoyage basique"""
        df = df.copy()
        
        # Remplir les textes vides
        text_cols = ['description_courte', 'sous_types_tags', 'nom', 
                    'region', 'type_activite']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str)
        
        # Nettoyer les nombres
        if 'nombre_avis' in df.columns:
            df['nombre_avis'] = pd.to_numeric(
                df['nombre_avis'].astype(str).str.replace('+', ''), 
                errors='coerce'
            ).fillna(0)
        
        if 'note_moyenne' in df.columns:
            df['note_moyenne'] = pd.to_numeric(df['note_moyenne'], errors='coerce')
            df['note_moyenne'] = df['note_moyenne'].fillna(df['note_moyenne'].median())
        
        # Convertir la durée en heures
        if 'duree_typique_visite' in df.columns:
            df['duree_heures'] = self._convert_duration(df['duree_typique_visite'])
        
        # Features supplémentaires
        if 'nombre_avis' in df.columns:
            df['log_avis'] = np.log1p(df['nombre_avis'])
        
        return df
    
    def _convert_duration(self, duration_series):
        """Convertit la durée en heures"""
        def parse_duration(value):
            if pd.isna(value):
                return 2  # valeur par défaut
            
            value = str(value).lower()
            
            # Chercher des patterns simples
            heures = re.search(r'(\d+)\s*heures?', value)
            if heures:
                return int(heures.group(1))
            
            minutes = re.search(r'(\d+)\s*minutes?', value)
            if minutes:
                return int(minutes.group(1)) / 60
            
            if 'demi' in value:
                return 4
            if 'journée' in value:
                return 8
                
            return 2  # valeur par défaut
        
        return duration_series.apply(parse_duration)
    
    def build_preprocessor(self, df):
        """Construit le préprocesseur sklearn"""
        
        # Features numériques
        numeric_features = []
        for col in ['latitude', 'longitude', 'note_moyenne', 'log_avis', 
                   'prix_approximatif_ar', 'duree_heures']:
            if col in df.columns:
                numeric_features.append(col)
        
        # Features catégorielles
        categorical_features = []
        for col in ['region', 'type_activite', 'difficulte']:
            if col in df.columns:
                categorical_features.append(col)
        
        # Pipelines
        numeric_transformer = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        text_transformer = TfidfVectorizer(
            max_features=100,
            stop_words=FRENCH_STOP_WORDS,
            lowercase=True
        )
        
        # Construire le column transformer
        transformers = []
        
        if numeric_features:
            transformers.append(('num', numeric_transformer, numeric_features))
        
        if categorical_features:
            transformers.append(('cat', categorical_transformer, categorical_features))
        
        if 'description_courte' in df.columns:
            transformers.append(('text', text_transformer, 'description_courte'))
        
        self.preprocessor = ColumnTransformer(transformers)
        
        return self.preprocessor
    
    def fit_transform(self, df):
        """Applique tout le preprocessing"""
        df_clean = self.clean_data(df)
        preprocessor = self.build_preprocessor(df_clean)
        X = preprocessor.fit_transform(df_clean)
        return df_clean, X
    
    def transform(self, df):
        """Transforme de nouvelles données"""
        df_clean = self.clean_data(df)
        return self.preprocessor.transform(df_clean)
    
    def save(self, path):
        """Sauvegarde le préprocesseur"""
        joblib.dump(self, path)
    
    @staticmethod
    def load(path):
        """Charge le préprocesseur"""
        return joblib.load(path)