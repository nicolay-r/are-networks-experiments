import argparse

from arekit.common.evaluation.evaluators.two_class import TwoClassEvaluator
from arekit.contrib.networks.core.nn_io import NeuralNetworkModelIO
from arekit.contrib.networks.run_training import NetworksTrainingEngine
from args.cv_index import CvCountArg
from args.experiment import ExperimentTypeArg, SUPERVISED_LEARNING, SUPERVISED_LEARNING_WITH_DS
from args.labels_count import LabelsCountArg
from args.ra_ver import RuAttitudesVersionArg
from args.rusentrel import RuSentRelVersionArg
from args.stemmer import StemmerArg
from common import Common
# TODO. Move this parameters into args/input_format.py
from data_training import RuSentRelTrainingData
from factory_networks import \
    INPUT_TYPE_SINGLE_INSTANCE, \
    INPUT_TYPE_MULTI_INSTANCE, \
    INPUT_TYPE_MULTI_INSTANCE_WITH_ATTENTION, \
    compose_network_and_network_config_funcs, \
    create_bags_collection_type
from factory_config_setups import get_custom_config_func, get_common_config_func
from rusentrel.classic.common import classic_common_callback_modification_func
from rusentrel.callback_utils import classic_cv_common_callback_modification_func, \
    ds_cv_common_callback_modification_func
from rusentrel.ctx_names import ModelNames
from rusentrel.rusentrel_ds.common import ds_common_callback_modification_func


def supported_model_names():
    model_names = ModelNames()
    return [
        model_names.SelfAttentionBiLSTM,
        model_names.AttSelfPZhouBiLSTM,
        model_names.AttSelfZYangBiLSTM,
        model_names.BiLSTM,
        model_names.CNN,
        model_names.LSTM,
        model_names.PCNN,
        model_names.RCNN,
        model_names.RCNNAttZYang,
        model_names.RCNNAttPZhou
    ]


def get_callback_func(exp_type, cv_count):
    assert(isinstance(cv_count, int))

    if exp_type == SUPERVISED_LEARNING:
        if cv_count == 1:
            return classic_common_callback_modification_func
        else:
            return classic_cv_common_callback_modification_func
    if exp_type == SUPERVISED_LEARNING_WITH_DS:
        if cv_count == 1:
            return ds_common_callback_modification_func
        else:
            return ds_cv_common_callback_modification_func


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Data serializer (train/test) for further experiments organization")

    # Composing cmd arguments.
    RuAttitudesVersionArg.add_argument(parser)
    CvCountArg.add_argument(parser)
    LabelsCountArg.add_argument(parser)
    ExperimentTypeArg.add_argument(parser)
    RuSentRelVersionArg.add_argument(parser)
    StemmerArg.add_argument(parser)

    parser.add_argument('--model-input-type',
                        dest='model_input_type',
                        type=unicode,
                        choices=[INPUT_TYPE_SINGLE_INSTANCE,
                                 INPUT_TYPE_MULTI_INSTANCE,
                                 INPUT_TYPE_MULTI_INSTANCE_WITH_ATTENTION],
                        default='ctx',
                        nargs='?',
                        help='Input format type')

    parser.add_argument('--model-name',
                        dest='model_name',
                        type=unicode,
                        choices=supported_model_names(),
                        nargs=1,
                        help='Name of a model to be utilized in experiment')

    parser.add_argument('--model-state-dir',
                        dest='model_load_dir',
                        type=unicode,
                        default=None,
                        nargs='?',
                        help='Use pretrained state as initial')

    # Parsing arguments.
    args = parser.parse_args()

    # Reading arguments.
    exp_type = ExperimentTypeArg.read_argument(args)
    labels_count = LabelsCountArg.read_argument(args)
    rusentrel_version = RuSentRelVersionArg.read_argument(args)
    cv_count = CvCountArg.read_argument(args)
    ra_version = RuAttitudesVersionArg.read_argument(args)
    stemmer = StemmerArg.read_argument(args)
    model_input_type = args.model_input_type
    model_load_dir = args.model_load_dir
    model_name = unicode(args.model_name[0])

    # init handler
    callback_func = get_callback_func(exp_type=exp_type, cv_count=cv_count)
    bags_collection_type = create_bags_collection_type(model_input_type=model_input_type)
    common_config_func = get_common_config_func(exp_type=exp_type, model_input_type=model_input_type)
    custom_config_func = get_custom_config_func(model_name=model_name, model_input_type=model_input_type)
    network, network_config = compose_network_and_network_config_funcs(model_name=model_name,
                                                                       model_input_type=model_input_type)

    # Creating experiment
    evaluator = TwoClassEvaluator()
    experiment_data = RuSentRelTrainingData(labels_scaler=Common.create_labels_scaler(labels_count),
                                            stemmer=stemmer,
                                            opinion_formatter=Common.create_opinion_collection_formatter(),
                                            evaluator=evaluator)

    experiment = Common.create_experiment(exp_type=exp_type,
                                          experiment_data=experiment_data,
                                          cv_count=cv_count,
                                          rusentrel_version=rusentrel_version,
                                          ruattitudes_version=ra_version)

    model_io = NeuralNetworkModelIO(full_model_name=Common.create_full_model_name(exp_type=exp_type,
                                                                                  cv_count=cv_count,
                                                                                  model_name=model_name),
                                    target_dir=experiment.ExperimentIO.get_target_dir(),
                                    source_dir=model_load_dir)

    experiment_data.set_model_io(model_io)

    training_engine = NetworksTrainingEngine(load_model=model_load_dir is not None,
                                             experiment=experiment,
                                             create_network_func=network,
                                             create_config=network_config,
                                             bags_collection_type=bags_collection_type,
                                             custom_config_modification_func=custom_config_func,
                                             common_config_modification_func=common_config_func,
                                             common_callback_modification_func=callback_func)

    training_engine.run()
