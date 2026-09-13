import json
import os.path
import uuid
from glob import glob
from pathlib import Path

from logging import getLogger

logger = getLogger(__name__)

BASEPATH = os.environ.get("BASEPATH", 'testdata')
STATEPATH = os.path.join(BASEPATH, 'state.json')

if not os.path.exists(STATEPATH):
    with open(STATEPATH, 'w') as f:
        f.write(json.dumps({}))


# Yes this is awful and I need to convert it to a dataclass, I know...

class Entry:

    def __init__(self, id: str):
        self.id = id
        self.lazy_save = False
        self._awaiting_write = {}

    @property
    def entry_filename(self):
        return Path(BASEPATH, 'submissions', f'{self.id}.json')

    def _read(self) -> dict:
        return json.load(open(self.entry_filename))

    def _write(self, new_data: dict):
        if self.lazy_save:
            self._awaiting_write.update(new_data)
        else:
            data = self._read()
            data.update(new_data)
            json.dump(data, open(self.entry_filename, 'w'), indent=4)

    def save_awaiting_writes(self):
        data = self._read()
        data.update(self._awaiting_write)
        json.dump(data, open(self.entry_filename, 'w'), indent=4)

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


class Eurovision:

    @classmethod
    def get_entries(cls) -> list[Entry]:
        # Load all json files and make Entry classes for them
        paths = glob('*.json', root_dir=Path(BASEPATH, 'submissions').absolute())
        return [Entry(p.split('.')[0]) for p in paths]

    @classmethod
    def get_entry_by_user(cls, username):
        for entry in cls.get_entries():
            if entry.username == username:
                return entry
        # If we've not returned, there is no entry! Create one...
        json.dump({"username": username}, open(Path(BASEPATH, 'submissions', f'{uuid.uuid4()}.json'), 'w'))
        return cls.get_entry_by_user(username)

    @classmethod
    def get_entry_by_country(cls, country):
        for entry in cls.get_entries():
            if entry.country == country:
                return entry

    @classmethod
    def get_contestants(cls) -> list[Entry]:
        contestants: list[Entry] = []
        for entry in cls.get_entries():
            if entry.username and entry.song_name and entry.flag_filename:
                contestants.append(entry)
        return contestants

    @classmethod
    def load_state(cls):
        return json.load(open(STATEPATH))

    @classmethod
    def save_state(cls, data):
        json.dump(data, open(STATEPATH, 'w'))

    @classmethod
    def is_voting_open(cls) -> bool:
        return cls.load_state().get('is_voting_open', False)

    @classmethod
    def set_is_voting_open(cls, is_voting_open: bool):
        state = cls.load_state()
        state['is_voting_open'] = is_voting_open
        cls.save_state(state)

    @classmethod
    def un_announce_jury_vote(cls):
        jury_paths = Path(BASEPATH, 'points').glob('points_jury_*.json')
        for jury_path in jury_paths:
            data = json.load(open(jury_path))
            data.pop('announce', False)
            data.pop('announce_12', False)
            json.dump(data, open(jury_path, 'w'))

    @classmethod
    def reset_public_vote(cls):
        raise NotImplemented()

    @classmethod
    def get_points(self) -> dict[str, int]:
        total_points: dict[str, int] = {contestants.country: 0 for contestants in Eurovision.get_contestants()}

        # Collect Jury Votes
        jury_paths = Path(BASEPATH, 'points').glob('points_jury_*.json')
        for jury_path in jury_paths:
            data = json.load(open(jury_path))
            logger.warning(f'Reading: {jury_path}: {data}')
            announce = data.pop('announce', False)
            announce_12 = data.pop('announce_12', False)
            for country, points_awarded in data.items():
                if announce_12 or (announce and points_awarded < 12):
                    total_points[country] += points_awarded

        # Collect Public Votes
        # TODO Favourite Postcard/Flag/Costume/Theme etc...
        jury_paths = Path(BASEPATH, 'points').glob('points_public_*.json')
        for jury_path in jury_paths:
            data = json.load(open(jury_path))
            logger.warning(f'Reading: {jury_path}: {data}')
            for country, points_awarded in data.items():
                total_points[country] += points_awarded

        logger.warning(f'Jury points: {total_points}')
        return total_points

