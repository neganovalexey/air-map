import os
import numpy as np

if __name__ == '__main__':
    for fname in os.listdir('static/csvs/'):
        if fname.endswith('.csv'):
            with open('static/csvs/' + fname) as fr:
                lines = [l.strip().split(',') for l in fr]
            lines = lines[1:]
            v_max = np.max([float(l[1]) for l in lines])
            v_min = np.min([float(l[1]) for l in lines])
            lines_new = [[l[0], str((float(l[1]) - v_min) * 100 / (v_max - v_min)), l[2], l[3]] for l in lines]
            with open('static/csvs/' + 'n_' + fname, 'w') as fw:
                for l in lines_new:
                    fw.write(','.join(l) + '\n')
