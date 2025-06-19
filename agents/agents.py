from .base import BaseAgent


class ProfileAgent(BaseAgent):
    def __init__(self):
        super().__init__("profile")


class ExperienceAgent(BaseAgent):
    def __init__(self):
        super().__init__("experience")


class ProjectsAgent(BaseAgent):
    def __init__(self):
        super().__init__("projects")


class EducationAgent(BaseAgent):
    def __init__(self):
        super().__init__("education")


class TechnologiesAgent(BaseAgent):
    def __init__(self):
        super().__init__("technologies")


class CertificationsAgent(BaseAgent):
    def __init__(self):
        super().__init__("certifications")
