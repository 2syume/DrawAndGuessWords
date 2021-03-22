#!/usr/bin/env python3
import sys, os
import argparse
import pyperclip
from pynput import keyboard

parser = argparse.ArgumentParser()
parser.add_argument("targets", metavar="target", nargs="+", help="target list to generate from")
parser.add_argument("-f", "--format", choices=["comma", "each"], default="comma", help="formats to load words, comma: comma-seperated, each: copy to clipboard once at a time, default: comma")
parser.add_argument("-t", "--target_type", choices=["file", "tag"], default="file", help="load from file/tag targets, default: file")
parser.add_argument("-l", "--lang", action="store", default="zh_cn", help="language of words, used for tag loading only, default: zh_cn")
parser.add_argument("-k", "--hotkey", action="store", default="<enter>", help="hotkey to trigger next word to be loaded in 'each' mode, default: <enter>")

class WordIter(object):
    def __init__(self, words):
       super().__init__()
       self._words = list(words)
       self._n = 0
       self._listener = None
    def __call__(self):
        if self._n >= len(self._words):
            if self._listener is not None:
                self._listener.stop()
                return
        w = self._words[self._n]
        self._n += 1
        pyperclip.copy(w)
    def set_listener(self, l):
        self._listener = l


def main(targets, format, target_type, lang, hotkey):
    words = set()
    if target_type == "file":
        for t in targets:
            with open(t) as f:
                tags_done = False
                for line in f:
                    word = line.strip()
                    if not word:
                        continue
                    if word == "---":
                        tags_done = True
                        continue
                    if not tags_done:
                        continue 
                    words.add(word)
    elif target_type == "tag":
        targets = set(targets)
        for file in os.listdir(lang):
            path = os.path.join(lang, file)
            with open(path) as f:
                tags_selected = False
                tags_done = False
                for line in f:
                    word = line.strip()
                    if not word:
                        continue
                    if not tags_done and word in targets:
                        tags_selected = True
                        continue
                    if word == "---":
                        tags_done = True
                        continue
                    if not tags_done:
                        continue
                    if not tags_selected:
                        break
                    words.add(word)
    if format == "comma":
        pyperclip.copy(",".join(words))
    elif format == "each":
        pyperclip.copy("")
        word_iter = WordIter(words)
        hotkey = keyboard.HotKey(keyboard.HotKey.parse(hotkey), word_iter)
        with keyboard.Listener(on_press=hotkey.press, on_release=hotkey.release) as l:
            word_iter.set_listener(l)
            l.join()
    return 0

if __name__ == "__main__":
    args = parser.parse_args()
    ret = main(args.targets, args.format, args.target_type, args.lang, args.hotkey)
    sys.exit(ret)