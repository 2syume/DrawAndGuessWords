#!/usr/bin/env python3
import sys, os
import argparse
import pyperclip
from pynput import keyboard
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("targets", metavar="target", nargs="+", help="target list to generate from")
parser.add_argument("-f", "--format", choices=["comma", "copy_each", "paste_each"], default="comma", help="formats to load words, comma: comma-seperated, copy_each: copy to clipboard once at a time, paste_each: copy and paste once at a time, default: comma")
parser.add_argument("-t", "--target_type", choices=["file", "tag"], default="file", help="load from file/tag targets, default: file")
parser.add_argument("-l", "--lang", action="store", default="zh_cn", help="language of words, used for tag loading only, default: zh_cn")
parser.add_argument("-k", "--hotkey", action="store", default="<enter>", help="hotkey to trigger next word to be loaded in 'copy_each' mode, default: <enter>")
parser.add_argument("-p", "--paste_key", action="store", default="<ctrl>+v", help="keys(s) to paste content in 'paste_each' mode")
parser.add_argument("-c", "--commit_key", action="store", default="<enter>", help="key(s) to commit change in 'paste_each' mode")
parser.add_argument("-d", "--paste_delay", action="store", type=float, default=0.1, help="seconds to wait between actions in 'paste_each' mode")

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


def main(targets, format, target_type, lang, hotkey, paste_key, commit_key, paste_delay):
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
    elif format == "copy_each":
        pyperclip.copy("")
        word_iter = WordIter(words)
        hotkey = keyboard.HotKey(keyboard.HotKey.parse(hotkey), word_iter)
        with keyboard.Listener(on_press=hotkey.press, on_release=hotkey.release) as l:
            word_iter.set_listener(l)
            l.join()
    elif format == "paste_each":
        kb = keyboard.Controller()
        for word in words:
            pyperclip.copy(word)
            sleep(paste_delay)
            for k in keyboard.HotKey.parse(paste_key):
                kb.press(k)
            for k in keyboard.HotKey.parse(paste_key):
                kb.release(k)
            sleep(paste_delay)
            for k in keyboard.HotKey.parse(commit_key):
                kb.press(k)
            for k in keyboard.HotKey.parse(commit_key):
                kb.release(k)
            sleep(paste_delay)

    return 0

if __name__ == "__main__":
    args = parser.parse_args()
    ret = main(args.targets, args.format, args.target_type, args.lang, args.hotkey, args.paste_key, args.commit_key, args.paste_delay)
    sys.exit(ret)