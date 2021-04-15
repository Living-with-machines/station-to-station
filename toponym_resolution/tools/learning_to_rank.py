import pathlib
import subprocess

def convert_feature_file_format(filepath, filter):
    p = pathlib.Path(filepath)
    
    if filter == "exact":
        outfile = p.stem+"_exact-ranklib.tsv"
    elif filter == "notexact":
        outfile = p.stem+"_notexact-ranklib.tsv"
    else:
        outfile = p.stem+"_all-ranklib.tsv"

    out_feat_folder = "toponym_resolution/supervised_ranking/feature_files/"
    out_model_folder = "toponym_resolution/supervised_ranking/models/"
    pathlib.Path(out_feat_folder).mkdir(parents=True, exist_ok=True)
    pathlib.Path(out_model_folder).mkdir(parents=True, exist_ok=True)
    out = open(out_feat_folder+ outfile,"w")

    features = open(filepath).read().strip().split("\n")[1:]
    current_qid = 0
    current_sub_id = 0
    for line in features:
        feat_vect = []
        line = line.split("\t")
        filter_flag = line[-1]
        if filter == "exact" and filter_flag!="1":
            continue
        if filter == "notexact" and filter_flag!="0":
            continue

        label = line[-2]
        cand = line[4]
        feat_vect.append(str(label))
        sub_id = line [2]
        if sub_id != current_sub_id:
            current_sub_id = sub_id
            current_qid+=1
        feat_vect.append("qid:"+str(current_qid))
        feat_counter = 1
        for f in range(5,14):
            feat_vect.append(str(feat_counter)+":"+str(line[f]))
            feat_counter+=1
        feat_vect.append("# "+ str(cand)+ " "+ str(current_sub_id))
        out.write(" ".join(feat_vect))
        out.write("\n")
    out.close()
    return out_feat_folder+ outfile

def run_ranklib(dev_feat_file,test_feat_file,filter,code_folder,cross_val):

    dev = convert_feature_file_format(dev_feat_file,filter=filter)
    feature_used = open("toponym_resolution/supervised_ranking/models/features.txt","r").read().replace('\n'," ")

    if cross_val == True:
        subprocess.call(["java", "-jar",code_folder+"PlaceLinking/toponym_resolution/tools/RankLib-2.13.jar","-train",dev,"-ranker","4","-kcv", "5", "-metric2t","P@1", "-metric2T", "P@1","-feature","toponym_resolution/supervised_ranking/models/features.txt"])
        print ("feature used:",feature_used)
    else:
        test = convert_feature_file_format(test_feat_file,filter="all")
        out = subprocess.check_output(["java", "-jar",code_folder+"PlaceLinking/toponym_resolution/tools/RankLib-2.13.jar","-train",dev,"-test",test,"-ranker","4","-metric2t","P@1", "-metric2T", "P@1","-save",code_folder+"PlaceLinking/toponym_resolution/supervised_ranking/models/model.run","-feature","toponym_resolution/supervised_ranking/models/features.txt"])
        train_performance = out.decode("utf-8").split("\n")[-6]
        test_performance = out.decode("utf-8").split("\n")[-4]
        print (train_performance,test_performance)
        subprocess.check_output(["java", "-jar",code_folder+"PlaceLinking/toponym_resolution/tools/RankLib-2.13.jar","-load","toponym_resolution/supervised_ranking/models/model.run","-rank",test,"-indri","toponym_resolution/supervised_ranking/models/rank.txt","-feature","toponym_resolution/supervised_ranking/models/features.txt"])
        
        rank = open("toponym_resolution/supervised_ranking/models/rank.txt","r").read().strip().split("\n")
        q_ids = set([x.split(" ")[3] for x in rank])

        results = {}

        for q_id in q_ids:
            scores = [[x.split(" ")[2],float(x.split(" ")[5])] for x in rank if x.split(" ")[3]==q_id]
            scores.sort(key=lambda x: x[1],reverse=True)
            results[q_id] = scores[0][0]
        print ("feature used:",feature_used)

        return results


code_folder = "/home/fnanni/Projects/"
filter="exact"
dev_feat_file = "toponym_resolution/features_dev_deezy_match.tsv"
test_feat_file = "toponym_resolution/features_test_deezy_match.tsv"
cross_val = False
res_dict = run_ranklib(dev_feat_file,test_feat_file,filter,code_folder,cross_val)
print (res_dict)