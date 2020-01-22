import graphics as gr
import json
import parser_vk as vk
import unittest


with open('data_test.json') as json_file:
    data = json.load(json_file)


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.data = data
        self.post = [self.data['response']['items'][0]]

    def test_get_wall(self):
        return self.assertEqual(vk.get_wall('epamsystems', '2020-01-16'),
                                self.post)

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

    def test_likes_parse(self):
        return self.assertEqual(vk.likes_parse(self.post), [1])

    def test_reposts_ids(self):
        return self.assertEqual(vk.reposts_parse(self.post), [0])

    def test_comments_ids(self):
        return self.assertEqual(vk.comments_parse(self.post), [0])

    def test_stat(self):
        return self.assertEqual(gr.stat('year', 'likes', self.post),
                                {2020: 1.0})

    def test_post_stat(self):
        return self.assertEqual(gr.post_stat('year', self.post), {2020: 1})
