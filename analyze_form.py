import numpy as np
import pandas as pd

words2index = {
    1: {  # Patrick
    'не согласен': 1,
    'скорее не согласен': 2,
    'скорее согласен': 3,
    'согласен': 4
    },
    2 : {  # big 5
    'не согласен': 1,
    'скорее не согласен': 2,
    'безразличен': 3,
    'скорее согласен': 4,
    'согласен': 5
    },
    3: {  # Sadism
    'не согласен': 1,
    'скорее не согласен': 2,
    'не могу согласиться или не согласиться': 3,
    'скорее согласен': 4,
    'согласен': 5
    },
    4: {  # Barrat
    'почти никогда/никогда': 1,
    'иногда': 2,
    'часто': 3,
    'почти всегда/всегда': 4
    },
    5 : {  # anti-social
    'никогда': 1,
    'практически никогда': 2,
    'иногда': 3,
    'часто': 4,
    'практически все время': 5
    },
    6: {  # Davis
    'не согласен': 1,
    'скорее не согласен': 2,
    'скорее согласен': 3,
    'согласен': 4
    },
    7: {  # triada
    'не согласен': 1,
    'скорее не согласен': 2,
    'скорее согласен': 3,
    'согласен': 4
    },
    8: {  # agression
    'не согласен': 1,
    'скорее не согласен': 2,
    'скорее согласен': 3,
    'согласен': 4
    }
}

index2quiz_name = {
    1: 'Patrick',
    2: 'Big5',
    3: 'CAST',
    4: 'Barrat',
    5: 'Antisocial Behavior',
    6: 'Davis',
    7: 'SD3',
    8: 'Bass-Perry'
}

quiz_name2index = {}
for key, val in index2quiz_name.items():
    quiz_name2index[val] = key

def process_quiz(answers, columns, quiz_name):
    # read excel with codes and scales
    xls = pd.ExcelFile('./scales.xlsx')
    scales_codes = pd.read_excel(xls, quiz_name)
    scales_codes.columns = map(str.lower, scales_codes.columns)

    answers_array = np.array(answers)

    # use codes
    if 'codes' in scales_codes:
        codes = scales_codes['code'].to_numpy()
        number_of_answers = len(words2index[quiz_name2index[quiz_name]].keys())
        answers_array[codes == 'f', :] = number_of_answers + 1 - answers_array[codes == 'f', :]

    # use scales
    if 'scale' in scales_codes:
        scales = scales_codes['scale'].to_numpy()
        unique_scales = np.unique(scales)
        scale_sums = np.zeros((len(unique_scales), answers_array.shape[1]))
        for index, scale in enumerate(unique_scales):
            columns.append(scale)
            scale_sums[index] = np.sum(answers_array[scales == scale, :], axis=0)

        answers_array = np.concatenate((answers_array, scale_sums), axis=0)

    columns.append('global')
    answers_array = np.concatenate(
        (answers_array, np.sum(answers_array, axis=0, keepdims=True)),
        axis=0)

    pd.DataFrame(data=answers_array.T, columns=columns).to_excel(
        './{}.xlsx'.format(quiz_name))

if __name__ == '__main__':
    data = pd.read_csv('psy.csv', )

    quiz_num = 1
    question_num = 1

    print(index2quiz_name[quiz_num])

    output_cols = []
    output_answers = []

    for column in data.columns[5:]:
        column_name = column.replace('[', '').replace(']', '')
        num, *question = column_name.split('.')
        num = int(num)
        question = ''.join(question)

        if num != question_num:
            process_quiz(output_answers, output_cols, index2quiz_name[quiz_num])

            output_answers = []
            output_cols = []

            quiz_num += 1
            print(index2quiz_name[quiz_num])
            question_num = num

        output_cols.append(column_name)
        output_answers.append([])

        question_num += 1

        for val in data[column].values:
            val_str = ''
            if isinstance(val, str):
                val_str = val.lower()
                assert val_str in words2index[quiz_num].keys(), "answer wasn't converted to int!"
                output_answers[-1].append(words2index[quiz_num][val_str])
