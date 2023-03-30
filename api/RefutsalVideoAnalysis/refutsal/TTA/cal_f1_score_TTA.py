import os
import sys
TEST = 2

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if TEST ==1:
    GROUND_TRUE_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\\goal_clips\\test1\\output\\ground_true.csv'
    RESULT_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\\goal_clips\\test1\\output\\result.csv'
elif TEST ==2:
    GROUND_TRUE_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\\goal_clips\\test2\\output\\ground_true.csv'
    RESULT_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\\goal_clips\\test2\\output\\result.csv'
elif TEST ==3:
    GROUND_TRUE_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\\goal_clips\\test3\\output\\ground_true.csv'
    RESULT_PATH = 'RefutsalVideoAnalysis\input\\refutsal_v1\\goal_clips\\test3\\output\\result.csv'
import csv

#ground_true, result 파일에서 vid name 읽음 저장
with open(GROUND_TRUE_PATH, 'r') as ground_truth_file, open(RESULT_PATH, 'r') as expected_result_file:
    ground_truth_reader = csv.reader(ground_truth_file)
    next(ground_truth_reader)
    expected_result_reader = csv.reader(expected_result_file)
    next(expected_result_reader) #skip header
    vid_name_gt = [row[0] for row in ground_truth_reader]
    vid_name_exp = [row[0] for row in expected_result_reader]

# Ground True result 파일에서 결과값을 읽어 리스트로 저장
with open(GROUND_TRUE_PATH, 'r') as ground_truth_file, open(RESULT_PATH, 'r') as expected_result_file:
    ground_truth_reader = csv.reader(ground_truth_file)
    next(ground_truth_reader)
    expected_result_reader = csv.reader(expected_result_file)
    next(expected_result_reader) #skip header

    ground_truth = [row[1] for row in ground_truth_reader]
    expected_result = [row[1] for row in expected_result_reader]

print(ground_truth)
print(expected_result)


if vid_name_gt == vid_name_exp: #ground true 파일과 result 파일의 영상 순서가 같은지 확인
    print("[video sequence matching!]")
else:
    print('[video sequence error]')
    print("result & ground true video name isn't matched")
# Initialize variables for true positives, false positives, and false negatives

tp = 0
fp = 0
fn = 0
tn = 0

# Count true positives, false positives, and false negatives
for i in range(len(ground_truth)):
    if ground_truth[i] == 'TRUE':
        ground_truth[i] = 'True' 
    if ground_truth[i] == 'FALSE':
        ground_truth[i] = 'False'  

    if ground_truth[i] == 'True' and expected_result[i] == 'True': # True postive : True를 True로 예측
        tp += 1
    elif ground_truth[i] == 'False' and expected_result[i] == 'False': #True Negative : False 를 False로 예측
        tn += 1
    elif expected_result[i] == 'True': #False Postive : False를 True로 예측
        fp += 1
    elif ground_truth[i] == 'True': # False Negative : True를 False로 예측
        fn += 1
    else:
        print(ground_truth[i], expected_result[i])

# Calculate precision, recall and F1 Score
precision = tp / (tp + fp) #precison 계산식
recall = tp / (tp + fn) #recall 계산식
f1 = 2 * (precision * recall) / (precision + recall) #f1 score 계산식

chart = '{0:>10}{1:>10}{2:>10}'
print(chart.format('','expect F', 'expect_T'))
print(chart.format('result F',tn, fp))
print(chart.format('result T',fn, tp),'\n')
print(f'precision: {precision:.2f}')
print(f'recall: {recall:.2f}')
print(f'F1 Score: {f1:.2f}')
