# -*- coding: utf-8 -*-
"""Mashable sources (news, weather, wiki) against recorded responses — no network."""

import json
import unittest
from unittest import mock

from src.vm import VM, KapilaError
from src.vm import sources

RSS_PRAJAVANI = """<?xml version="1.0"?><rss><channel>
<item><title>ಬೆಂಗಳೂರಿನಲ್ಲಿ ಮಳೆ</title><link>https://p.example/1</link>
  <pubDate>Sun, 08 Nov 2026 08:00:00 +0530</pubDate></item>
<item><title>ಮೈಸೂರು ದಸರಾ</title><link>https://p.example/2</link>
  <pubDate>Sun, 08 Nov 2026 07:00:00 +0530</pubDate></item>
</channel></rss>""".encode()

RSS_TV9 = """<?xml version="1.0"?><rss><channel>
<item><title>ಬೆಂಗಳೂರು ಸಂಚಾರ ದಟ್ಟಣೆ</title><link>https://t.example/1</link>
  <pubDate>Sun, 08 Nov 2026 09:00:00 +0530</pubDate></item>
<item><title>ಬೆಂಗಳೂರಿನಲ್ಲಿ ಮಳೆ</title><link>https://t.example/dup</link>
  <pubDate>Sun, 08 Nov 2026 06:00:00 +0530</pubDate></item>
</channel></rss>""".encode()

RSS_GOOGLE = """<?xml version="1.0"?><rss><channel>
<item><title>Rain lashes Bengaluru - The Hindu</title><link>https://g.example/1</link>
  <pubDate>Sun, 08 Nov 2026 03:00:00 GMT</pubDate><source url="https://thehindu.com">The Hindu</source></item>
</channel></rss>""".encode()

GEO_OPEN_METEO = json.dumps({"results": [{"name": "ಮೈಸೂರು", "latitude": 12.2979, "longitude": 76.6393}]}).encode()
GEO_EMPTY = json.dumps({}).encode()
GEO_NOMINATIM = json.dumps([{"name": "ಹುಬ್ಬಳ್ಳಿ", "lat": "15.3518", "lon": "75.1380"}]).encode()
FORECAST = json.dumps({"current": {"time": "2026-11-08T09:30", "temperature_2m": 24.4,
                                   "precipitation": 1.2, "wind_speed_10m": 17.8, "weather_code": 63}}).encode()
WIKI_KUVEMPU = json.dumps({"type": "standard", "title": "ಕುವೆಂಪು", "extract": "ಕನ್ನಡದ ಕವಿ",
                           "content_urls": {"desktop": {"page": "https://kn.wikipedia.org/wiki/x"}},
                           "thumbnail": {"source": "https://img.example/k.jpg"}}).encode()
WIKI_SEARCH = json.dumps({"pages": [{"key": "Kuvempu", "title": "Kuvempu"}]}).encode()
WIKI_EN = json.dumps({"type": "standard", "title": "Kuvempu", "extract": "Kannada poet",
                      "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Kuvempu"}},
                      "coordinates": {"lat": 13.6, "lon": 75.4}}).encode()


def fake_http(routes):
    """Replace sources._http_get: first route whose key is in the URL wins; else 404 (b'')."""
    def get(url, client_id=None):
        for key, body in routes.items():
            if key in url:
                return body
        return b""
    return mock.patch.object(sources, "_http_get", side_effect=get)


def run(source):
    vm = VM(sandbox=True)
    vm.run(source)
    return vm


class NewsTests(unittest.TestCase):
    def test_kannada_topic_searches_kannada_publishers(self):
        with fake_http({"prajavani": RSS_PRAJAVANI, "tv9kannada": RSS_TV9}):
            vm = run('ಸ := "ಬೆಂಗಳೂರು" ಸುದ್ದಿ.')
        titles = [r["ಶೀರ್ಷಿಕೆ"] for r in vm.variables["ಸ"]]
        # inflected form (ಬೆಂಗಳೂರಿನಲ್ಲಿ) matches; Mysuru doesn't; duplicate title kept once; newest first
        self.assertEqual(titles, ["ಬೆಂಗಳೂರು ಸಂಚಾರ ದಟ್ಟಣೆ", "ಬೆಂಗಳೂರಿನಲ್ಲಿ ಮಳೆ"])
        self.assertEqual(vm.variables["ಸ"][1]["ಮೂಲ"], "ಪ್ರಜಾವಾಣಿ")
        self.assertEqual(vm.variables["ಸ"][0]["ಸಮಯ"], "2026-11-08T09:00:00+05:30")

    def test_empty_topic_gives_latest(self):
        with fake_http({"prajavani": RSS_PRAJAVANI, "tv9kannada": RSS_TV9}):
            vm = run('ಸ := "" ಸುದ್ದಿ.')
        self.assertEqual(len(vm.variables["ಸ"]), 3)

    def test_one_dead_feed_does_not_sink_the_rest(self):
        with fake_http({"prajavani": b"<not xml", "tv9kannada": RSS_TV9}):
            vm = run('ಸ := "ಬೆಂಗಳೂರು" ಸುದ್ದಿ.')
        self.assertEqual(len(vm.variables["ಸ"]), 2)

    def test_english_topic_uses_google_news_and_strips_publisher(self):
        with fake_http({"news.google.com": RSS_GOOGLE}):
            vm = run('n := "Bengaluru rain" news.')
        rec = vm.variables["n"][0]
        self.assertEqual(rec["ಶೀರ್ಷಿಕೆ"], "Rain lashes Bengaluru")
        self.assertEqual(rec["ಮೂಲ"], "The Hindu")


class WeatherTests(unittest.TestCase):
    def test_weather_record(self):
        with fake_http({"geocoding-api": GEO_OPEN_METEO, "api.open-meteo.com/v1/forecast": FORECAST}):
            vm = run('ಹ := "ಮೈಸೂರು" ಹವಾಮಾನ.')
        rec = vm.variables["ಹ"]
        self.assertEqual(rec["ಸ್ಥಳ"], "ಮೈಸೂರು")
        self.assertEqual(rec["ತಾಪಮಾನ"], 24.4)
        self.assertEqual(rec["ಮಳೆ"], 1.2)
        self.assertEqual(rec["ಸ್ಥಿತಿ"], "ಮಳೆ")
        self.assertEqual((rec["ಅಕ್ಷಾಂಶ"], rec["ರೇಖಾಂಶ"]), (12.2979, 76.6393))

    def test_falls_back_to_openstreetmap(self):
        with fake_http({"geocoding-api": GEO_EMPTY, "nominatim": GEO_NOMINATIM,
                        "api.open-meteo.com/v1/forecast": FORECAST}):
            vm = run('ತ := "ಹುಬ್ಬಳ್ಳಿ" ಹವಾಮಾನದ ಸ್ಥಳ.')
        self.assertEqual(vm.variables["ತ"], "ಹುಬ್ಬಳ್ಳಿ")

    def test_unknown_place(self):
        with fake_http({"geocoding-api": GEO_EMPTY, "nominatim": b"[]"}):
            with self.assertRaises(KapilaError):
                run('"ಇಲ್ಲದಊರು" ಹವಾಮಾನ.')


class WikiTests(unittest.TestCase):
    def test_kannada_title_uses_kannada_wikipedia(self):
        with fake_http({"kn.wikipedia.org/api/rest_v1/page/summary": WIKI_KUVEMPU}):
            vm = run('ಕ := "ಕುವೆಂಪು" ವಿಕಿ.')
        rec = vm.variables["ಕ"]
        self.assertEqual(rec["ಸಾರಾಂಶ"], "ಕನ್ನಡದ ಕವಿ")
        self.assertEqual(rec["ಚಿತ್ರ"], "https://img.example/k.jpg")
        self.assertNotIn("ಅಕ್ಷಾಂಶ", rec)

    def test_inexact_title_falls_back_to_search(self):
        with fake_http({"summary/Kuvempu": WIKI_EN, "search/page": WIKI_SEARCH}):
            vm = run('k := "kuvempu poet" wiki.')
        rec = vm.variables["k"]
        self.assertEqual(rec["ಶೀರ್ಷಿಕೆ"], "Kuvempu")
        self.assertEqual((rec["ಅಕ್ಷಾಂಶ"], rec["ರೇಖಾಂಶ"]), (13.6, 75.4))

    def test_not_found(self):
        with fake_http({}):
            with self.assertRaises(KapilaError):
                run('"zzqx" wiki.')


class SafetyTests(unittest.TestCase):
    def test_source_calls_per_run_are_limited(self):
        with fake_http({"summary": WIKI_EN}):
            with self.assertRaises(KapilaError) as cm:
                run('[ ೧ ೨ ೩ ೪ ೫ ೬ ] [ ಪಠ್ಯಕ್ಕೆ wiki ] ನಕ್ಷೆ.')
        self.assertIn(str(sources.FETCHES_PER_RUN), str(cm.exception))

    def test_only_allowlisted_hosts(self):
        with self.assertRaises(KapilaError):
            sources._http_get("https://evil.example/x")
        with self.assertRaises(KapilaError):
            sources._http_get("http://en.wikipedia.org/x")   # https only

    def test_sources_available_in_sandbox(self):
        vm = VM(sandbox=True)
        for word in ("ಸುದ್ದಿ", "ಹವಾಮಾನ", "ವಿಕಿ", "news", "weather", "wiki"):
            self.assertIn(word, vm.builtins)


if __name__ == "__main__":
    unittest.main()


class BudgetResetTests(unittest.TestCase):
    def test_budget_resets_per_run_but_not_through_eval(self):
        with fake_http({"summary": WIKI_EN}):
            vm = VM(sandbox=True)
            for _ in range(3):                       # a reused VM (REPL, sandarbha) gets 5 per run
                vm.run('[ ೧ ೨ ೩ ೪ ೫ ] [ ಪಠ್ಯಕ್ಕೆ wiki ] ನಕ್ಷೆ.')
            with self.assertRaises(KapilaError):      # eval inside a run shares that run's budget
                vm.run('[ ೧ ೨ ೩ ೪ ೫ ] [ ಪಠ್ಯಕ್ಕೆ wiki ] ನಕ್ಷೆ. "\\"x\\" wiki" eval.')


class TraceTests(unittest.TestCase):
    def test_trace_records_words_and_requests(self):
        with fake_http({"geocoding-api": GEO_OPEN_METEO, "api.open-meteo.com/v1/forecast": FORECAST}):
            vm = VM(sandbox=True)
            vm.trace = []
            vm.run('"ಮೈಸೂರು" ಹವಾಮಾನ ಸ್ಥಿತಿ ಮುದ್ರಿಸು.')
        words = [e["w"] for e in vm.trace if e["k"] == "word"]
        fetches = [e for e in vm.trace if e["k"] == "fetch"]
        self.assertEqual(words, ["ಹವಾಮಾನ", "ಸ್ಥಿತಿ", "ಮುದ್ರಿಸು"])
        self.assertEqual([f["host"] for f in fetches], ["geocoding-api.open-meteo.com", "api.open-meteo.com"])
        self.assertIn("name=ಮೈಸೂರು", fetches[0]["path"])     # shown decoded, readable
        self.assertEqual(fetches[0]["d"], 1)                  # nested under ಹವಾಮಾನ

    def test_tracing_is_off_by_default(self):
        vm = VM(sandbox=True)
        vm.run('೨ ೩ ಕೂಡು.')
        self.assertIsNone(vm.trace)


class NoArgumentTests(unittest.TestCase):
    def test_news_with_nothing_on_the_stack_gives_latest(self):
        with fake_http({"prajavani": RSS_PRAJAVANI, "tv9kannada": RSS_TV9}):
            vm = run('ಸ := ಸುದ್ದಿ.')
        self.assertEqual(len(vm.variables["ಸ"]), 3)

    def test_weather_without_a_place_explains_itself(self):
        with self.assertRaises(KapilaError) as cm:
            run('ಹವಾಮಾನ ಮುದ್ರಿಸು.')
        self.assertIn('"ಮೈಸೂರು" ಹವಾಮಾನ', str(cm.exception))

    def test_underflow_names_the_word(self):
        with self.assertRaises(KapilaError) as cm:
            run('ಕೂಡು.')
        self.assertIn("ಕೂಡು", str(cm.exception))


RSS_TV9_BUSINESS = """<?xml version="1.0"?><rss><channel>
<item><title>ಷೇರು ಮಾರುಕಟ್ಟೆ ಏರಿಕೆ</title><link>https://t.example/b1</link>
  <pubDate>Sun, 08 Nov 2026 09:00:00 +0530</pubDate></item>
</channel></rss>""".encode()
RSS_KP_BUSINESS = """<?xml version="1.0"?><rss><channel>
<item><title>ಚಿನ್ನದ ಬೆಲೆ ಇಳಿಕೆ</title><link>https://k.example/b1</link>
  <pubDate>Sun, 08 Nov 2026 08:00:00 +0530</pubDate></item>
</channel></rss>""".encode()


class SectionTests(unittest.TestCase):
    def test_kannada_section_reads_section_feeds(self):
        with fake_http({"tv9kannada.com/business/feed": RSS_TV9_BUSINESS,
                        "collections/business.rss": RSS_KP_BUSINESS}):
            vm = run('ಸ := "ವಾಣಿಜ್ಯ" ಸುದ್ದಿ.')
        recs = vm.variables["ಸ"]
        self.assertEqual([r["ಶೀರ್ಷಿಕೆ"] for r in recs], ["ಷೇರು ಮಾರುಕಟ್ಟೆ ಏರಿಕೆ", "ಚಿನ್ನದ ಬೆಲೆ ಇಳಿಕೆ"])
        self.assertEqual({r["ವಿಭಾಗ"] for r in recs}, {"ವಾಣಿಜ್ಯ"})

    def test_section_aliases(self):
        with fake_http({"tv9kannada.com/business/feed": RSS_TV9_BUSINESS}):
            vm = run('ಸ := "ಉದ್ಯಮ" ಸುದ್ದಿ.')
        self.assertEqual(vm.variables["ಸ"][0]["ವಿಭಾಗ"], "ವಾಣಿಜ್ಯ")

    def test_english_section_uses_google_topic(self):
        seen = []
        def get(url, client_id=None):
            seen.append(url)
            return RSS_GOOGLE
        with mock.patch.object(sources, "_http_get", side_effect=get):
            vm = run('n := "Business" news.')
        self.assertIn("/headlines/section/topic/BUSINESS", seen[0])
        self.assertEqual(vm.variables["n"][0]["ವಿಭಾಗ"], "ವಾಣಿಜ್ಯ")

    def test_other_words_still_search_headlines(self):
        with fake_http({"prajavani": RSS_PRAJAVANI, "tv9kannada.com/feed": RSS_TV9}):
            vm = run('ಸ := "ದಸರಾ" ಸುದ್ದಿ.')
        self.assertEqual([r["ಶೀರ್ಷಿಕೆ"] for r in vm.variables["ಸ"]], ["ಮೈಸೂರು ದಸರಾ"])
        self.assertNotIn("ವಿಭಾಗ", vm.variables["ಸ"][0])
