# constant.py

from enum import Enum


BASE_URL = 'https://www.gradescope.com'
LOGIN_URL = f'{BASE_URL}/login'
GRADEBOOK = 'https://www.gradescope.com/courses/{course_id}/gradebook.json?user_id={member_id}'
PAST_SUBMISSIONS = '.json?content=react&only_keys%5B%5D=past_submissions'


ROLE_MAP = {
    'student': 'Student Courses',
    'instructor': 'Instructor Courses'
}


class Role(Enum):
    STUDENT     = 'student'
    INSTRUCTOR  = 'instructor'



# gradescope.py

import re
import requests
import logging as log
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

# dataclass.py

from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class Course:
    '''Represents a course in Gradescope.'''
    course_id: int
    url: str
    role: Role
    term: str
    short_name: str
    full_name: str

    def get_url(self) -> str:
        '''Returns the full URL of the course.'''
        return urljoin(BASE_URL, self.url)


@dataclass
class Assignment:
    '''Represents an assignment in Gradescope.'''
    assignment_id: int
    assignment_type: str
    url: str
    title: str
    container_id: str
    versioned: bool
    version_index: str
    version_name: str
    total_points: str
    student_submission: str
    created_at: str
    release_date: str
    due_date: str
    hard_due_date: str
    time_limit: str
    active_submissions: int
    grading_progress: int
    published: bool
    regrade_requests_open: bool
    regrade_requests_possible: bool
    regrade_request_count: int
    due_or_created_at_date: str

    # Not included:
    # edit_url
    # edit_actions_url
    # has_section_overrides
    # regrade_request_url

    def get_url(self) -> str:
        '''Returns the full URL of the assignment.'''
        return urljoin(BASE_URL, self.url)

# GradeScope

class Gradescope:
    '''
    A Python wrapper for Gradescope to easily retrieve data from your Gradescope Courses.
    '''
    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        auto_login: bool = True,
        verbose: bool = False
    ) -> None:
        '''
        Initializes a Gradescope object.

        Args:
            username (str | None): The username for logging into Gradescope. Defaults to None.
            password (str | None): The password for logging into Gradescope. Defaults to None.
            auto_login (bool): Whether to automatically login upon object initialization. Defaults to True.
            verbose (bool): Whether to enable verbose logging. Defaults to False.
        '''
        self.session = requests.session()
        self.username = username
        self.password = password
        self.verbose = verbose
        self.logged_in = False

        if self.verbose:
            log.basicConfig(level=log.INFO)
        else:
            log.basicConfig(level=log.WARNING)

        if auto_login and (not (username is None and password is None)):
            self.login()

    def login(self, username: str | None = None, password: str | None = None) -> bool:
        '''
        Log into Gradescope with the provided username and password.

        Args:
            username (str | None): The username for logging into Gradescope. Defaults to None.
            password (str | None): The password for logging into Gradescope. Defaults to None.

        Returns:
            bool: True if login is successful, False otherwise.
        
        Raises:
            TypeError: If the username or password is None.
            LoginError: If the return URL after login is unknown.
        '''
        if username is not None: self.username = username
        if password is not None: self.password = password
        if self.username is None or self.password is None:
            raise TypeError('The username or password cannot be None.')

        response = self.session.get(BASE_URL)
        self._response_check(response)
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find('input', attrs={'name': 'authenticity_token'})

        if token_input:
            authenticity_token = token_input.get('value')
            log.info(f'[Login] Authenticity Token: {authenticity_token}')
        else:
            log.warning('[Login] Authenticity token not found.')

        data = {
            'authenticity_token': authenticity_token,
            'session[email]': self.username,
            'session[password]': self.password,
            'session[remember_me]': 0,
            'commit': 'Log In',
            'session[remember_me_sso]': 0,
        }
        response = self.session.post(LOGIN_URL, data=data)
        self._response_check(response)

        log.info(f'[Login] Current URL: {response.url}')
        if 'account' in response.url:
            log.info('[Login] Login Successful.')
            self.logged_in = True
            return True
        elif 'login' in response.url:
            log.warning('[Login] Login Failed.')
            self.logged_in = False
            return False
        else:
            self.logged_in = False
            raise LoginError('Unknown return URL.')

    def get_courses(self, role: Role) -> list[Course]:
        '''
        Retrieves the list of courses for the specified role.

        Args:
            role (Role): The role for which to retrieve the courses.

        Returns:
            list[Course]: The list of courses for the specified role.

        Raises:
            NotLoggedInError: If not logged in.
            ResponseError: If the heading for the specified role is not found.
        '''
        if not self.logged_in: raise NotLoggedInError

        response = self.session.get(BASE_URL)
        self._response_check(response)
        soup = BeautifulSoup(response.text, 'html.parser')

        courses = list()
        current_heading = soup.find('h1', string=ROLE_MAP[role.value])
        if not current_heading:
            current_heading = soup.find('h1', class_ ='pageHeading')
        if current_heading:
            course_lists = current_heading.find_next_sibling('div', class_='courseList')
            for term in course_lists.find_all(class_='courseList--term'):
                term_name = term.get_text(strip=True)
                courses_container = term.find_next_sibling(class_='courseList--coursesForTerm')
                if courses_container:
                    for course in courses_container.find_all(class_='courseBox'):
                        if course.name == 'a':
                            courses.append(
                                Course(
                                    course_id=self._parse_int(course.get('href', '').split('/')[-1]),
                                    url=course.get('href', None),
                                    role=role.value,
                                    term=term_name,
                                    short_name=course.find(class_='courseBox--shortname').get_text(strip=True),
                                    full_name=course.find(class_='courseBox--name').get_text(strip=True)
                                )
                            )
        else:
            log.warning(f'Cannot find heading for Role: {role}')
            # raise ResponseError(f'Cannot find heading for Role: {role}')
        return courses

    def get_assignments(self, course: Course):
        '''
        Retrieves the list of assignments for the specified course.

        Args:
            course (Course): The course for which to retrieve the assignments.

        Returns:
            list[Assignment]: The list of assignments for the specified course.

        Raises:
            NotLoggedInError: If not logged in.
            ResponseError: If the assignments table is empty or not found for the specified course.
        '''
        if not self.logged_in: raise NotLoggedInError

        response = self.session.get(course.get_url())
        self._response_check(response)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        assignments = list()
        if tables:
            assignments_data = tables[0].find('tbody').find_all('tr')
            for assignment in assignments_data:
                header = assignment.find('th')
                cells = assignment.find_all('td')
                # Title
                title = header.get_text(strip=True)
                url = course.get_url()
                # Status
                status = cells[0].get_text(strip=True)
                # Released & due
                lateStatus = cells[1].find('span', class_='submissionTimeChart--lateStatus')
                if lateStatus:
                    lateStatus = lateStatus.get_text(strip=True)
                    
                remaining = cells[1].find('span', class_='submissionTimeChart--timeRemaining')
                if remaining:
                    remaining = remaining.get_text(strip=True)
                
                releaseDate = cells[1].find('time', class_='submissionTimeChart--releaseDate')
                if releaseDate:
                    releaseDate = releaseDate.get('datetime')
                
                dueDate = cells[1].find_all('time', class_='submissionTimeChart--dueDate')
                if dueDate:
                    dueDate = list(map(lambda x: datetime.strptime(x.get('datetime'), "%Y-%m-%d %H:%M:%S %z").timestamp(), dueDate))
                
                assignments.append({
                    'title': title,
                    'url': url,
                    'status': status,
                    'releaseDate': releaseDate,
                    'dueDate': dueDate,
                    'lateStatus': lateStatus,
                    'remaining': remaining
                })
        return assignments
        # raise ResponseError(f'Assignments Table not found for course ID: {course.course_id}')

    def _response_check(self, response: requests.Response) -> bool:
        '''
        Checks the response status code and raises an error if it's not 200.

        Args:
            response (requests.Response): The response object.

        Returns:
            bool: True if the status code is 200.

        Raises:
            ResponseError: If the status code is not 200.
        '''
        if response.status_code == 200:
            return True
        else:
            raise ResponseError(f'Failed to fetch the webpage. Status code: {response.status_code}. URL: {response.url}')

    def _parse_int(self, text: str) -> int:
        '''
        Parses an integer from a given text.

        Args:
            text (str): The text containing the integer.

        Returns:
            int: The parsed integer.
        '''
        return int(''.join(re.findall(r'\d', text)))

    def _to_datetime(self, text: str) -> datetime:
        '''
        Converts a string to a datetime object.

        Args:
            text (str): The string to be converted.

        Returns:
            datetime: The converted datetime object.
        '''
        return datetime.strptime(text, "%Y-%m-%dT%H:%M")

# errors.py

class GradescopeError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class LoginError(GradescopeError):
    def __init__(self, msg: str = 'Login failed, please check username and password.'):
        super().__init__(msg)


class NotLoggedInError(GradescopeError):
    def __init__(self, msg: str = 'Not logged in.'):
        super().__init__(msg)


class ResponseError(GradescopeError):
    def __init__(self, msg: str):
        super().__init__(msg)