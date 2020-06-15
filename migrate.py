#! /usr/bin/python3
import json
import sys
import bech32

from typing import Dict, List

replaceable_map = \
    ["enigma1", "enigmapub1", "enigmavaloper1", "enigmavaloperpub1", "enigmavalcons1", "enigmavalconspub1"]

conversion_map = {"enigma": "secret",
                  "enigmapub": "secretpub",
                  "enigmavaloper": "secretvaloper",
                  "enigmavaloperpub": "secretvaloperpub",
                  "enigmavalcons": "secretvalcons",
                  "enigmavalconspub": "secretvalconspub"}

SOURCE_CHAIN_ID = "enigma-1"
TARGET_CHAIN_ID = "secret-1"

genesis_tokenswap_params = {
    "params": {
        "minting_approver_address": "secret1n4pc2w3us9n4axa0ppadd3kv3c0sar8cxl30wq",
        "minting_enabled": False,
        "minting_multiplier": "1.000000000000000000",
        "swaps": None
    }
}


staking_amounts_to_fix: Dict[str, List[Dict[str, str]]] = {
    "secret1tjmq3dqxkd8gak30qwtdq5pwtuyfl7ypkss8l7": [{"old_amnt": "3500404.000004584539591600", "new_amnt": "3465400.027519803049775553"},],
    "secret1v0uwr4d9wznqnlp3y57chk8pume59mnhupnvh2": [{"old_amnt": "999989999.999999999999999999", "new_amnt": "989990119.287656282774184652"},],
    "secret146v4v2wsgnu4dv9phhtrfcuvugktyzdj8quqqv": [{"old_amnt": "12000012099.999999999999999998", "new_amnt": "11880012210.499795031627199675"},
                                                      {"old_amnt": "100911990000.000000000000000000", "new_amnt": "95966340000.000000000000000000"},],
    "secret1zsktmkfqr8pq6vmdku7gfxwmyzysgswqms08j7": [{"old_amnt": "124694483574.000000000000000000", "new_amnt": "123447543574.000000000000000000"},],
    "secret1fwzv9awm23lz0xc2c7z5n826kwnm7a5lxyuagv": [{"old_amnt": "14949700.000000000000000000", "new_amnt": "14809700.000000000000000000"},],
    "secret1tqswduqq7f6czrke4lmdvjphvp80rscu723dck": [{"old_amnt": "2000000.000000000000000000", "new_amnt": "1980000.000000000000000000"},],
    "secret1t7t0vk4zyw6y6r2yxl9wfqg4gjqehw77jdk88e": [{"old_amnt": "2000000.000000000000000000", "new_amnt": "1980000.000000000000000000"},],
    "secret1f5mp7pywt2zm595tp4glu3mfrd0qk0zymncyl0": [{"old_amnt": "100000000000.000000000000000000", "new_amnt": "98010000000.000000000000000000"},],
    "secret1dyuykrsg0n0g2ejf4409am6kn9ejyuch4lzg6d": [{"old_amnt": "100000000.000000000000000000", "new_amnt": "98010000.000000000000000000"},],
    "secret1n28el0zwyx8g4t9jc7339v6tjs292ycveqppqr": [{"old_amnt": "10000000.000000000000000000", "new_amnt": "9810000.000000000000000000"},],
    "secret1z8el4u2j9zhq7ywnrjcdgyvwrank62f0lelk9e": [{"old_amnt": "479999.999999999999999999", "new_amnt": "470448.011586836462317555"},],
    "secret1h3gzw0wncwrjx4mpjuxhmdt6f4vk46g4pg94sj": [{"old_amnt": "120082379604.000000000000000000", "new_amnt": "118881559604.000000000000000000"},],
    "secret1p6jwgslfu6wz6df57exh4s5anqn2yrq6m68yjp": [{"old_amnt": "499999999999.999999999999999999", "new_amnt": "485149500249.450359378483681747"},],
    "secret1vxla2uvkcj0lkmxzl67y6gqk2una5muv9tntkv": [{"old_amnt": "500099999999.999999999999999999", "new_amnt": "485246530149.500249450359378484"},],
    "secret1m2f2fjykvldhnky65kdr6zf2hty88th3yekkll": [{"old_amnt": "1500000.000000000000000000", "new_amnt": "1490000.000000000000000000"}],
    "secret1az8rsuq50a78xdh975e40rykaw77s2gumgn59r": [{"old_amnt": "1390000.000000000000000000", "new_amnt": "1370000.000000000000000000"}],
}


def fix_staking_amounts(data):
    for i, delegator in enumerate(data["app_state"]["distribution"]["delegator_starting_infos"]):
        if delegator["delegator_address"] in staking_amounts_to_fix:
            old_value = delegator["starting_info"]["stake"]
            for item in staking_amounts_to_fix[delegator["delegator_address"]]:
                if item["old_amnt"] == old_value:
                    data["app_state"]["distribution"]["delegator_starting_infos"][i]["starting_info"]["stake"] = item["new_amnt"]

    return data


def convert_prefix(in_val: str) -> str:
    prefix = ""
    for key in replaceable_map:
        if in_val.startswith(key):
            prefix = key[:-1]
            break

    if not prefix:
        raise ValueError(f"Cannot decode string {in_val}")

    _, data = bech32.bech32_decode(in_val)
    return bech32.bech32_encode(conversion_map[prefix], data)


def should_replace(in_val: str) -> bool:
    for key in replaceable_map:
        if in_val.startswith(key):
            return True
    return False


def replace_values(data):
    for key, value in data.items():
        if isinstance(value, str):
            if should_replace(value):
                data[key] = convert_prefix(value)
            if key == "chain_id":
                data[key] = TARGET_CHAIN_ID
        elif isinstance(value, dict):
            data[key] = replace_values(value)
        elif isinstance(value, list):
            for j, val in enumerate(value):
                if isinstance(val, dict):
                    value[j] = replace_values(val)
                elif isinstance(val, str):
                    if should_replace(val):
                        value[j] = convert_prefix(val)
                elif isinstance(val, list):
                    for i, v in enumerate(val):
                        if isinstance(v, dict):
                            val[i] = replace_values(v)
                        elif isinstance(v, str) and should_replace(v):
                            val[i] = convert_prefix(v)
    return data


def replace_keys(old_dict):
    new_dict = {}
    for key in old_dict.keys():
        new_key = convert_prefix(key) if should_replace(key) else key
        if isinstance(old_dict[key], dict):
            new_dict[new_key] = replace_keys(old_dict[key])
        else:
            new_dict[new_key] = old_dict[key]
    return new_dict



def handle_args():
    import argparse
    parser = argparse.ArgumentParser(description='Simple helper to convert genesis files to the new prefix')
    parser.add_argument('-i', '--input', type=str, default=None, help="Path to input genesis file", required=True)
    parser.add_argument('-o', '--output', type=str, default=None, help="Path to output genesis file")

    args = parser.parse_args()

    return args


def run():
    try:
        args = handle_args()
    except TypeError as e:
        e_msg, e_val = e.args
        print(e_msg + '-' + e_val)
        sys.exit()

    with open(args.input, encoding="utf-8") as f:
        as_json = json.load(f)

    result = replace_values(as_json)
    result = replace_keys(result)
    result = fix_staking_amounts(result)

    result["app_state"]["tokenswap"] = genesis_tokenswap_params
    # result["app_state"]["genutil"] = {"gentxs": []}
    output_file = args.output or f'{args.input}'

    with open(output_file, 'w', encoding="utf-8") as f:
        json.dump(result, f, separators=(',', ':'))


if __name__ == '__main__':
    run()
