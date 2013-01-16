import ahocorasick
import chardet
import codecs
import gflags
import logging
import math
import re
import sys
import urllib2


gflags.DEFINE_string(
    'config_encoding', 'gb18030',
    'Encoding of config files')
gflags.DEFINE_string(
    'runtime_encoding', 'gb18030',
    'Encoding used in runtime string processing')
gflags.DEFINE_string(
    'entities_path', '',
    'Path to the entities file')
gflags.DEFINE_string(
    'user_agent',
    'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.11 (KHTML, like Gecko) '
    'Chrome/23.0.1271.97 Safari/537.11',
    'User Agent used to crawl pages')
gflags.DEFINE_float(
    'min_absolute_score', 1e-10,
    'Minimal absolute score for a candidate to be accepted')
gflags.DEFINE_float(
    'min_relative_score', 0.2,
    'Minimal score relative to that of the top candidate for a '
    'candidate to be accepted')
gflags.DEFINE_integer(
    'max_candidates', 10,
    'Maximal number of candidates to pick for each page')
gflags.DEFINE_boolean(
    'match_partial_image_url', True,
    'If set to true, only match the filename part of the image url')
gflags.DEFINE_boolean(
    'must_match_image_url', False,
    'If set to true, only pick candidates if the page being analyzed '
    'matches the provided image url')
gflags.DEFINE_integer(
    'header_length',
    1000,
    'Presumed length of the header section that includes title and meta tags')
gflags.DEFINE_integer(
    'header_equivalent_distance',
    200,
    'If an entity is found in the header section, use this equivalent distance')
gflags.DEFINE_integer(
    'min_distance',
    200,
    'Minimal value assigned to a physical distance')

# Flags for running this script in standalone mode.
gflags.DEFINE_string(
    'analyze_image_url', '',
    'Analyze for this image url')
gflags.DEFINE_string(
    'analyze_url', '',
    'Fetch and analyze this url')
gflags.DEFINE_string(
    'analyze_file_path', '',
    'Load and analyze this file')
gflags.DEFINE_string(
    'analyze_file_encoding', '',
    'Encoding of the file to analyze')

FLAGS = gflags.FLAGS


class Analyzer:
    def __init__(self):
        self.tree = None
        self.weights = {}  # entity -> weight
        self.opener = None


    def load(self):
        """Load entities from file to Aho-Corasick tree"""
        assert FLAGS.entities_path
        f = codecs.open(FLAGS.entities_path, encoding=FLAGS.config_encoding,
                        mode='r')
        lines = f.read().split('\n')
        f.close()

        blacklist_pattern = re.compile(r'^[a-zA-Z0-9]{,4}$')
        self.tree = ahocorasick.KeywordTree()
        self.weights = {}
        for line in lines:
            parts = line.strip().split('\t ')
            if len(parts) == 1:
                entity = line
                weight = 1.0
            else:
                entity = parts[0]
                weight = float(parts[1])
            if len(entity) < 2 or blacklist_pattern.match(entity):
                continue
            entity = entity.encode(FLAGS.runtime_encoding).upper()
            self.tree.add(entity)
            self.weights[entity] = weight
        self.tree.make()


    def analyze_url(self, url, image_url):
        page = self.fetch(url)
        logging.info('Page fetched from %s' % url)
        return self.analyze_page(page, image_url)


    def analyze_file(self, path, encoding, image_url):
        f = codecs.open(path, encoding=encoding, mode='r')
        page = f.read().encode(FLAGS.runtime_encoding)
        f.close()
        logging.info('File loaded from %s' % path)
        return self.analyze_page(page, image_url)


    def analyze_page(self, page, image_url):
        """Analyze the given page and return candidates of highest
           confidence scores.
           
           Note: page must be encoded in FLAGS.runtime_encoding.
        """
        page = page.upper()

        # Locate the position of the image.
        image_pos = -1
        if image_url:
            image_url = image_url.upper()
            if FLAGS.match_partial_image_url:
                image_url = image_url[image_url.rfind('/') + 1:]
            image_pos = page.find(image_url)
        if image_pos < 0:
            if FLAGS.must_match_image_url:
                return
            image_pos = len(page) / 2
        else:
            logging.info('Image located at position %s' % image_pos)

        # Match and score.
        scores = {}
        header_entities = {}
        for match in self.tree.findall(page, allow_overlaps=True):
            entity = page[match[0]:match[1]]
            if match[0] < FLAGS.header_length:
                if entity in header_entities:
                    continue  # no awards for repetitions in header section
                header_entities[entity] = True
                distance = FLAGS.header_equivalent_distance
            else:
                distance = abs(match[0] - image_pos) + 1
                distance = max(FLAGS.min_distance, distance)
            score = math.pow(distance, -2.0) * self.weights[entity]
            if entity not in scores:
                scores[entity] = 0.0
            scores[entity] += score

        # Pick candidates whose scores are above the threshold.
        candidates = []
        for entity, score in scores.iteritems():
            if score > FLAGS.min_absolute_score:
                entity = entity.decode(FLAGS.runtime_encoding)
                candidates.append((entity, score))
        num_candidates = len(candidates)
        if num_candidates <= 1:
            return candidates

        # Sort candidates by scores in descending order.
        candidates = sorted(candidates, key=lambda x: -x[1])

        # Pick candidates with sufficient relative scores.
        max_candidates = min(FLAGS.max_candidates, num_candidates)
        min_score = candidates[0][1] * FLAGS.min_relative_score
        pos = 1
        while pos < max_candidates:
            if candidates[pos][1] < min_score:
                break
            pos += 1
        return candidates[:pos]


    def fetch(self, url):
        if not self.opener:
            self.opener = urllib2.build_opener()
            self.opener.addheaders = [('User-Agent', FLAGS.user_agent)]
        f = self.opener.open(url)
        page = f.read()
        # Don't trust the encoding reported by this page itself.
        encoding = chardet.detect(page)['encoding']
        if encoding != FLAGS.runtime_encoding:
            page = page.decode(encoding).encode(FLAGS.runtime_encoding)
        return page


if __name__ == '__main__':
    try:
        sys.argv = FLAGS(sys.argv)
    except gflags.FlagsError, e:
        print '%s\nUsage: %s ARGS\n%s' % (e, sys.argv[0], FLAGS)
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    analyzer = Analyzer()
    analyzer.load()
    candidates = []
    if FLAGS.analyze_url:
        candidates = analyzer.analyze_url(FLAGS.analyze_url,
                                          FLAGS.analyze_image_url)
    elif FLAGS.analyze_file_path:
        assert FLAGS.analyze_file_encoding
        candidates = analyzer.analyze_file(FLAGS.analyze_file_path,
                                           FLAGS.analyze_file_encoding,
                                           FLAGS.analyze_image_url)
    for entity, score in candidates:
        print '%s\t%s' % (entity, score)