# How to use the Repository for the Project

This file is a small guide on how to use the repository for review.

## Regarding the Code & Execution

The project setup, based on my presentation & report includes running Likelihood-based Surprise Adequacy (LSA) on MNIST. The LSA values are calculated on the 10.000 Test samples and the 10.000 FGSM adversarial samples (adversial samples are stored in [`adv/`](adv/)).

1. After cloning, with the committed elements, you can run the [`run.py`](run.py) script to execute the project Surprise Adequacy (SA) and Surprise Coverage (SC) calculations (using my model checkpoint from the presentation & report):

    ```bash
    python run.py --lsa -d mnist
    ```

    > Since there is no seeding implemented, i do not recommend to run the [`train_model.py`](train_model.py) without a certain model renaming, since the model will be overwritten otherwise. This is mentioned to ensure getting the same results as in the presentation & report.

2. Then, all Activation Traces (ATs) and predictions will be stored in the [`tmp/`](tmp/) directory for each dataset (train, test, fgsm). The directory [`former_lsa/`](former_lsa/) contains the LSA activations and predictions from the project execution. These were added to provide all files from the project execution. If the required files were already present in the upper [`tmp/`](tmp/) directory itself, the script would skip obtaining the ATs and predictions and directly calculate the SA values. By this, the script will be run properly and calculating the ATs and predictions while reviewing the project. The new calculated ATs and predictions will not differ from the ones in [`former_lsa/`](former_lsa/) by using the same model checkpoint.
3. For each novel input (test/fgsm), the Surprise Adequacy then is calculated.
4. Finally, the Surprise Coverage and other metrics are calculated for each novel dataset (test/fgsm) and stored in [`logs/lsa`](logs/lsa).
5. These results can be visualized by running another terminal using the `tensorboard` command:

    ```bash
    tensorboard --logdir logs/lsa
    ```

   > If you are also interested in the short training run (model saved in `model/`), execute the following command:

    ```bash
    tensorboard --logdir logs/fit
    ```

This provides accuracy and loss metrics for train and validation sets.

## Regarding the presentation & report

The presentation for the project is stored in [`pres/`](pres/), and the report is stored in [`report/`](report/). The required files are available for running the .tex files, but the PDFs are also included for quick access. The report is a long-form version document of the presentation, including many details and explanations regarding the project. Overall, the presentation contains the main points of the report, since the presentation was created after the report for ease of creation.

## AI Usage Disclaimer

According to the [`Selbstständigkeitserklärung.pdf`](Selbstständigkeitserklärung.pdf), the AI-based conversations for the project are included, see [`prompt_conv1.md`](prompt_conv1.md) and [`prompt_conv2.md`](prompt_conv2.md).

All changes done after the AI-based conversations are done by me, and I am responsible for the content of the repository. The diffs based on the conversations are [in this commit](https://github.com/mgrube753/sadl-se4ai/commit/ac2e1851b18af5769ec9c7545f08aeabd6d16992).
