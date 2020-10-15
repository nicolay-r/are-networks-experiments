from arekit.contrib.networks.core.feeding.bags.collection.multi import MultiInstanceBagsCollection
from arekit.contrib.networks.engine import ExperimentEngine
from arekit.contrib.networks.multi.configurations.max_pooling import MaxPoolingOverSentencesConfig
from arekit.contrib.networks.context.architectures.cnn import VanillaCNN
from arekit.contrib.networks.multi.architectures.max_pooling import MaxPoolingOverSentences
from arekit.contrib.networks.context.configurations.cnn import CNNConfig
from rusentrel.classic.ctx.cnn import ctx_cnn_custom_config
from rusentrel.classic.common import classic_common_callback_modification_func, classic_mi_common_config_settings


def mi_cnn_custom_config(config):
    ctx_cnn_custom_config(config.ContextConfig)
    config.fix_context_parameters()


def run_mi_testing_cnn(experiment,
                       load_model,
                       network_classtype=MaxPoolingOverSentences,
                       config_classtype=MaxPoolingOverSentencesConfig,
                       custom_config_func=mi_cnn_custom_config,
                       custom_callback_func=classic_common_callback_modification_func):

    ExperimentEngine.run_testing(
        experiment=experiment,
        load_model=load_model,
        create_network=lambda: network_classtype(context_network=VanillaCNN()),
        create_config=lambda: config_classtype(context_config=CNNConfig()),
        common_callback_modification_func=custom_callback_func,
        custom_config_modification_func=custom_config_func,
        bags_collection_type=MultiInstanceBagsCollection,
        common_config_modification_func=classic_mi_common_config_settings)
