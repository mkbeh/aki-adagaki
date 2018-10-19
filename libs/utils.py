# -*- coding: utf-8 -*-
import logging


def logger(msg, file):
    """
    Func which logging message into file.
    :param msg:
    :param file:
    :return:
    """
    logging.basicConfig(filename=file, level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info(msg)


def values_comparison(val1, val2):
    """
    Func which comparison values and return tuple.
    :param val1:
    :param val2:
    :return:
    """
    return (val1, val2) if val1 < val2 else (val1, val2 + 1)


def split_on_ranges(num, num_ranges, btt_specified=1):
    """
    Func which split number on list of ranges.
    :param num: Number which need split on ranges.
    :param num_ranges: Number of ranges on which need to split number.
    :param btt_specified: Just btt specified param. Need for get correct page num.
    :return:
    """
    last_range = num % num_ranges
    ranges_lst = []

    a = ((num - last_range) / num_ranges * btt_specified).__round__()
    c = a

    for i in range(num_ranges):
        e = 0 if i == 0 else btt_specified
        ranges_lst.append((c - a + e, c))

        if i == num_ranges - 1 and last_range != 0:
            ranges_lst.append(values_comparison(c + btt_specified, c + last_range * btt_specified))

        else:
            c += a

    return ranges_lst

