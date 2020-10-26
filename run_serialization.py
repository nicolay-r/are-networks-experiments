import argparse

from arekit.contrib.networks.core.io_utils import NetworkIOUtils
from common import Common

from arekit.contrib.networks.run_serializer import NetworksExperimentInputSerializer
from arekit.contrib.source.rusentrel.io_utils import RuSentRelVersions
from serialization_data import RuSentRelSerializationData

from args.cv_index import CvCountArg
from args.experiment import ExperimentTypeArg
from args.labels_count import LabelsCountArg
from args.ra_ver import RuAttitudesVersionArg

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Data serializer (train/test) for further experiments organization")

    # Providing arguments.
    RuAttitudesVersionArg.add_argument(parser)
    CvCountArg.add_argument(parser)
    ExperimentTypeArg.add_argument(parser)
    LabelsCountArg.add_argument(parser)

    # Parsing arguments.
    args = parser.parse_args()

    # Reading arguments.
    exp_type = ExperimentTypeArg.read_argument(args)
    ra_version = RuAttitudesVersionArg.read_argument(args)
    cv_count = CvCountArg.read_argument(args)
    labels_count = LabelsCountArg.read_argument(args)
    io_utils = NetworkIOUtils

    # Preparing necesary structures for further initializations.
    labels_scaler = Common.create_labels_scaler(labels_count)
    experiment_data = RuSentRelSerializationData(labels_scaler=labels_scaler)

    experiment = Common.create_experiment(exp_type=exp_type,
                                          experiment_data=experiment_data,
                                          cv_count=cv_count,
                                          rusentrel_version=RuSentRelVersions.V11,
                                          ruattitudes_version=ra_version)

    cv_folding_algo = Common.create_folding_algorithm(
        doc_operations=experiment.DocumentOperations,
        data_dir=experiment_data.get_data_root())
    experiment_data.set_cv_folding_algorithm(cv_folding_algo)
    experiment_data.CVFoldingAlgorithm.set_cv_count(cv_count)

    # Performing serialization process.
    serialization_engine = NetworksExperimentInputSerializer(experiment=experiment,
                                                             skip_folder_if_exists=True,
                                                             io_utils=io_utils)

    serialization_engine.run()
