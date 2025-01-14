import matplotlib
import numpy

matplotlib.use('Agg')
import matplotlib.pyplot as plt

import sys

from AdaFair import AdaFair

sys.path.insert(0, 'DataPreprocessing')
sys.path.insert(0, 'equalized_odds_and_calibration-master')

# import funcs_disp_mist as fdm

from Competitors.AdaCost import AdaCostClassifier
from load_kdd import load_kdd
# from load_german import load_german
from load_compas_data import load_compas
from load_adult import load_adult
from load_bank import load_bank


def run_eval(dataset):

    if dataset == "compass-gender":
        X, y, sa_index, p_Group, x_control = load_compas("sex")
    elif dataset == "compass-race":
        X, y, sa_index, p_Group, x_control = load_compas("race")
    elif dataset == "adult-gender":
        X, y, sa_index, p_Group, x_control = load_adult("sex")
    elif dataset == "bank":
        X, y, sa_index, p_Group, x_control = load_bank()
    elif dataset == "kdd":
        X, y, sa_index, p_Group, x_control = load_kdd()
    else:
        exit(1)


    base_learners = 200
    adaboost, adaboost_weights, init_weights = train_classifier(X,  y, sa_index, p_Group, 0, base_learners )
    csb1, csb1_weights, temp= train_classifier(X, y, sa_index, p_Group, 1, base_learners )
    csb2, csb2_weights, temp = train_classifier(X, y, sa_index, p_Group, 2, base_learners )

    adaboost *= y
    csb1 *= y
    csb2 *= y

    csb1_positives = csb1[y==1]
    csb1_negatives = csb1[y==-1]

    csb2_positives = csb2[y==1]
    csb2_negatives = csb2[y==-1]

    adaboost_positives = adaboost[y==1]
    adaboost_negatives = adaboost[y==-1]


    num_bins = 50
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12,3))
    # fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(14,3))
    plt.rcParams.update({'font.size': 11})


    ax1.set_title( "Positive CDF")
    ax1.grid(True)
    counts_ada_positives, bin_edges_ada_positives = numpy.histogram(adaboost_positives, bins=num_bins, normed=True)
    cdf_ada_positives = numpy.cumsum(counts_ada_positives)
    ax1.plot(bin_edges_ada_positives[1:], cdf_ada_positives/ cdf_ada_positives[-1], c='blue', label= 'AdaBoost')

    counts_csb1_positives, bin_edges_csb1_positives = numpy.histogram(csb1_positives, bins=num_bins, normed=True)
    cdf_csb1_positives = numpy.cumsum(counts_csb1_positives)
    ax1.plot(bin_edges_csb1_positives[1:], cdf_csb1_positives / cdf_csb1_positives[-1], c='green', linestyle='-.',label='AdaFair NoConf')

    counts_csb2_positives, bin_edges_csb2_positives = numpy.histogram(csb2_positives, bins=num_bins, normed=True)
    cdf_csb2_positives = numpy.cumsum(counts_csb2_positives)
    ax1.plot(bin_edges_csb2_positives[1:], cdf_csb2_positives / cdf_csb2_positives[-1], c='red', linestyle='--', label='AdaFair')
    ax1.legend(loc='best')
    ax1.set_xlabel("Margin")

    ax1.set_ylabel("Cumulative Distribution")
    ax1.axhline(0, color='black')
    ax1.axvline(0, color='black')



    ax2.grid(True)

    ax2.axhline(0, color='black')
    ax2.axvline(0, color='black')
    ax2.set_title("Negative CDF")

    counts_ada_negatives, bin_edges_ada_negatives = numpy.histogram(adaboost_negatives, bins=num_bins, normed=True)
    cdf_ada_negatives = numpy.cumsum(counts_ada_negatives)
    ax2.plot(bin_edges_ada_negatives[1:], cdf_ada_negatives / cdf_ada_negatives[-1], c='blue',
            label='AdaBoost')
    ax2.set_ylabel("Cumulative Distribution")
    ax2.set_xlabel("Margin")

    counts_csb1_negatives, bin_edges_csb1_negatives = numpy.histogram(csb1_negatives, bins=num_bins, normed=True)
    cdf_csb1_negatives = numpy.cumsum(counts_csb1_negatives)
    ax2.plot(bin_edges_csb1_negatives[1:], cdf_csb1_negatives/ cdf_csb1_negatives[-1], c='green', linestyle='-.',label='AdaFair NoConf')
    counts_csb2_negatives, bin_edges_csb2_negatives = numpy.histogram(csb2_negatives, bins=num_bins, normed=True)
    cdf_csb2_negatives= numpy.cumsum(counts_csb2_negatives)
    ax2.plot(bin_edges_csb2_negatives[1:], cdf_csb2_negatives/ cdf_csb2_negatives[-1], c='red', linestyle='--', label='AdaFair')
    ax2.legend(loc='best')



    # index = numpy.arange(4)
    # bar_width = 0.2
    #
    # adaboost_weights = adaboost_weights.split(",")
    # init_weights = init_weights.split(",")
    # csb1_weights = csb1_weights.split(",")
    # csb2_weights = csb2_weights.split(",")
    #
    # ax3.set_title("Weights per group")
    # # ax3.set_ylabel("(%)")
    #
    #
    # prot_pos = [float(init_weights[4]), float(adaboost_weights[4]), float(csb1_weights[4]), float(csb2_weights[4])]
    # non_prot_pos = [float(init_weights[5]), float(adaboost_weights[5]), float(csb1_weights[5]), float(csb2_weights[5])]
    # prot_neg = [float(init_weights[6]), float(adaboost_weights[6]), float(csb1_weights[6]), float(csb2_weights[6])]
    # non_prot_neg = [float(init_weights[7]), float(adaboost_weights[7]), float(csb1_weights[7]), float(csb2_weights[7])]
    #
    # ax3.bar(index, prot_pos,label='Prot. Pos.', edgecolor='black', width= bar_width)
    # ax3.bar(index, non_prot_pos,label='Non-Prot. Pos.', bottom=prot_pos, edgecolor='red', width= bar_width)
    # ax3.bar(index, prot_neg,label='Prot. Neg.', bottom=[i+j for i,j in zip(prot_pos, non_prot_pos)],  edgecolor='green', width= bar_width)
    # ax3.bar(index, non_prot_neg,label='Non-Prot. Neg.', bottom=[i+j+z for i,j,z in zip(prot_pos, non_prot_pos, prot_neg)],  edgecolor='blue', width= bar_width)
    #
    #
    #
    # ax3.set_xticks([0  , 1 , 2 , 3 ])
    # ax3.grid(True)
    #
    # ax3.set_xticklabels(['Initial Weights','AdaBoost', 'AdaFair NoConf.', 'AdaFair'])
    # ax3.legend(loc='best', fancybox=True, framealpha=0.1)
    # plt.yticks(numpy.arange(0, 1.0001, step=0.1))

    # ax3.set_ylim([0.48, 0.52])
    # plt.rcParams.update({'font.size': 9})

    fig.tight_layout()

    plt.show()


    plt.legend(loc='best',fancybox=True, framealpha=0.2)
    plt.savefig("Images/cdf_" +dataset  + ".png")

def train_classifier(X_train, y_train, sa_index, p_Group, mode, base_learners):
    if mode == 0:
        classifier = AdaCostClassifier(saIndex=sa_index, saValue=p_Group, n_estimators=base_learners, CSB="CSB1", debug=True)
    elif mode == 1:
        classifier = AdaFair(n_estimators=base_learners, saIndex=sa_index, saValue=p_Group, CSB="CSB1", debug=True, c=1)
    elif mode == 2:
        classifier = AdaFair(n_estimators=base_learners, saIndex=sa_index, saValue=p_Group, CSB="CSB2", debug=True, c=1)

    classifier.fit(X_train, y_train)

    return classifier.conf_scores, classifier.get_weights_over_iterations(), classifier.get_initial_weights()


def main(dataset):
    run_eval(dataset)


if __name__ == '__main__':
    # main("compass-gender")
    # main("adult-gender")
    # main("bank")
    main("kdd")
