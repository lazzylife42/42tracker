from enum import Enum as PyEnum
from sqlalchemy import Column, Enum, Boolean, Integer, Float, String, DateTime
from database import BASE

# PROJECT 42
class BlocEnum(PyEnum):
	ai = "AI"
	db = "DB"
	common_core = "Common Core"

class ProjectStatusEnum(PyEnum):
	todo = "todo"
	in_progress = "in_progress"
	done = "done"

class Projects_42(BASE):
	__tablename__ = "projects_42"
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	slug = Column(String, nullable=False, unique=True)
	xp = Column(Integer)
	bloc = Column(Enum(BlocEnum))
	status = Column(Enum(ProjectStatusEnum), nullable=False)
	mark = Column(Integer)
	validated = Column(Boolean)
	validated_at = Column(DateTime)
	retriable_at = Column(DateTime)
	estimated_hours = Column(Integer)
	order_priority = Column(Integer)

# LEETCODE STATS
class LeetCode(BASE):
	__tablename__ = "leetcode_stats"
	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, nullable=False)
	easy_solved = Column(Integer)
	medium_solved = Column(Integer)
	hard_solved = Column(Integer)
	total_solved = Column(Integer)
	streak = Column(Integer)
	synced_at = Column(DateTime, nullable=False)

# LEETCODE PATTERNS
class PatternsEnum(PyEnum):
	array = "Arrays"
	two_pointer = "Two Pointers"
	sliding_window = "Sliding Window"
	stack = "Stack"
	binary_search = "Binary Search"
	linked_list = "Linked List"
	trees = "Trees"
	graphes = "Graphs"
	heaps = "Heaps"
	dynamic_programming = "Dynamic Programming"

class LeetCodePatterns(BASE):
	__tablename__ = "leetcode_patterns"
	id = Column(Integer, primary_key=True, index=True)
	pattern_name = Column(Enum(PatternsEnum), nullable=False)
	target_count = Column(Integer, nullable=False, default=0)
	solved_count = Column(Integer, nullable=False, default=0)

# SKILS GAP
class CategoryEnum(PyEnum):
	system_design = "System Design"
	ml_theory = "Machine Learning Theory"
	mlops = "Machine Learning Operational"
	soft_skills = "Soft Skills"
	project = "Project"
	opensource = "Open Source Contribution"

class SkillsGapStatusEnum(PyEnum):
	todo = "todo"
	in_progress = "in_progress"
	done = "done"

class SkillsGap(BASE):
	__tablename__ = "skills"
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	category = Column(Enum(CategoryEnum), nullable=False)
	status = Column(Enum(SkillsGapStatusEnum), nullable=False, default=SkillsGapStatusEnum.todo)
	notes = Column(String)
	updated_at = Column(DateTime)

# WORK SESSIONS
class SkillTypeEnum(PyEnum):
	leet_code = "Leet Code"
	project_42 = "42 Project"
	reading = "Reading"
	mock_interview = "Mock Interview"
	music_daemon = "Music Daemon"
	mappy = "Mappy"
	forty_two_tracker = "42tracker"
	outreach = "Outreach"

class WorkSession(BASE):
	__tablename__ = "work_sessions" 
	id = Column(Integer, primary_key=True, index=True)
	date = Column(DateTime, nullable=False)
	type = Column(Enum(SkillTypeEnum), nullable=False)
	duration_minutes = Column(Integer, nullable=False)
	notes= Column(String)

# OUTREACH PIPELINE
class ContactStatus(PyEnum):
	identified = "Identified"
	contacted = "Contacted"
	replied = "Replied"
	call_done = "Call Done"
	referral = "Referral"
	applied = "Applied"

class Contacts(BASE):
	__tablename__ = "contact"
	id = Column(Integer, primary_key=True, index=True)
	company = Column(String, nullable=False)
	name = Column(String, nullable=False)
	linkedin_url = Column(String)
	role = Column(String, nullable=False)
	status = Column(Enum(ContactStatus), nullable=False)
	date_contacted = Column(DateTime)
	notes = Column(String)

# READINESS SCORE
class ReadinessSnapshots(BASE):
	__tablename__ = "readiness_snapshots"
	id = Column(Integer, primary_key=True, index=True)
	computed_at = Column(DateTime, nullable=False)
	rncp_ai_pct = Column(Float)
	rncp_db_pct = Column(Float)
	leetcode_pct = Column(Float)
	skills_pct = Column(Float)
	outreach_pct = Column(Float)
	global_score = Column(Float)
