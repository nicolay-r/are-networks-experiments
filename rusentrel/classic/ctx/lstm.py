from arekit.contrib.networks.context.configurations.rnn import RNNConfig
from arekit.contrib.networks.tf_helpers.cell_types import CellTypes


def ctx_lstm_custom_config(config):
    assert(isinstance(config, RNNConfig))
    config.modify_cell_type(CellTypes.BasicLSTM)
    config.modify_hidden_size(128)
    config.modify_bags_per_minibatch(2)
    config.modify_dropout_rnn_keep_prob(0.8)
    config.modify_learning_rate(0.1)
    config.modify_terms_per_context(25)
