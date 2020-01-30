import statistics as gr
import json
import parser_vk as vk
import unittest


with open('data_test.json') as json_file:
    data = json.load(json_file)


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.data = data
        self.post = [self.data['response']['items'][0]]

    def test_ids_parse(self):
        return self.assertEqual(vk.ids_parse(self.post), [1845])

    def test_text_parse(self):
        return self.assertEqual(
            vk.text_parse(self.post),
            ['Кен Гордон, Principal Communications Specialist в EPAM Continuum,'
             ' встретился с автором книги «Seeing Around Corners» Ритой МакГрат'
             ', чтобы обсудить бизнес-стратегии и шаги, которые могут помочь '
             'компаниям оставаться конкурентоспособными.'])

    def test_attachments_parse(self):
        return self.assertEqual(
            vk.attachments_parse(self.post),
            [['https://www.epam.com/insights/blogs/a-spirited-conversation-with'
              '-the-author-of-seeing-around-corners']])

    def test_num_attach_parse(self):
        return self.assertEqual(
            vk.num_attachments_parse(self.post), [1])

    def test_parse_likes(self):
        return self.assertEqual(vk.parse(self.post, 'likes'), [1])

    def test_parse_reposts(self):
        return self.assertEqual(vk.parse(self.post, 'reposts'), [0])

    def test_parse_comments(self):
        return self.assertEqual(vk.parse(self.post, 'comments'), [0])

    def test_average_statistics(self):
        return self.assertEqual(gr.average_statistics('year', 'likes',
                                                      self.post), {2020: 1.0})

    def test_post_stat(self):
        return self.assertEqual(gr.post_statistics('year', self.post), {2020: 1})
