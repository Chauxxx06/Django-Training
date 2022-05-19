import datetime
from urllib import response

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


#Testeo de modelos o vistas
class QuestionModelTest(TestCase):
    
    def test_was_published_recently_with_future_question(self):
        """ was_published_recently returns False for question whose pub_dater is in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="Quein es el mejor Course Director de Platzi", pub_date=time)
        self.assertIs(future_question.was_published_recently(),False)

    def test_was_published_recently_with_past_question(self):
        """ was_published_recently returns False for question whose pub_dater is in the future"""
        time = timezone.now() - datetime.timedelta(days=30)
        past_question = Question(question_text="Quein es el mejor Course Director de Platzi", pub_date=time)
        self.assertIs(past_question.was_published_recently(),False)

    def test_was_published_recently_with_present_question(self):
        """ was_published_recently returns False for question whose pub_dater is in the future"""
        time = timezone.now()
        present_question = Question(question_text="Quein es el mejor Course Director de Platzi", pub_date=time)
        self.assertIs(present_question.was_published_recently(),True)

def create_question(question_text, days):
    """ Create a question with the given question_text and publish the given number of days
        offset to now(negative for question publish in the pass,
        positive for question that have yet to be published)"""
    time = timezone.now() + datetime.timedelta(days=days)
    return  Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTest(TestCase):
    
    def test_no_questions(self):
        """ If no question exist, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index")) #reverse hace que no se harcodee la url (es dinamico) y self.client.get es la peticion http GET
        self.assertEqual(response.status_code,200) # response.status_code retorna estado respuesta http
        self.assertContains(response, "No Polls are available.") # el mensaje viene el frontend
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

    def test_future_question(self):
        """
            Question with as pùb_date in the future aren't displayed on the index page
        """
        create_question("future_question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No Polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

    def test_past_question(self):
        """
            Questions with a pub_date in the pàst are displayedon the index page
        """
        question = create_question("past_question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[question])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future question exist, only past question are display
        """
        past_question = create_question(question_text="past_question", days=-30)
        future_question = create_question(question_text="future_question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question]
        )

    def test_two_past_question(self):
        """
        The question index page may display multiple question
        """
        past_question1 = create_question(question_text="past_question_1", days=-20)
        past_question2 = create_question(question_text="past_question_2", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question1, past_question2]
        )

    def test_two_future_question(self):
        """
        The question index page may display multiple question
        """
        future_question1 = create_question(question_text="future_question_1", days=20)
        future_question2 = create_question(question_text="future_question_2", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No Polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        """
        Teh detail view of a question with a pub_date in the future
        return a 404 error not found
        """
        future_question = create_question(question_text="future_question", days=30)
        url = reverse("polls:detail",args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        the detail view of a question with a pub_date in the past
        display dthe question text
        """
        past_question = create_question(question_text="past_question", days=-30)
        url = reverse("polls:detail",args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
