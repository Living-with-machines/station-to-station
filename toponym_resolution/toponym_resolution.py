import pandas as pd
from pathlib import Path
from tools import eval_methods, resolution_methods
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score
import random
import itertools
from tqdm import tqdm
import pickle


# Options for experiments
num_candidates_list = [1, 3, 5]
settings = ["test", "dev"]
candrank_approaches = ["deezy_match", "partial_match", "perfect_match"]


# Load gazetteer
gazetteer_df = pd.read_csv("../processed/wikidata/gb_gazetteer.csv", header=0, index_col=0, low_memory=False)


# Load pickle with wikipedia inlinks
with open("../processed/wikipedia/overall_entity_freq.pickle", 'rb') as fp:
    wikipedia_entity_overall_dict = pickle.load(fp)

    
# ===============================
# Feature selection for dev and test
# ===============================
for num_candidates in num_candidates_list:
    for setting in settings:
        for candrank in candrank_approaches:
            print("Processing " + candrank + " " + setting + " " + str(num_candidates))
            features_file = "../processed/resolution/features_" + candrank + "_" + setting + str(num_candidates) + ".tsv"
            if not Path(features_file).is_file():
                df = pd.read_pickle("../processed/resolution/candranking_" + candrank + "_" + setting + str(num_candidates) + ".pkl")
                exp_df = resolution_methods.feature_selection(candrank, df, gazetteer_df, wikipedia_entity_overall_dict)
                exp_df.drop_duplicates(subset=['Query','Candidate'], inplace=True)
                exp_df.to_csv(features_file, sep="\t")

    
# ===============================
# Apply the different methods
# ===============================

for num_candidates in num_candidates_list:
    for candrank_method in candrank_approaches:
        
        print("Applying methods and baselines to " + candrank_method + " with " + str(num_candidates) + " nv.")

        # We will store the results of all methods/baselines as columns in the original structured dataframe:
        results_test_df = pd.read_pickle("../processed/quicks/quicks_test.pkl")
        features_dev_df = pd.read_csv("../processed/resolution/features_" + candrank_method + "_dev" + str(num_candidates) + ".tsv",sep='\t', index_col=0)
        features_test_df = pd.read_csv("../processed/resolution/features_" + candrank_method + "_test" + str(num_candidates) + ".tsv",sep='\t', index_col=0)

        # -------------------------------
        # Baselines
        # -------------------------------

        # Apply candrank-most-confident baseline
        results_test_df = resolution_methods.candrank_most_confident(features_test_df, results_test_df)

        # Apply wikipedia-most-relevant baseline
        results_test_df = resolution_methods.wikipedia_most_relevant(features_test_df, results_test_df)

        # Apply semantically_most_similar baseline
        results_test_df = resolution_methods.semantically_most_similar(features_test_df, results_test_df)

        # -------------------------------
        # Skyline
        # -------------------------------

        # Best possible result given candidates
        results_test_df = resolution_methods.skyline(features_test_df, results_test_df)

        # -------------------------------
        # RankLib: Apply learning to rank (note: performed and averaged 5 runs because results fluctuated quite a lot)
        # -------------------------------

        code_folder = str(Path("../../").resolve()) + "/"
        filter="all"
        feature_combination = "allfeatures" # Uncomment if you want to use all features 
        cross_val = False

        # Apply all features combination to test set:
        results_test_df = resolution_methods.ranklib(features_dev_df,features_test_df,filter,code_folder,cross_val,results_test_df,feature_combination,num_candidates)

        # -------------------------------
        # Our method simple: one classifier for all entries
        # -------------------------------

        # ------------------------------
        # Train the classifier with all the features
        dev_df = features_dev_df # development set feature vectors
        use_cols_all = ['f_0','f_1','f_2','f_3','f_4','f_5','f_6','f_7','f_8'] # features to use
        clf_all = resolution_methods.train_classifier(dev_df, use_cols_all)

        # ------------------------------
        # Apply the classifier with all the features
        features_test_df = features_test_df # test set feature vectors
        results_test_df = resolution_methods.our_method_simple(features_test_df, clf_all, use_cols_all, gazetteer_df, results_test_df)

        # -------------------------------
        # Our method comb: Combine stations and places classifiers
        # -------------------------------

        use_cols_all = ["f_0", "f_1", "f_2", "f_3", "f_4", "f_5", "f_6", "f_7", "f_8"] 

        # Train railway stations classifier (exact setting):
        dev_df = features_dev_df # development set feature vectors
        df_exact = dev_df[dev_df["Exact"] == 1]
        use_cols_stations = use_cols_all
        # Train the classifier:
        clf_stations = resolution_methods.train_classifier(df_exact, use_cols_all)

        # Train places classifier (not exact setting):
        dev_df = features_dev_df # development set feature vectors
        df_inexact = dev_df[dev_df["Exact"] == 0]
        use_cols_places = use_cols_all
        # Train the classifier:
        clf_places = resolution_methods.train_classifier(df_inexact, use_cols_all)

        # Find optimal threshold for stations/places:
        optimal_threshold = 0.0
        keep_acc = 0.0
        for th in np.arange(0, 1, 0.05):
            th = round(th, 2)
            results_dev_df = pd.read_pickle("../processed/quicks/quicks_dev.pkl")
            results_dev_df = resolution_methods.our_method_comb(features_dev_df, clf_stations, use_cols_stations, clf_places, use_cols_places, gazetteer_df, th, results_dev_df)
            acc = eval_methods.topres_exactmetrics(results_dev_df, "our_method_comb", False)
            if acc >= keep_acc:
                optimal_threshold = th
                keep_acc = acc

        print(optimal_threshold, keep_acc)

        # Apply our classification methods:
        results_test_df = resolution_methods.our_method_comb(features_test_df, clf_stations, use_cols_stations, clf_places, use_cols_places, gazetteer_df, optimal_threshold, results_test_df)
        
        # Store resolution file:
        results_test_df.to_pickle("../processed/resolution/resolved_" + candrank_method + "_test" + str(num_candidates) + ".pkl")