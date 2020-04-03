wget -O ./model.zip https://www.dropbox.com/sh/296jton428kzhpm/AABJwB7JAqD_NAF2y5Dd_inda?dl=0

unzip model.zip

python3 test_model.py $1 $2

python3 bleu_eval.py $2