from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404

from itertools import chain
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView

from konnectapp.models import Answer, Author, Comment, Question
from taggit.models import Tag
from django.template.defaultfilters import slugify
from .forms import PostForm
from django.db import IntegrityError




class UpdateAnswer(LoginRequiredMixin, UpdateView):
    model = Answer
    fields = ['answer_text']
    template_name = 'konnectapp/answer_update_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answer_id = self.kwargs['pk']
        answer = Answer.objects.get(id=answer_id)
        self.pk = answer.question.id
        context['answer_text'] = answer.answer_text
        return context

    def get_success_url(self):
        return (reverse('question-detail', kwargs={'pk': self.object.question.id}))

class DeleteAnswer(LoginRequiredMixin, DeleteView):
    model = Answer
    template_name = 'konnectapp/answer_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answer_id = self.kwargs['pk']
        answer = Answer.objects.get(id=answer_id).delete()
        #self.pk = answer.question.id

        return context

    def get_success_url(self):
        return (reverse('question-detail', kwargs={'pk': self.object.question.id}))

class UpdateQuestion(LoginRequiredMixin, UpdateView):
    model = Question
    fields = ['question_text','question_title']
    success_url = reverse_lazy('questions')
    template_name = 'konnectapp/question_update_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_id = self.kwargs['pk']
        question = Question.objects.get(id=question_id)
        context['question_text'] = question.question_text
        context['question_title'] = question.question_title
        return context
class DeleteQuestion(LoginRequiredMixin, DeleteView):
        model = Question
        success_message = "Deleted Successfully"
        success_url = reverse_lazy('questions')
        template_name = 'konnectapp/question_delete.html'
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            question_id = self.kwargs['pk']
            question = Question.objects.get(id=question_id).delete()


            #context['question_text'] = question.question_text.delete()
            #context['question_title'] = question.question_title.delete()
            return context


class SearchView(ListView):
    template_name = 'views.html'
    paginate_by = 20
    count = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.count or 0
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)

        if query is not None:
            blog_results = Question.objects.search(query)


            # combine querysets
            queryset_chain = chain(
                    blog_results,

            )
            qs = sorted(queryset_chain,
                        key=lambda instance: instance.pk,
                        reverse=True)
            self.count = len(qs) # since qs is actually a list
            return qs
        return Question.objects.none() # just an empty queryset as default




class CommentCreate(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['author', 'answer', 'comment_text']

    def get(self, request, *args, **kwargs):
        a_id = self.kwargs['pk']
        return render(request, 'konnectapp/comment_form.html', {"a_id": a_id})

    def post(self, request, *args, **kwargs):
        comment_text = request.POST.get('comment_text')
        params = self.kwargs['pk']
        author = Author.objects.get(user=self.request.user)
        answer = Answer.objects.get(id=params)
        Comment.objects.create(
            author=author, answer=answer, comment_text=comment_text)
        response = redirect(
            reverse('question-detail', kwargs={'pk': answer.question.id}))
        return response

class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'konnectapp/comment_delete.html'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        a_id = self.kwargs['pk']
        comment = Comment.objects.get(id=a_id).delete()

        #context['comment_text'] =Comment.comment_text.delete()
        #context['question_title'] = question.question_title.delete()
        return context

class UpvoteCreate(LoginRequiredMixin, CreateView):
    model = Answer
    fields = ['answer_text', 'id', 'upvote']

    def post(self, request, *args, **kwargs):
        answer_id = self.kwargs['pk']
        answer = Answer.objects.filter(id=answer_id).first()

        answer.upvote +=1

        answer.save()

        response = redirect(
            reverse('question-detail', kwargs={'pk': answer.question.id}))
        return response

    """def vote_foo_question(request, **kwargs, value):


        answer_id = self.kwargs['pk']
        answer = get_object_or_404(Answer, pk=answer_id)
        vote = Answer.objects.filter(user_id=answer_id).first()



        vote.value = value
        vote.save()
        question.update_votes()
        question.save()

        return redirect('questions:show', question_id)"""






class QuestionCreate(LoginRequiredMixin, CreateView):
    model = Question
    fields = ['question_title','question_text', 'tags']



    def get(self, request, *args, **kwargs):
        return render(request, 'konnectapp/question_form.html')

    def post(self, request, *args, **kwargs):
        question_title = request.POST.get('question_title')
        question_text = request.POST.get('question_text')


        question = Question.objects.create(author=Author.objects.get(user=self.request.user),question_text=question_text,question_title=question_title)



        response = redirect('/konnectapp/questions')
        return response
    def tagged(request, slug):
        tags = get_object_or_404(Tags, slug=slug)
        common_tags = Question.tags.most_common()[:4]
        posts = Question.objects.filter(tags=tag)
        context = {
            'tag':tag,
            'common_tags':common_tags,
            'question':question,
            }
        response = redirect('/konnectapp/questions')
        return response


class AnswerCreate(LoginRequiredMixin, CreateView):
    model = Answer
    fields = ['answer_text']

    def get(self, request, *args, **kwargs):
        q_id = self.kwargs['pk']
        return render(request, 'konnectapp/answer_form.html', {"q_id": q_id})

    def post(self, request, *args, **kwargs):
        answer_text = request.POST.get('answer_text')
        answer = Answer.objects.create(author=Author.objects.get(
            user=self.request.user), question=Question.objects.get(
                id=self.kwargs['pk']), answer_text=answer_text)
        response = redirect(reverse('question-detail', kwargs={'pk': answer.question.id}))
        return response


class AuthorCreate(CreateView):
    model = Author
    fields = ['email']

    def get(self, request, *args, **kwargs):
        return render(request, 'konnectapp/author_form.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        year = request.POST.get('year')
        email = request.POST.get('email')

        if password1 == password2:
            hasher = PBKDF2PasswordHasher()
            password = hasher.encode(
                password=password1, salt='salt', iterations=150000)
        try:
            user = User.objects.create(username=username, password=password)
            Author.objects.create(user=user, email=email,year=year )
        except IntegrityError:
            return render(request, 'konnectapp/userexists.html')
            #return response
            raise ValidationError(_("This username has already existed."))
        else:
            response = redirect('/accounts/login')
            return response




class AuthorUpdate(UpdateView):
    model = Author
    fields = ['email']


class AuthorDelete(DeleteView):
    model = Author
    fields = ['user']
    fields = ['email']
    fields = ['credits']
    success_url = reverse_lazy('questions')


class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an Author."""
    model = Author


class QuestionDetailView(generic.DetailView):
    """Generic class-based detail view for a Question."""
    model = Question

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_id = self.kwargs['pk']
        question = Question.objects.get(id=question_id)
        answer_list = Answer.objects.filter(question=question)
        comment_dictionary = {
                ans.id: Comment.objects.filter(answer=ans) for ans in answer_list
            }


        context['answer_list'] = answer_list
        context['answer_url'] = '/konnectapp/question/'+str(question_id)+'/answer/'
        context['upvote_url'] = '/konnectapp/answer/upvote/'
        context['downvote_url'] = '/konnectapp/answer/downvote/'
        context['comment_dictionary'] = comment_dictionary
        return context




class AnswerListView(generic.ListView):
    model = Answer
    paginate_by = 3


class QuestionListView(generic.ListView):
    model = Question
    paginate_by = 7


    ordering = 'time_created' and '-date_created'




def index(request):
    """View function for home page of site."""
    num_questions = Question.objects.all().count()
    num_answers = Answer.objects.all().count()
    num_authors = Author.objects.count()
    num_comments = Comment.objects.count()
    context = {
        'num_questions': num_questions,
        'num_answers': num_answers,
        'num_authors': num_authors,
        'num_comments': num_comments,
    }
    return render(request, 'index.html', context=context)
def about(request):
    """View function about"""

    return render(request, 'about.html')


def overview(request):
    if request.method == "POST":
        form = NewIndexForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = NewIndexForm()

    indexes = Question.objects.all()

    context = {'form': form,
               'indexes': indexes
           }

    return render(request, 'over.html', context)

def tagged(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    questions_list = Question.objects.filter(tags=tag)

    paginator = Paginator(questions_list, 10)

    page = request.GET.get('page')

    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    context = { 'questions': questions, 'tag': tag }
    return render(request, 'questions/tagged.html', context)
