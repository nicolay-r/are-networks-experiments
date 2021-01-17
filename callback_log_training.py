import datetime
from dateutil import parser


def get_message(epoch_index, avg_fit_cost, avg_fit_acc):
    """ Providing logging message
    """
    return u"{}: Epoch: {}: avg_fit_cost: {:.3f}, avg_fit_acc: {:.3f}".format(
        str(datetime.datetime.now()),
        epoch_index,
        avg_fit_cost,
        avg_fit_acc)


def extract_last_acc_from_training_log(filepath):
    acc = 0
    with open(filepath, 'r') as f:
        for line in f.readlines():
            acc = float(line.split(u'avg_fit_acc: ')[-1])

    return acc


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def extract_avg_epoch_time_from_training_log(filepath):
    times = []
    with open(filepath, 'r') as f:
        for line in f.readlines():
            string_time = line.split(u': ')[0]
            times.append(parser.parse(string_time))

    deltas = []
    for e_index in range(1, len(times)-1):
        deltas.append(times[e_index+1] - times[e_index])

    if len(deltas) > 0:
        # NOTE. due to that the time may consider
        # computations of other operations therefore
        # we cannot gauaratee the correctness.
        # Hence we providing the minimal time.
        return chop_microseconds(sorted(deltas)[0])
    else:
        # Providing 0 by default otherwise.
        return datetime.timedelta()


def parse_float_network_parameter(filepath, param_name):
    # ['base:current_time', datetime.datetime(2020, 12, 30, 9, 30, 6, 531903)]
    # ['base:use_class_weights', True]
    # ['base:dropout (keep prob)', 0.8]
    # ['base:classes_count', 3]
    # ['base:class_weights', [33.333333333333336, 33.333333333333336, 33.333333333333336]]
    # ['base:terms_per_context', 50]

    value = 0
    with open(filepath, 'r') as f:
        for line in f.readlines():
            if param_name not in line:
                continue

            # removing brackets
            line = line.strip()
            line = line[1:-1]
            # extracting value
            value = float(line.split(',')[-1])

    return value


