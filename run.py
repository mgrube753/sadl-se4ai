import numpy as np
import time
import argparse

#### change start ------------------------------------------------------------
import matplotlib.pyplot as plt
import tensorflow as tf
import datetime
import io

#### change end --------------------------------------------------------------

from tqdm import tqdm
from keras.datasets import mnist, cifar10
from keras.models import load_model, Model
from sa import fetch_dsa, fetch_lsa, get_sc
from utils import *

CLIP_MIN = -0.5
CLIP_MAX = 0.5

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--d", "-d", help="Dataset", type=str, default="mnist")
    parser.add_argument(
        "--lsa", "-lsa", help="Likelihood-based Surprise Adequacy", action="store_true"
    )
    parser.add_argument(
        "--dsa", "-dsa", help="Distance-based Surprise Adequacy", action="store_true"
    )
    parser.add_argument(
        "--target",
        "-target",
        help="Target input set (test or adversarial set)",
        type=str,
        default="fgsm",
    )
    parser.add_argument(
        "--save_path", "-save_path", help="Save path", type=str, default="./tmp/"
    )
    parser.add_argument(
        "--batch_size", "-batch_size", help="Batch size", type=int, default=128
    )
    parser.add_argument(
        "--var_threshold",
        "-var_threshold",
        help="Variance threshold",
        type=int,
        default=1e-5,
    )
    parser.add_argument(
        "--upper_bound", "-upper_bound", help="Upper bound", type=int, default=2000
    )
    parser.add_argument(
        "--n_bucket",
        "-n_bucket",
        help="The number of buckets for coverage",
        type=int,
        default=1000,
    )
    parser.add_argument(
        "--num_classes",
        "-num_classes",
        help="The number of classes",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--is_classification",
        "-is_classification",
        help="Is classification task",
        type=bool,
        default=True,
    )
    args = parser.parse_args()
    assert args.d in ["mnist", "cifar"], "Dataset should be either 'mnist' or 'cifar'"
    assert args.lsa ^ args.dsa, "Select either 'lsa' or 'dsa'"
    print(args)

    if args.d == "mnist":
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x_train = x_train.reshape(-1, 28, 28, 1)
        x_test = x_test.reshape(-1, 28, 28, 1)

        # Load pre-trained model.
        model = load_model("./model/model_mnist.h5")
        model.summary()

        # You can select some layers you want to test.
        # layer_names = ["activation_1"]
        # layer_names = ["activation_2"]
        layer_names = ["activation_3"]

        # Load target set.
        x_target = np.load("./adv/adv_mnist_{}.npy".format(args.target))

    #### change start -----------------------------------------------------------
    # elif args.d == "cifar":
    #     (x_train, y_train), (x_test, y_test) = cifar10.load_data()

    #     model = load_model("./model/model_cifar.h5")
    #     model.summary()

    #     # layer_names = [
    #     #     layer.name
    #     #     for layer in model.layers
    #     #     if ("activation" in layer.name or "pool" in layer.name)
    #     #     and "activation_9" not in layer.name
    #     # ]
    #     layer_names = ["activation_6"]

    #     x_target = np.load("./adv/adv_cifar_{}.npy".format(args.target))
    #### change end -----------------------------------------------------------

    x_train = x_train.astype("float32")
    x_train = (x_train / 255.0) - (1.0 - CLIP_MAX)
    x_test = x_test.astype("float32")
    x_test = (x_test / 255.0) - (1.0 - CLIP_MAX)

    if args.lsa:
        test_lsa = fetch_lsa(model, x_train, x_test, "test", layer_names, args)

        target_lsa = fetch_lsa(model, x_train, x_target, args.target, layer_names, args)

        #### change start (get FGSM / Test and Mix coverage) ----------------------
        lower_bound = min(np.amin(test_lsa), np.amin(target_lsa))
        test_cov = get_sc(lower_bound, args.upper_bound, args.n_bucket, test_lsa)
        target_cov = get_sc(lower_bound, args.upper_bound, args.n_bucket, target_lsa)

        combined_lsa = np.concatenate((test_lsa, target_lsa))
        combined_cov = get_sc(
            lower_bound, args.upper_bound, args.n_bucket, combined_lsa
        )
        #### change end -----------------------------------------------------------

        auc = compute_roc_auc(test_lsa, target_lsa)
        #### change start (add mean/std prints) ------------------------------------------
        print(
            infog(
                "Test - Mean: "
                + str(np.mean(test_lsa))
                + ", Std: "
                + str(np.std(test_lsa))
            )
        )
        print(
            infog(
                "FGSM - Mean: "
                + str(np.mean(target_lsa))
                + ", Std: "
                + str(np.std(target_lsa))
            )
        )
        #### change end -----------------------------------------------------------
        print(infog("ROC-AUC: " + str(auc * 100)))

        #### change start (add TensorBoard logging and prints) --------------------
        log_dir_base = "logs/lsa/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        writer_test = tf.summary.FileWriter(log_dir_base + "/test")
        writer_target = tf.summary.FileWriter(log_dir_base + "/target_" + args.target)

        plt.figure(figsize=(6, 4))
        plt.hist(
            test_lsa,
            bins=50,
            histtype="step",
            linewidth=2,
            label="Test",
            density=True,
            range=(min(np.min(test_lsa), np.min(target_lsa)), 200),
        )
        plt.hist(
            target_lsa,
            bins=50,
            histtype="step",
            linewidth=2,
            label="Target",
            density=True,
            range=(min(np.min(test_lsa), np.min(target_lsa)), 200),
        )
        plt.xlim(right=200)
        plt.title("LSA Distribution")
        plt.legend(loc="upper right")

        buf_lsa = io.BytesIO()
        plt.savefig(buf_lsa, format="png")
        plt.close()
        buf_lsa.seek(0)

        img_summary_lsa = tf.Summary.Image(encoded_image_string=buf_lsa.getvalue())
        writer_test.add_summary(
            tf.Summary(
                value=[
                    tf.Summary.Value(
                        tag="LSA_Overall_Overlay/All_Classes", image=img_summary_lsa
                    )
                ]
            ),
            0,
        )

        writer_test.add_summary(
            tf.Summary(
                value=[
                    tf.Summary.Value(
                        tag="LSA_Mean_Overall", simple_value=np.mean(test_lsa)
                    )
                ]
            ),
            0,
        )
        writer_target.add_summary(
            tf.Summary(
                value=[
                    tf.Summary.Value(
                        tag="LSA_Mean_Overall", simple_value=np.mean(target_lsa)
                    )
                ]
            ),
            0,
        )

        test_lsa_np = np.array(test_lsa)
        target_lsa_np = np.array(target_lsa)

        for c in range(args.num_classes):
            class_filter = y_test == c
            class_test_lsa = test_lsa_np[class_filter]
            class_target_lsa = target_lsa_np[class_filter]

            plt.figure(figsize=(6, 4))

            min_val = min(np.min(class_test_lsa), np.min(class_target_lsa))
            plt.hist(
                class_test_lsa,
                bins=50,
                histtype="step",
                linewidth=2,
                label="Test",
                density=True,
                range=(min_val, 200),
            )
            plt.hist(
                class_target_lsa,
                bins=50,
                histtype="step",
                linewidth=2,
                label="Target",
                density=True,
                range=(min_val, 200),
            )
            plt.xlim(right=200)
            plt.title("LSA Class {}".format(c))
            plt.legend(loc="upper right")

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)

            img_summary = tf.Summary.Image(encoded_image_string=buf.getvalue())
            writer_test.add_summary(
                tf.Summary(
                    value=[
                        tf.Summary.Value(
                            tag="LSA_Class_Overlay/Class_{}".format(c),
                            image=img_summary,
                        )
                    ]
                ),
                0,
            )

            mean_class_test = tf.Summary(
                value=[
                    tf.Summary.Value(
                        tag="LSA_Mean_Per_Class/Class_{}".format(c),
                        simple_value=np.mean(class_test_lsa),
                    )
                ]
            )
            writer_test.add_summary(mean_class_test, 0)

            mean_class_target = tf.Summary(
                value=[
                    tf.Summary.Value(
                        tag="LSA_Mean_Per_Class/Class_{}".format(c),
                        simple_value=np.mean(class_target_lsa),
                    )
                ]
            )
            writer_target.add_summary(mean_class_target, 0)

            auc_summary = tf.Summary(
                value=[tf.Summary.Value(tag="Metrics/ROC-AUC", simple_value=auc * 100)]
            )
            writer_test.add_summary(auc_summary, 0)

            test_cov_summary = tf.Summary(
                value=[tf.Summary.Value(tag="Coverage", simple_value=test_cov)]
            )
            writer_test.add_summary(test_cov_summary, 0)

            target_cov_summary = tf.Summary(
                value=[tf.Summary.Value(tag="Coverage", simple_value=target_cov)]
            )
            writer_target.add_summary(target_cov_summary, 0)

            combined_cov_summary = tf.Summary(
                value=[tf.Summary.Value(tag="Coverage", simple_value=combined_cov)]
            )
            writer_test.add_summary(combined_cov_summary, 0)

        writer_test.flush()
        writer_target.flush()
        writer_test.close()
        writer_target.close()
        #### change end ---------------------------------------------------------------

    #### change start
    # if args.dsa:
    #     test_dsa = fetch_dsa(model, x_train, x_test, "test", layer_names, args)

    #     target_dsa = fetch_dsa(model, x_train, x_target, args.target, layer_names, args)
    #     target_cov = get_sc(
    #         np.amin(target_dsa), args.upper_bound, args.n_bucket, target_dsa
    #     )

    #     auc = compute_roc_auc(test_dsa, target_dsa)
    #     print(infog("ROC-AUC: " + str(auc * 100)))
    #### change end

    #### change start (print all coverages) --------------------------------------
    print(infog("------\n{} coverage: ".format(args.target) + str(target_cov)))
    print(infog("test coverage: " + str(test_cov)))
    print(infog("combined test+{} coverage: ".format(args.target) + str(combined_cov)))
    #### change end --------------------------------------------------------------
