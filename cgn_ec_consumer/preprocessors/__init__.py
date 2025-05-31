from cgn_ec_consumer.preprocessors.generic import (
    filter_keys,
    match_kv,
    match_kvs,
    key_exists,
    exclude_by_kv,
    exclude_by_kvs,
    exclude_by_kv_values,
)


PREPROCESSORS = {
    "filter_keys": filter_keys,
    "match_kv": match_kv,
    "match_kvs": match_kvs,
    "key_exists": key_exists,
    "exclude_by_kv": exclude_by_kv,
    "exclude_by_kvs": exclude_by_kvs,
    "exclude_by_kv_values": exclude_by_kv_values,
}
