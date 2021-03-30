from DeezyMatch import train as dm_train
from DeezyMatch import plot_log
from DeezyMatch import finetune as dm_finetune
from DeezyMatch import inference as dm_inference

from pathlib import Path
from shutil import copyfile

# If model does not exist already, train a new model:
if not Path('../processed/deezymatch/wikidata_british_isles').is_dir():
    # train a new model
    dm_train(input_file_path="../processed/deezymatch/input_dfm.yaml",
         dataset_path="../processed/deezymatch/british_isles_toponym_pairs.txt",
         model_name="wikidata_british_isles")
    
# plot log file
plot_log(path2log="../processed/deezymatch/wikidata_british_isles/log.txt", 
         output_name="wikidata_british_isles")

# fine-tune a pretrained model stored at pretrained_model_path and pretrained_vocab_path 
dm_finetune(input_file_path="../processed/deezymatch/input_dfm.yaml", 
            dataset_path="../processed/deezymatch/british_isles_stations_toponym_pairs.txt", 
            model_name="wikidata_british_isles_stations",
            pretrained_model_path="../processed/deezymatch/models/wikidata_british_isles/wikidata_british_isles.model", 
            pretrained_vocab_path="../processed/deezymatch/models/wikidata_british_isles/wikidata_british_isles.vocab")
    
# plot log file
plot_log(path2log="../processed/deezymatch/wikidata_british_isles_stations/log.txt", 
         output_name="wikidata_british_isles_stations")