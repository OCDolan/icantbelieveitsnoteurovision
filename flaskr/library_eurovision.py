import json
import os.path
import uuid
from glob import glob
from pathlib import Path

from logging import getLogger

logger = getLogger(__name__)

BASEPATH = '/eurovision'


# Yes this is awful and I need to convert it to a dataclass, I know...

class Entry:

    def __init__(self, id: str):
        self.id = id
        self.lazy_save = False
        self._awaiting_write = {}

    def _read(self) -> dict:
        return json.load(open(os.path.join(BASEPATH, f'{self.id}.json')))

    def _write(self, new_data: dict):
        if self.lazy_save:
            self._awaiting_write.update(new_data)
        else:
            data = self._read()
            data.update(new_data)
            json.dump(data, open(os.path.join(BASEPATH, f'{self.id}.json'), 'w'), indent=4)

    def save_awaiting_writes(self):
        data = self._read()
        data.update(self._awaiting_write)
        json.dump(data, open(os.path.join(BASEPATH, f'{self.id}.json'), 'w'), indent=4)

    @property
    def username(self) -> str:
        return self._read().get('username', None)

    @username.setter
    def username(self, data: str):
        self._write({'username': data})

    @property
    def country(self) -> str:
        return self._read().get('country', None)

    @country.setter
    def country(self, data: str):
        self._write({'country': data})

    @property
    def song_name(self) -> str:
        return self._read().get('song_name', None)

    @song_name.setter
    def song_name(self, data: str):
        self._write({'song_name': data})

    @property
    def song_url(self) -> str:
        return self._read().get('song_url', None)

    @song_url.setter
    def song_url(self, data: str):
        self._write({'song_url': data})

    @property
    def song_filename(self):
        return self._read().get('song_filename', None)

    @song_filename.setter
    def song_filename(self, data: str):
        # TODO Code to
        self._write({'song_filename': data})

    @property
    def postcard_url(self) -> str:
        return self._read().get('postcard_url', None)

    @postcard_url.setter
    def postcard_url(self, data: str):
        self._write({'postcard_url': data})

    @property
    def postcard_filename(self) -> str:
        return self._read().get('postcard_filename', None)

    @postcard_filename.setter
    def postcard_filename(self, data: str):
        self._write({'postcard_filename': data})

    @property
    def flag_filename(self) -> str:
        return self._read().get('flag_filename', None)

    @flag_filename.setter
    def flag_filename(self, data: str):
        self._write({'flag_filename': data})

    @property
    def favourite_colour(self) -> str:
        return self._read().get('favourite_colour', None)

    @favourite_colour.setter
    def favourite_colour(self, data):
        self._write({'favourite_colour': data})


def create_new_entry(username):
    json.dump({"username": username}, open(os.path.join(BASEPATH, f'{uuid.uuid4()}.json'), 'w'))


class Eurovision:

    @classmethod
    def get_entries(cls) -> list[Entry]:
        # Load all json files and make Entry classes for them
        paths = glob('*.json', root_dir=Path(BASEPATH).absolute())
        return [Entry(p.split('.')[0]) for p in paths]

    @classmethod
    def get_entry_by_user(cls, username):
        for entry in cls.get_entries():
            if entry.username == username:
                return entry
        # If we've not returned, there is no entry! Create one...
        print(Path(os.curdir).absolute())
        json.dump({"username": username}, open(os.path.join(BASEPATH, f'{uuid.uuid4()}.json'), 'w'))
        return cls.get_entry_by_user(username)
