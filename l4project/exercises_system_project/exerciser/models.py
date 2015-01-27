from django.db import models
from django.contrib.auth.models import User



class Application(models.Model):
    name = models.CharField(max_length = 128, primary_key = True)
    layout = models.CharField(max_length = 128)

    def __unicode__(self):
        return self.name

class Document(models.Model):
    name = models.CharField(max_length=128, unique=True, primary_key = True)
    type = models.CharField(max_length=128)
    kind = models.CharField(max_length=128)
    fixOrder = models.BooleanField()

    def __unicode__(self):
        return self.name

class Fragment(models.Model):
    document = models.ForeignKey(Document)
    id = models.CharField(max_length=128,unique=True,primary_key=True)
    text = models.TextField()
    type = models.CharField(max_length=128)
    order = models.IntegerField()

    def __unicode__(self):
        return " ".join((self.text, self.id))
		
	def __init__(self, *args, **kwargs):
		super(Fragment, self).__init__(*args, **kwargs)
		self.visible = False
		self.highlighted = False
		
	def reset(self):
		self.visible = False
		self.highlighted = False
		
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    type = models.CharField(max_length=128)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username


class Step(models.Model):
    application = models.ForeignKey(Application)
    order = models.IntegerField()

    def __unicode__(self):
        return str(self.order)
		
class Question(models.Model):
    application = models.ForeignKey(Application)
    step = models.ForeignKey(Step)
    question_text = models.TextField()

    def __unicode__(self):
        return self.question_text

class Change(models.Model):
	step = models.ForeignKey(Step)
	fragment = models.ForeignKey(Fragment, blank=True, null=True)
	question = models.ForeignKey(Question, blank=True, null=True)
	document = models.ForeignKey(Document)
	operation = models.CharField(max_length=128)

	def getChanges(self):
		if self.operation == 'Insert':
			return [[self.fragment.id, 'show']]
		elif self.operation == 'Highlight':
			return [[self.fragment.id, 'highlight']] #change later
		elif self.operation == 'Unhighlight':
			return [[self.fragment.id, 'unhighlight']]
		elif self.operation == 'Show all':
			result = []
			fragments = Fragment.objects.filter (document = self.document)
			for fragment in fragments:
				result.append([fragment.id, 'show'])
			return result
		elif self.operation == 'Ask Answer':
			question_text = self.question.question_text
			options = Option.objects.filter(question = self.question)
			option_list = []
			for option in options:
				option_list.append(option.content)
			return [[question_text, 'question', option_list]]
		else:
			return [[self.fragment.id, 'hide']]#default behaviour
		
	def __unicode__(self):
		return " ".join(("Document: ", self.document.name," | Step: ", str(self.step.order), " | Text: ",self.fragment.text, " | Operation:", self.operation ))

class Explanation(models.Model):
    step = models.ForeignKey(Step)
    text = models.TextField()

    def __unicode__(self):
        return self.text
		

class Option(models.Model):
    question = models.ForeignKey(Question)
    number = models.IntegerField()
    content = models.CharField(max_length = 256)


    def __unicode__(self):
        return " ".join(("ID",str(self.id),"Option: ", str(self.number), ". ", self.content))

		
class Panel(models.Model):
	application = models.ForeignKey(Application)
	document = models.ForeignKey(Document)
	type = models.CharField(max_length = 128)
	number = models.IntegerField()
	
	
	
	
	def __init__(self, *args, **kwargs):
		super(Panel, self).__init__(*args, **kwargs)
		self.fragment_operation_mapping = self.initialise_fragment_operation_mappings()
		
		
	def __unicode__(self):
		return " ".join((str(self.number) ,self.application.name))
		
	def initialise_fragment_operation_mappings(self):
		mappings = []
		for fragment in Fragment.objects.filter(document = self.document):
			index = fragment.order
			mappings.insert(index,{fragment.text : 'show'}) #should be hide!!!
		return mappings
	def getFragments(self):
		return Fragment.objects.filter(document = self.document)

class AcademicYear(models.Model):
	start = models.IntegerField(primary_key=True)
		
class Teacher(models.Model):
	user = models.OneToOneField(User)
	can_analyse = models.BooleanField(default=False)
		
class Group(models.Model):
	teacher = models.ForeignKey(Teacher)
	academic_year = models.ForeignKey(AcademicYear)
	name = models.CharField(max_length=100, unique=True)
	
class Student(models.Model):
	teacher = models.ForeignKey(Teacher)
	group = models.ForeignKey(Group)
	student_id = models.CharField(max_length=2)
	
	def __unicode__(self):
		return " ".join((" teacher: ",self.teacher.user.username," group: ",self.group.name, " name",self.student_id))
	
class UsageRecord(models.Model):
	application = models.ForeignKey(Application)
	teacher = models.ForeignKey(Teacher, blank=True, null=True)
	group = models.ForeignKey(Group, blank=True, null=True)
	student = models.ForeignKey(Student, blank=True, null=True)
	step = models.ForeignKey(Step)
	session_id = models.CharField(max_length=100)
	time_on_step = models.FloatField(default=0)
	direction = models.CharField(max_length=10)

	
	def __unicode__(self):
		if self.teacher != None:
			teacher=self.teacher.user.username
		else:
			teacher="No teacher"
		if self.group != None:
			group=self.group.name
		else:
			group="No group"
		if self.student != None:
			student=self.student.student_id
		else:
			student="No student id"
		return " ".join((self.application.name ," teacher: ",teacher," group: ",group," student: ",student))

"""
class QuestionRecord1(models.Model):
	record = models.OneToOneField(UsageRecord)
	answer = models.ForeignKey(Option)
"""

class QuestionRecord(models.Model):
	application = models.ForeignKey(Application)
	question = models.ForeignKey(Question)
	teacher = models.ForeignKey(Teacher, blank=True, null=True)
	group = models.ForeignKey(Group, blank=True, null=True)
	student = models.ForeignKey(Student, blank=True, null=True)
	session_id = models.CharField(max_length=100)
	answer = models.ForeignKey(Option)

class SampleQuestionnaire(models.Model):
	FRESHMAN = 'FR'
	SOPHOMORE = 'SO'
	JUNIOR = 'JR'
	SENIOR = 'SR'
	YEAR_IN_SCHOOL_CHOICES = (
		(FRESHMAN, 'Freshman'),
		(SOPHOMORE, 'Sophomore'),
		(JUNIOR, 'Junior'),
		(SENIOR, 'Senior'),
	)
	year_in_school = models.CharField(max_length=2,
										choices=YEAR_IN_SCHOOL_CHOICES,
										default=FRESHMAN)
	year_in_school2 = models.CharField(max_length=2,
										choices=YEAR_IN_SCHOOL_CHOICES,
										default=SENIOR)
	school=models.CharField(max_length=100)
	bool=models.BooleanField()
	comment=models.TextField()
	

