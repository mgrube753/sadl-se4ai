#### New file for visualizing 1 normal and 1 adversarial sample with their predictions
import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import mnist
from keras.models import load_model


def predict_samples(index):
    model = load_model("model/model_mnist.h5")

    (_, _), (x_test, y_test) = mnist.load_data()
    x_test = (x_test.astype("float32") / 255.0).reshape(-1, 28, 28, 1)
    x_test_adv = np.load("adv/adv_mnist_fgsm.npy")

    pred_normal = model.predict(x_test[index : index + 1])
    pred_fgsm = model.predict(x_test_adv[index : index + 1])
    true_label = y_test[index]

    _, axes = plt.subplots(2, 2, figsize=(12, 10))
    classes = range(10)

    ax = axes[0, 0]
    ax.imshow(x_test[index].reshape(28, 28), cmap="gray")
    ax.set_title("Normal MNIST Sample\nGround Truth: {}".format(true_label))
    ax.axis("off")

    ax = axes[0, 1]
    ax.bar(classes, pred_normal[0])
    ax.set_xlabel("Class")
    ax.set_ylabel("Probability")
    ax.set_title(
        "Normal Prediction\nClass: {}, Confidence: {:.4f}".format(
            np.argmax(pred_normal[0]), np.max(pred_normal[0])
        )
    )
    ax.set_xticks(classes)

    ax = axes[1, 0]
    ax.imshow(x_test_adv[index].reshape(28, 28), cmap="gray")
    ax.set_title("FGSM Adversarial Sample")
    ax.axis("off")

    ax = axes[1, 1]
    ax.bar(classes, pred_fgsm[0])
    ax.set_xlabel("Class")
    ax.set_ylabel("Probability")
    ax.set_title(
        "FGSM Prediction\nClass: {}, Confidence: {:.4f}".format(
            np.argmax(pred_fgsm[0]), np.max(pred_fgsm[0])
        )
    )
    ax.set_xticks(classes)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    predict_samples(8)

####
