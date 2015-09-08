#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
from collections import namedtuple
import csv
from jinja2 import Template
from slugify import slugify


TEMPLATE = """
<h1>Talks</h1>

{% for talk, speaker in talks_and_speakers %}
<article>
    <h3>
        <a href="#talks-{{ talk.slug }}" class="pagelink">
                {{ speaker.name }} - {{ talk.title }}
        </a>
    </h3>
    <p>
        {{ talk.outline }}
    </p>
    <p>
        <strong>About the author:</strong> {{ talk.about_author }}
    </p>
</article>
{% endfor %}

"""


Speaker = namedtuple("Speaker", "name talk email")
Talk = namedtuple("Talk", "email title slug outline about_author")


def main(speakers_csv, cfp_csv):
    accepted_speakers = parse_accepted_speacers(speakers_csv)
    proposed_talks = parse_talks(cfp_csv)
    talks_and_speakers = group_talks_and_speakers(accepted_speakers, proposed_talks)
    print render_html(talks_and_speakers).encode("utf-8")


def parse_accepted_speacers(speakers_csv):
    with open(speakers_csv) as f:
        reader = csv.reader(f)
        field_names = reader.next()
        for line in reader:
            name = line[0].decode("utf-8")
            talk = line[1].decode("utf-8")
            email = line[2].decode("utf-8")
            if name.lower().startswith("not accepted"):
                break
            if all([name, talk, email]):
                yield Speaker(name, talk, email)


def parse_talks(cfp_csv):
    with open(cfp_csv) as f:
        reader = csv.reader(f)
        field_names = reader.next()
        for line in reader:
            if len(line) <= 13 or not all([line[4], line[7], line[8], line[12]]):
                continue
            talk = Talk(
                email=line[4].decode("utf-8"),
                title=line[7].decode("utf-8"),
                slug=slugify(line[7].decode("utf-8")),
                outline=line[8].decode("utf-8"),
                about_author=line[12].decode("utf-8"),
            )
            yield talk


def group_talks_and_speakers(accepted_speakers, proposed_talks):
    proposed_talks = list(proposed_talks)
    talks_by_title = {t.title: t for t in proposed_talks}
    talks_by_email = {t.email: t for t in proposed_talks}
    for speaker in accepted_speakers:
        try:
            talk = talks_by_title[speaker.talk]
        except KeyError:
            talk = talks_by_email[speaker.email]
        yield talk, speaker


def render_html(talks_and_speakers):
    return Template(TEMPLATE).render(talks_and_speakers=talks_and_speakers)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        sys.exit(
            "Usage: {} <accepted speakers csv> <call for proposals "
            "csv>".format(sys.argv[0])
        )
    main(*sys.argv[1:])
