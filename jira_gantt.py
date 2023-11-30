import datetime
import gantt
from jira import JIRA

# """没有子任务的项目"""
# class JiraVersionChart(object):
#     """A chart of Jira project versions"""
#     def __init__(self, project):
#         self.project = project
#
#     def generate_chart(self):
#         """
#         Creates a version chart SVG.
#         """
#         p = gantt.Project(name=self.project.name)
#         for version in self.project.versions:
#             if hasattr(version, 'startDate') and hasattr(version, 'releaseDate'):
#                 start_date = (int(x) for x in version.startDate.split('-'))
#                 end_date = (int(x) for x in version.releaseDate.split('-'))
#                 task = gantt.Task(name=version.name,
#                                   start=datetime.date(*start_date),
#                                   stop=datetime.date(*end_date))
#                 p.add_task(task)
#         today = datetime.date.today()
#         p.make_svg_for_tasks(filename='{0}_dy.svg'.format(self.project.key),
#                              today=today,
#                              scale=gantt.DRAW_WITH_DAILY_SCALE)
#         p.make_svg_for_tasks(filename='{0}_wk.svg'.format(self.project.key),
#                              today=today,
#                              scale=gantt.DRAW_WITH_WEEKLY_SCALE)
# """有子任务的项目"""
# class JiraEpicChart(object):
#     """A chart of Jira project epics"""
#     def __init__(self, project, epics):
#         self.project = project
#         self.epics = epics
#
#     def generate_chart(self):
#         """
#         Creates an epic chart SVG.
#         """
#         p = gantt.Project(name=self.project.name)
#         for epic in self.epics:
#             if hasattr(epic.fields, 'startDate') and hasattr(epic.fields, 'releaseDate'):
#                 name = epic.fields.customfield_10007
#                 start_date = (int(x) for x in epic.fields.startDate.split('-'))
#                 end_date = (int(x) for x in epic.fields.releaseDate.split('-'))
#                 task = gantt.Task(name=name,
#                                   start=datetime.date(*start_date),
#                                   stop=datetime.date(*end_date))
#                 p.add_task(task)
#         today = datetime.date.today()
#         p.make_svg_for_tasks(filename='{0}_dy.svg'.format(self.project.key),
#                              today=today,
#                              scale=gantt.DRAW_WITH_DAILY_SCALE)
#         p.make_svg_for_tasks(filename='{0}_wk.svg'.format(self.project.key),
#                              today=today,
#                              scale=gantt.DRAW_WITH_WEEKLY_SCALE)
    """
    重构后的代码，将 JiraVersionChart和JiraEpicChart类合并为一个 JiraChart 类
    """
class JiraChart(object):
    """A chart of Jira project versions or epics"""
    def __init__(self, project, chart_type):"""接受的参数versions和epics（子任务）"""
        self.project = project
        self.chart_type = chart_type

    def generate_chart(self):
        """
        Creates a chart SVG.
        """
        p = gantt.Project(name=self.project.name)
        for item in self.project.__getattribute__(self.chart_type):
            if hasattr(item, 'startDate') and hasattr(item, 'releaseDate'):
                name = item.name
                start_date = (int(x) for x in item.startDate.split('-'))
                end_date = (int(x) for x in item.releaseDate.split('-'))
                task = gantt.Task(name=name,
                                  start=datetime.date(*start_date),
                                  stop=datetime.date(*end_date))
                p.add_task(task)
        today = datetime.date.today()
        p.make_svg_for_tasks(filename='{0}_dy.svg'.format(self.project.key),
                             today=today,
                             scale=gantt.DRAW_WITH_DAILY_SCALE)
        p.make_svg_for_tasks(filename='{0}_wk.svg'.format(self.project.key),
                             today=today,
                             scale=gantt.DRAW_WITH_WEEKLY_SCALE)

"""调用生成SVG图像"""
project = JIRA().project('PROJECT_KEY')
version_chart = JiraChart(project, 'versions')
version_chart.generate_chart()

epics = JIRA().search_issues('project=PROJECT_KEY and issuetype=Epic')
epic_chart = JiraChart(project, 'epics')
epic_chart.generate_chart()


class JiraConnection(object):
    """Manages a connection to a Jira database"""
    def __init__(self):
        self.jira = None
        self.project = None

    def connect(self, url, user, passwd):
        """
        Connect to a Jira server

        Arguments:
        url    -- URL of the Jira server
        user   -- username
        passwd -- password
        """
        options = {'server': url}
        self.jira = JIRA(options, basic_auth=(user, passwd))

    def get_project_list(self):
        """
        Returns a list of available projects.
        Projects are tuples with the format (key, name).
        """
        plist = []
        for project in self.jira.projects():
            plist.append((project.key, project.name))
        return plist

    def set_project(self, key):
        """
        Sets the active project.

        Arguments:
        key -- project key
        """
        self.project = self.jira.project(key)
    
    def get_epic_list(self, project=None):
        """
        Returns a list of epics for the project.

        Arguments:
        project -- project key (optional if project is set)
        """
        if project is None and self.project is not None:
            project = self.project.key
        else:
            raise ValueError('A project is required')

        return self.jira.search_issues('project={0} and type=Epic'.format(project))
