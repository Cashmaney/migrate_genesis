import json
from migrate import convert_prefix, replace_values, replace_keys, fix_staking_amounts


def test_convert_bech():
    in_addr = "enigma130wzdjl6yg70knj9y6k92euksc39t4g2qcqawp"

    expected = "secret130wzdjl6yg70knj9y6k92euksc39t4g2n4dgkl"

    result = convert_prefix(in_addr)

    assert result == expected


def test_parse_json():
    with open('C:\\Users\\Itzik\\PycharmProjects\\migrate_genesis\\state_new.json', encoding="utf-8") as f:
        as_json = json.load(f)

    result = replace_values(as_json)
    result = replace_keys(result)
    result = fix_staking_amounts(result)

    with open('C:\\Users\\Itzik\\PycharmProjects\\migrate_genesis\\state_conv.json', 'w', encoding="utf-8") as f:
        json.dump(result, f)
