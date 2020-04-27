import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

class FeatureStackingClf(BaseEstimator, ClassifierMixin):

    """
    Feature stacking classifier as described in TODO.
    
    Args:
        subset_lengths (list): TODO
        l0_clf (obj): TODO
        l1_clf (obj): TODO
        cv_num_folds (int): TODO

    Attributes:
        subset_lengths (list): TODO
        l0_clf (obj): TODO
        l1_clf (obj): TODO
        cv_num_folds (int): TODO

    """


    def __init__(self, subset_lengths, l0_clf=LogisticRegression, l1_clf=RandomForestClassifier, cv_num_folds=10):
        self.subset_lengths = subset_lengths
        self.l0_clf = l0_clf
        self.l1_clf = l1_clf
        self.cv_num_folds = cv_num_folds


    def _create_subsets(self, X, subset_lengths):
        """
        Partition data into feature subsets.

        Args:
            X (numpy.ndarray): Dataset with all features.
            subset_lengths (list): Lengths of subsets.

        Returns:
            (list): List of partitions.
        """
        
        # Initialize list for storing partitions.
        data_feat_subsets = []

        # Set starting index.
        start_idx = 0
        for idx in range(len(subset_lengths)):
            data_feat_subsets.append(X[:, start_idx:start_idx+subset_lengths[idx]])
            start_idx += subset_lengths[idx]
        return data_feat_subsets


    def fit(self, X, y):
        """
        Fit classifier to training data.

        Args:
            X (numpy.ndarray): Training data samples
            y (numpy.ndarray): Training data labels

        Returns:
            (obj): Reference to self
        """

        # Get number of unique classes.
        num_classes = len(np.unique(y))
        
        # Create training data subsets.
        data_subsets_train = self._create_subsets(X, self.subset_lengths)

        # Initialize list for storing subset predictions.
        pred_subs_all = []
        
        # Go over subsets and get features using cross-validation.
        for subset, clf in zip(data_subsets_train, l0_clfs):
            pred_subs = np.empty((0, num_classes), dtype=int)
            for train_index, test_index in KFold(self.cv_num_folds).split(subset, y):
                pred_nxt = self.l0_clf().fit(subset[train_index, :], y[train_index]).predict_proba(subset[test_index])
                pred_subs = np.vstack((pred_subs, pred_nxt))
            pred_subs_all.append(pred_subs)

        # Learn l1 classifier on predictions.
        self.trained_l1 = self.l1_clf().fit(np.hstack(pred_subs_all), y)

        # Learn l0 classifiers for feature encoding.
        self.encoding_l0 = [self.l0_clf().fit(subset, y) for subset in data_subsets_train]
        
        # Return reference to self.
        return self

    def predict(self, X, y=None):
        """
        Predict labels of new data.
        
        Args:
            X (numpy.ndarray): Data for which to predict classes

        Returns:
            (numpy.ndarray): Predicted labels
        """
        
        data_subsets_predict = self._create_subsets(X, self.subset_lengths)
        l0_encoded = np.hstack([clf.predict_proba(subset) for subset, clf in zip(data_subsets_predict, self.encoding_l0)])

        return self.trained_l1.predict(l0_encoded)


    def score(self, X, y, sample_weight=None):
        """
        Score predictions on training data.
        
        Args:
            X (numpy.ndarray): Test data
            y (numpy.ndarray): True labels
            sample_weight (numpy.ndarray): Sample weights for scoring predictions

        Returns:
            (float): Accuracy scores of predictions
        """
        return accuracy_score(y, self.predict(X), sample_weight=sample_weight)

