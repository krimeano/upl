__author__ = "krimeano"


class Config:
    filename = "results.csv"


class NumberWeighted:
    def __init__(self, n, w=1):
        # if not w:
        #     raise AssertionError('number weight should be not null')
        if not w:
            n = 0
        self.n = n
        self.w = w

    def __add__(self, other):
        if not other.w:
            return NumberWeighted(self.n, self.w)
        sum_w = self.w + other.w
        out = NumberWeighted((self.n * self.w + other.n * other.w) / sum_w, sum_w)
        return out

    def __str__(self):
        return "{:.3f}({:d})".format(*[self.n, self.w])


class TeamStats:
    """
    team: Team
    """

    def __init__(self, team):
        self.team = team

    @staticmethod
    def sum_scored(ss):
        return NumberWeighted(sum(ss) / len(ss), len(ss))

    def get_scored_home(self):
        return TeamStats.sum_scored(self.team.scored_home)

    def get_scored_away(self):
        return TeamStats.sum_scored(self.team.scored_away)

    def get_scored(self):
        return self.get_scored_home() + self.get_scored_away()

    def get_missed_home(self):
        return TeamStats.sum_scored(self.team.missed_home)

    def get_missed_away(self):
        return TeamStats.sum_scored(self.team.missed_away)

    def get_missed(self):
        return self.get_missed_home() + self.get_missed_away()


class Team:
    """
    :teams: Team[]
    :matches: Match[]
    """
    teams = []

    def __init__(self, name):
        self.matches = []
        self.name = name
        self.scored_home = []
        self.scored_away = []
        self.missed_home = []
        self.missed_away = []
        self.won_home = 0
        self.won_away = 0
        self.lost_home = 0
        self.lost_away = 0
        self.drawn_home = 0
        self.drawn_away = 0

    @staticmethod
    def get_team(name):
        """
        :param name:
        :return: Team
        """
        for x in Team.teams:
            if x.name == name:
                return x
        team = Team(name)
        Team.teams.append(team)
        return team

    def add_match(self, match):
        """
        :param match: Match
        :return: Team
        """
        me = None
        r = match.get_result()
        if r == 'n':
            return self

        if match.team == self:
            if not match.walkover:
                self.scored_home.append(match.scored)
                self.missed_home.append(match.scored_away)
            if r == '1':
                self.won_home += 1
            elif r == '2':
                self.lost_home += 1
            elif r == 'x':
                self.drawn_home += 1
        elif match.team_away == self:
            if not match.walkover:
                self.scored_away.append(match.scored_away)
                self.missed_away.append(match.scored)
            if r == '1':
                self.lost_away += 1
            elif r == '2':
                self.won_away += 1
            elif r == 'x':
                self.drawn_away += 1
        else:
            raise AssertionError('Adding match for other team')

        self.matches.append(match)

        # print(self.name, ": adding match", match, ':', match.get_result())
        return self

    def get_wins(self):
        return self.won_home + self.won_away

    def get_drows(self):
        return self.drawn_home + self.drawn_away

    def get_looses(self):
        return self.lost_home + self.lost_away

    def get_points(self):
        return self.get_wins() * 3 + self.get_drows()

    def get_goals_scored(self):
        return sum(self.scored_home) + sum(self.scored_away)

    def get_goals_missed(self):
        return sum(self.missed_home) + sum(self.missed_away)

    def get_goals_diff(self):
        return self.get_goals_scored() - self.get_goals_missed()

    def get_played(self):
        return len(self.matches)

    def __str__(self):
        return '"' + self.name + '"'

    def comparison(self):
        return self.get_points() * 10 ** 6 + self.get_wins() * 10 ** 4 + self.get_goals_diff() * 10 ** 2 + self.get_goals_scored()


class Match:
    def __init__(self, teams, goals):
        self.teams_raw = teams
        self.goals_raw = goals
        self.team = Team.get_team(teams[0])
        self.team_away = Team.get_team(teams[1])
        self.walkover = 0
        self.scored = 0
        self.scored_away = 0
        score_walkover = {'+', '-'}
        is_walkover = len(score_walkover.intersection(set(goals)))

        if is_walkover:
            self.walkover = goals.index('+') + 1

        else:
            self.scored = int(goals[0])
            self.scored_away = int(goals[1])

        self.team.add_match(self)
        self.team_away.add_match(self)

    def __str__(self):
        ss = [[self.scored, self.scored_away], ['+', '-'], ['-', '+']][self.walkover]

        return '{th} - {ta} {sh}:{sa}'.format(
            **{'th': self.team, 'ta': self.team_away, 'sh': ss[0], 'sa': ss[1]})

    def get_result(self):
        if self.walkover:
            return str(self.walkover)
        if self.scored > self.scored_away:
            return '1'
        if self.scored < self.scored_away:
            return '2'
        if self.scored == self.scored_away:
            return 'x'
        return 'n'


class Upl:
    """
    matches: Match[]
    """

    def __init__(self):
        self.config = Config()
        self.matches = []

    def read_data(self):
        with open(self.config.filename) as f:
            self.matches = [Match([z.strip() for z in y[1].split('-')], [z.strip() for z in y[2].split(':')])
                            for y in [x.strip().split('\t') for x in f.read().split('\n')]]
        return self

    def gather_data(self):
        Team.teams = sorted(Team.teams, key=lambda t: t.comparison(), reverse=True)
        total_scored = NumberWeighted(0, 0)
        total_scored_home = NumberWeighted(0, 0)
        total_scored_away = NumberWeighted(0, 0)
        for x in Team.teams:
            s = TeamStats(x)
            scored = s.get_scored()
            scored_home = s.get_scored_home()
            scored_away = s.get_scored_away()
            missed = s.get_missed()
            missed_home = s.get_missed_home()
            missed_away = s.get_missed_away()
            total_scored += scored
            total_scored_home += s.get_scored_home()
            total_scored_away += s.get_scored_away()
            print(x.name, x.get_points(), '>',
                  scored, '(', scored_home, '+', scored_away, ')', ':',
                  missed,'(', missed_home, '+', missed_away, ')',
                  "> {:d}':{:d}' / goal".format(*[int(90 / scored.n), int(90 / missed.n)]))
        print('Total scored:', total_scored, 'Home:', total_scored_home, 'Away:', total_scored_away)
        return self

    def stats(self):
        self.read_data().gather_data()
        return self


if __name__ == "__main__":
    upl = Upl()
    upl.stats()
