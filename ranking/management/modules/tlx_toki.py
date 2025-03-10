# -*- coding: utf-8 -*-

import collections
import itertools
import json
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from pprint import pprint

from flatten_dict import flatten
from ratelimiter import RateLimiter

from ranking.management.modules.common import REQ, BaseModule
from ranking.management.modules.excepts import ExceptionParseStandings


class Statistic(BaseModule):
    STANDING_URL_FORMAT_ = '{0.url}/scoreboard'
    PROBLEM_URL_FORMAT_ = '{url}/problems/{short}'
    CONFIG_URL_FORMAT_ = 'https://api.tlx.toki.id/v2/contest-web/slug/{slug}/with-config'
    API_STANDINGS_URL_FORMAT_ = 'https://api.tlx.toki.id/v2/contests/{jid}/scoreboard?frozen=false&showClosedProblems=false&page={page}'  # noqa
    API_PROBLEMS_URL_FORMAT_ = 'https://api.tlx.toki.id/v2/contests/{jid}/problems'
    API_HISTORY_URL_FORMAT_ = 'https://api.tlx.toki.id/v2/contest-history/public?username={handle}'
    API_USER_SEARCH_ = 'https://api.tlx.toki.id/v2/user-search/username-to-jid'
    API_PROFILE_URL_FORMAT_ = 'https://api.tlx.toki.id/v2/profiles/{jid}/basic'
    API_AVATAR_URL_FORMAT_ = 'https://api.tlx.toki.id/v2/users/{jid}/avatar'

    def __init__(self, **kwargs):
        super(Statistic, self).__init__(**kwargs)

    def get_standings(self, users=None, statistics=None):
        slug = self.url.rstrip('/').rsplit('/', 1)[-1]
        config_url = self.CONFIG_URL_FORMAT_.format(slug=slug)
        page = REQ.get(config_url)
        config_data = json.loads(page)
        style = config_data['contest']['style'].upper()

        jid = config_data['contest']['jid']
        url = self.API_STANDINGS_URL_FORMAT_.format(jid=jid, page=1)
        data = json.loads(REQ.get(url))

        problems_url = self.API_PROBLEMS_URL_FORMAT_.format(jid=jid)
        problems_data = json.loads(REQ.get(problems_url))

        problems_info = []
        state = data['data']['scoreboard']['state']
        for idx, (code, short, problem_data) in enumerate(
            zip(state['problemJids'], state['problemAliases'], problems_data['data'])
        ):
            problem_data.update(problems_data['problemsMap'][problem_data['problemJid']])
            title = problem_data['titlesByLanguage'][problem_data['defaultLanguage']]
            info = {
                'name': title,
                'code': problem_data['slug'],
                'short': short,
            }
            if state['problemPoints']:
                info['full_score'] = state['problemPoints'][idx]
            elif problem_data['points']:
                info['full_score'] = problem_data['points']
            info['url'] = self.PROBLEM_URL_FORMAT_.format(url=self.url, short=info['short'])
            problems_info.append(info)

        result = {}
        if users is None or users:
            total = data['data']['totalEntries']
            has_old_rating = False
            page = 0
            stop = False
            while total > 0 and not stop:
                stop = True
                page += 1
                if page > 1:
                    url = self.API_STANDINGS_URL_FORMAT_.format(jid=jid, page=page)
                    data = json.loads(REQ.get(url))

                rows = data['data']['scoreboard']['content']['entries']
                users_profiles_map = data['profilesMap']
                for row in rows:
                    cjid = row['contestantJid']
                    total -= 1
                    if cjid not in users_profiles_map:
                        continue
                    user = users_profiles_map[cjid]
                    handle = user['username']

                    r = result.setdefault(handle, collections.OrderedDict())
                    r['member'] = handle
                    r['place'] = row.pop('rank')
                    if user.get('country'):
                        r['country'] = user['country']

                    if style == 'ICPC':
                        r['penalty'] = row.pop('totalPenalties')
                        r['solving'] = row.pop('totalAccepted')
                    elif style == 'GCJ' or style == 'TROC':
                        penalty = row.pop('totalPenalties')
                        r['penalty'] = f'{penalty // 60:02d}:{penalty % 60:02d}'
                        r['solving'] = row.pop('totalPoints')
                    elif style == 'IOI':
                        r['solving'] = row.pop('totalScores')
                    else:
                        raise ExceptionParseStandings(f'style = {style}')

                    problems = r.setdefault('problems', {})
                    solving = 0
                    if style == 'IOI':
                        for idx, score in enumerate(row['scores']):
                            if score is None:
                                continue
                            k = problems_info[idx]['short']
                            p = problems.setdefault(k, {})
                            p['result'] = score
                            p['partial'] = problems_info[idx].get('full_score', 100) > score
                            if not p['partial']:
                                solving += 1
                    else:
                        for idx, (attempt, penalty, pstate) in enumerate(
                            zip(row['attemptsList'], row['penaltyList'], row['problemStateList'])
                        ):
                            if not attempt:
                                continue
                            k = problems_info[idx]['short']
                            p = problems.setdefault(k, {})

                            if pstate:
                                solving += 1
                                p['result'] = f"+{'' if attempt == 1 else attempt - 1}"
                                p['time'] = f'{penalty // 60:02d}:{penalty % 60:02d}'
                            else:
                                p['result'] = f"-{attempt}"
                            if pstate == 2:
                                p['first_ac'] = True
                    if not problems:
                        result.pop(handle)
                        continue

                    if state['problemPoints'] or style == 'IOI':
                        r['solved'] = {'solving': solving}

                    r['old_rating'] = (user.get('rating') or {}).get('publicRating')
                    if r['old_rating'] is not None:
                        has_old_rating = True

                    stats = statistics.get(handle, {})
                    for f in 'old_rating', 'rating_change', 'new_rating':
                        if f in stats and f not in r:
                            r[f] = stats[f]

                    stop = False

            if not has_old_rating:
                for r in result.values():
                    r.pop('old_rating')

        standings = {
            'result': result,
            'url': self.STANDING_URL_FORMAT_.format(self),
            'problems': problems_info,
        }
        return standings

    @staticmethod
    def get_users_infos(users, resource, accounts, pbar=None):

        @RateLimiter(max_calls=5, period=1)
        def fetch_profile(jid, handle):
            url = Statistic.API_PROFILE_URL_FORMAT_.format(jid=jid)
            page = REQ.get(url)
            data = json.loads(page)
            data = flatten(data, 'dot')
            data['rating'] = data.pop('rating.publicRating', None)

            url = Statistic.API_AVATAR_URL_FORMAT_.format(jid=jid)
            data['avatar_url'] = url

            url = Statistic.API_HISTORY_URL_FORMAT_.format(handle=handle)
            history = json.loads(REQ.get(url))
            return data, history

        page = REQ.get(Statistic.API_USER_SEARCH_, post=json.dumps(users), content_type='application/json')
        data = json.loads(page)
        jids = [data[user] for user in users]

        with PoolExecutor(max_workers=8) as executor:
            profiles = executor.map(fetch_profile, jids, users)
            for user, (data, history) in zip(users, profiles):
                if pbar:
                    pbar.update()
                assert user == data['username']
                if not data:
                    if data is None:
                        yield {'info': None}
                    else:
                        yield {'skip': True}
                    continue

                contests = history['data']
                contests.sort(key=lambda c: history['contestsMap'][c['contestJid']]['beginTime'])
                last_rating = None
                contest_addition_update = {}
                for contest in contests:
                    slug = history['contestsMap'][contest['contestJid']]['slug']
                    url = f'https://tlx.toki.id/contests/{slug}'
                    update = contest_addition_update.setdefault(url, collections.OrderedDict())
                    if contest['rating']:
                        rating = contest['rating']['publicRating']
                        if last_rating is not None:
                            update['old_rating'] = last_rating
                            update['rating_change'] = rating - last_rating
                        update['new_rating'] = rating
                        last_rating = rating
                    elif last_rating is not None:
                        update['old_rating'] = last_rating
                    else:
                        contest_addition_update.pop(url)

                if last_rating is not None:
                    data['rating'] = last_rating

                ret = {
                    'info': data,
                    'contest_addition_update_params': {
                        'update': contest_addition_update,
                        'by': 'url',
                        'clear_rating_change': True,
                    },
                    'replace_info': True,
                }

                yield ret


if __name__ == '__main__':
    statistic = Statistic(url='https://tlx.toki.id/contests/troc-11-div-1', key='380')
    standings = statistic.get_standings()
    result = standings.pop('result', {})
    pprint(list(itertools.islice(result.items(), 0, 10)))
