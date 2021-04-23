from pathlib import Path
from chardet import UniversalDetector
from Config import getConfig
import json
import re
import typing

detector = UniversalDetector()
ERBMatch = re.compile("|".join(getConfig("ERBMatch").values()))
CSVMatch = re.compile("|".join(getConfig("CSVMatch").values()))
CharaMatch = re.compile("|".join(getConfig("CharaMatch").values()))
CSVMatchChara = re.compile("|".join(getConfig("CSVMatchChara").values()))
CSVMatchERB = "|".join(getConfig("CSVMatchERB").values())


class IOManager:
    def __init__(self, path: typing.Union[Path, str]) -> None:
        self.path = Path(path).resolve()
        self.dic = {}

    def __getitem__(self, key: str) -> str:
        if key in self.dic:
            return self.dic[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.dic[key] = value

    def __contains__(self, key: str) -> bool:
        return True if key in self.dic else False

    def __iter__(self) -> typing.Iterator[str]:
        return self.dic.__iter__()

    def __len__(self) -> int:
        return len(self.dic)

    def keys(self) -> typing.KeysView:
        return self.dic.keys()

    def values(self) -> typing.ValuesView:
        return self.dic.values()

    def items(self) -> typing.ItemsView:
        return self.dic.items()

    def translate(self, original: str, translation: str) -> None:
        if original in self.dic:
            if translation != original:
                self.dic[original] = translation
            else:
                self.dic[original] = ""


class FileManager(IOManager):
    def __init__(self, path: typing.Union[Path, str]) -> None:
        super().__init__(path)
        self.__encoding__ = None

    @property
    def encoding(self) -> str:
        """the encoding of file, detect using chardet"""
        if self.__encoding__ is None:
            detector.reset()
            for line in self.path.open("rb"):
                detector.feed(line)
                if detector.done:
                    break
            self.__encoding__ = detector.close()["encoding"]
            if self.__encoding__ is not None:
                self.__encoding__ = self.__encoding__.lower().replace("_", "-")
        return self.__encoding__

    def root(self, filetype: str) -> Path:
        """return the root folder of game"""
        for parent in self.path.parents:
            if parent.name.lower() == filetype:
                return parent.parent
        print(str(self.path) + f"不在{filetype}目录下")
        return Path()

    def convert(self) -> None:
        """convert the encoding to utf-8-sig"""
        if self.encoding == "utf-8-sig":
            return
        text = self.read()
        if text:
            try:
                self.path.write_text(text, encoding="utf-8-sig")
                self.__encoding__ = "utf-8-sig"
            except Exception as e:
                print(f"转换文件编码时发生错误{self.path.name,e}")

    def read(self) -> str:
        """auto detect the encoding using chardet"""
        try:
            return self.path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            try:
                return self.path.read_text(encoding="cp932")
            except UnicodeDecodeError:
                try:
                    return self.path.read_text(encoding=self.encoding)
                except UnicodeDecodeError:
                    print(f"未知编码({self.path.name})")
        except Exception as e:
            print(f"未预料的错误{self.path.name,e}")
        return ""

    def readlines(self) -> typing.List[str]:
        """auto detect the encoding using chardet"""
        try:
            return self.path.open(encoding="utf-8-sig").readlines()
        except UnicodeDecodeError:
            try:
                return self.path.open(encoding="cp932").readlines()
            except UnicodeDecodeError:
                try:
                    return self.path.open(encoding=self.encoding).readlines()
                except UnicodeDecodeError:
                    print(f"未知编码({self.path.name})")
        except Exception as e:
            print(f"未预料的错误{self.path.name,e}")
        return []


class CacheManager(FileManager):
    def load(self) -> None:
        self.dic = {}
        if self.path.exists():
            try:
                self.dic = json.loads(self.read())
            except Exception:
                pass

    def save(self, data: dict) -> None:
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True)
        if not self.path.exists():
            self.path.touch()
        self.dic = {v: k for k, v in data.items() if v}
        self.path.write_text(json.dumps(self.dic, ensure_ascii=False, separators=(",", ":")), encoding="utf-8-sig")


def resub(match: re.Match, redict: typing.Union[dict, CacheManager]) -> str:
    text = list(filter(None, match.groups()))[0]
    if text in redict and redict[text]:
        return match.group().replace(text, redict[text])
    else:
        return match.group()


class ERBManager(FileManager):
    def __init__(self, path: typing.Union[Path, str]) -> None:
        super().__init__(path)
        self.convert()
        self.content = self.readlines()
        self.cache = CacheManager(self.root.joinpath(f"cache/erb/{self.path.name+'.cache'}"))
        self.load()

    @property
    def root(self) -> Path:
        return super().root(filetype="erb")

    def load(self) -> None:
        self.cache.load()
        self.dic = {}
        for line in self.content:
            linestrip = line.strip()
            if not linestrip or linestrip[0] == ";":  #comment or empty line
                continue
            result = ERBMatch.match(linestrip)
            if not result:
                continue
            result = list(filter(None, result.groups()))[0].strip()  #what needs translating
            if not result:
                continue
            if result in self.cache:
                self.dic[self.cache[result]] = result
            else:
                self.dic[result] = ""

    def save(self) -> None:
        tempcontent = []
        for line in self.content:
            if self.cache:
                line = ERBMatch.sub(lambda x: resub(x, self.cache), line)
            line = ERBMatch.sub(lambda x: resub(x, self.dic), line)
            tempcontent.append(line)
        self.content = tempcontent
        self.path.open("w+", encoding="utf-8-sig").writelines(self.content)
        self.cache.save(self.dic)


class CSVManager(FileManager):
    def __init__(self, path: typing.Union[Path, str]) -> None:
        super().__init__(path)
        self.convert()
        self.content = self.readlines()
        self.cache = CacheManager(self.root.joinpath(f"cache/csv/{self.path.name+'.cache'}"))
        self.load()
        self.saveMatch = re.compile(CSVMatchERB.replace(r"%Attr%", self.path.stem.upper()))

    @property
    def root(self) -> Path:
        return super().root(filetype="csv")

    def load(self) -> None:
        self.cache.load()
        self.dic = {}
        for line in self.content:
            linestrip = line.strip()
            if not linestrip or linestrip[0] == ";":  #comment or empty line
                continue
            result = CSVMatch.match(linestrip)
            if not result:
                continue
            result = list(filter(None, result.groups()))[0].strip()  #what needs translating
            if not result:
                continue
            if result in self.cache:
                self.dic[self.cache[result]] = result
            else:
                self.dic[result] = ""

    def save(self) -> None:
        tempcontent = []
        for line in self.content:
            if self.cache:
                line = CSVMatch.sub(lambda x: resub(x, self.cache), line)
            line = CSVMatch.sub(lambda x: resub(x, self.dic), line)
            tempcontent.append(line)
        self.content = tempcontent
        self.path.open("w+", encoding="utf-8-sig").writelines(self.content)

        for erb in self.root.joinpath("erb").glob("**/*.erb"):
            manager = FileManager(erb)
            tempcontent = []
            for line in manager.readlines():
                if self.cache:
                    line = self.saveMatch.sub(lambda x: resub(x, self.cache), line)
                line = self.saveMatch.sub(lambda x: resub(x, self.dic), line)
                tempcontent.append(line)
            manager.path.open("w+", encoding="utf-8-sig").writelines(tempcontent)

        for chara in self.root.joinpath("csv").glob("**/chara*.csv"):
            manager = FileManager(chara)
            tempcontent = []
            for line in manager.readlines():
                if self.cache:
                    line = CSVMatchChara.sub(lambda x: resub(x, self.cache), line)
                line = CSVMatchChara.sub(lambda x: resub(x, self.dic), line)
                tempcontent.append(line)
            manager.path.open("w+", encoding="utf-8-sig").writelines(tempcontent)

        self.cache.save(self.dic)


class CharaManager(IOManager):
    def __init__(self, path: typing.Union[Path, str]) -> None:
        super().__init__(path)
        self.characsv = [FileManager(i) for i in self.path.glob("**/chara*.csv")]
        self.cache = CacheManager(self.path.parent.joinpath("cache/chara.cache"))
        self.load()

    def load(self) -> None:
        self.cache.load()
        for filepath in self.characsv:
            for line in filepath.readlines():
                linestrip = line.strip()
                if not linestrip or linestrip[0] == ';':
                    continue
                result = CharaMatch.match(linestrip)
                if not result:
                    continue
                result = list(filter(None, result.groups()))[0].strip()
                if not result:
                    continue
                if result in self.cache:
                    self.dic[self.cache[result]] = result
                else:
                    self.dic[result] = ""

    def save(self) -> None:
        for filepath in self.characsv:
            text = filepath.read()
            if self.cache:
                text = CharaMatch.sub(lambda x: resub(x, self.cache), text)
            text = CharaMatch.sub(lambda x: resub(x, self.dic), text)
            filepath.path.write_text(text, encoding="utf-8-sig")
        self.cache.save(self.dic)
