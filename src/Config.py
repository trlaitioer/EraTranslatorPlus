from configparser import ConfigParser
from pathlib import Path
import typing


class Config(ConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr


defaultConfig = {
    "Setting": {
        "API": "BaiduAPI",
    },
    "BaiduAPI": {
        "appid": "",
        "key": "",
        "from": "jp",
        "to": "zh"
    },
    "SystemCSV": {
        "ABL": "Abl.csv",
        "BASE": "Base.csv",
        "CFLAG": "CFlag.csv",
        "CSTR": "CStr.csv",
        "EXP": "Exp.csv",
        "FLAG": "Flag.csv",
        "ITEM": "Item.csv",
        "MARK": "Mark.csv",
        "PALAM": "Palam.csv",
        "SAVESTR": "Savestr.csv",
        "SOURCE": "Source.csv",
        "TALENT": "Talent.csv",
        "TCVAR": "Tcvar.csv",
        "TEQUIP": "Tequip.csv",
        "TFLAG": "Tflag.csv",
        "TSTR": "Tstr.csv"
    },
    "ERBMatch": {
        "0": r"PRINT\S*\s+\[[\d\s]+\]\W*(.+)",
        "1": r"PRINT\S*\s+(.+)",
        "2": r"REUSELASTLINE\s+(.+)"
    },
    "CSVMatch": {
        "1": r"\d+\s*,\s*([^\s,;]+)"
    },
    "CSVMatchERB": {
        "sp": r'"(.+?)"',
        "1": r"[A-Z]+?\s*:[^\s*/+-]+?:\s*([^\s,:;(){}|&=*/+-]+)",
        "2": r"[A-Z]+?\s*:\s*([^\s,:;(){}|&=*/+-]+)"
    },
    "CSVMatchChara": {
        "1": r"^[^\s,;]+\s*,\s*([^\s,;]+)\s*,",
        "2": r"^[^\s,;]+\s*,\s*([^\s,;]+)"
    },
    "CharaMatch": {
        "1": r"名前\s*,\s*([^,;\n\r]+)",
        "2": r"呼び名\s*,\s*([^,;\n\r]+)",
        "3": r"CSTR\s*,\s*CHARA_RENAME\s*,\s*([^,;\n\r]+)"
    },
    "IGNOREMatch": {
        "1": r"[\W\d_a-zA-Z]+"
    }
}
config = Config(interpolation=None)
configPath = Path('config.ini')

config.read_dict(defaultConfig)
if not configPath.exists():
    print("配置文件不存在,本次将使用默认配置")
    try:
        config.write(configPath.open("w+", encoding="utf-8-sig"))
        print("配置文件已生成,更改配置文件后请重启软件")
    except Exception as e:
        print(f"生成配置文件出错({e})")
else:
    try:
        config.read(configPath, encoding="utf-8-sig")
        config.write(configPath.open("w+", encoding="utf-8-sig"))
    except Exception as e:
        print(f"读取配置文件出错({e}),本次将使用默认配置")
        config.read_dict(defaultConfig)


def getConfig(section: str, key: str = "") -> typing.Union[str, dict]:
    try:
        if not key:
            return dict(config[section])
        else:
            return config[section][key]
    except KeyError:
        raise KeyError(f"配置参数异常{section,key}")
