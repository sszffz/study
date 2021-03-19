from typing import List


def split_list(a: List, chunk_size: int):
    """
    split a large list to small chunk with the specified size
    :param a:
    :param chunk_size:
    :return:
    """
    chunks = []
    list_length = len(a)

    start_pos = 0
    end_pos = start_pos + chunk_size
    while end_pos <= list_length:
        chunks.append(a[start_pos:end_pos])
        start_pos, end_pos = end_pos, end_pos + chunk_size

    if start_pos < list_length:
        chunks.append(a[start_pos:])

    return chunks

