import os
import unittest

from ogr import GithubService, get_project
from ogr.mock_core import PersistentObjectStorage
from ogr.services.github import GithubProject
from ogr.services.mock.pagure_mock import PagureMockAPI
from ogr.services.pagure import PagureProject

DATA_DIR = "test_data"
PERSISTENT_DATA_PREFIX = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), DATA_DIR
)


class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.github_user = os.environ.get("GITHUB_USER")
        self.pagure_token = os.environ.get("PAGURE_TOKEN")
        self.pagure_user = os.environ.get("PAGURE_USER")

        test_name = self.id() or "all"

        persistent_data_file = os.path.join(
            PERSISTENT_DATA_PREFIX, f"test_factory_data_{test_name}.yaml"
        )
        self.persistent_object_storage = PersistentObjectStorage(persistent_data_file)

        if self.persistent_object_storage.is_write_mode and (
            not self.github_user or not self.github_token
        ):
            raise EnvironmentError("please set GITHUB_TOKEN GITHUB_USER env variables")

        if self.persistent_object_storage.is_write_mode and (
            not self.pagure_user or not self.pagure_token
        ):
            raise EnvironmentError("please set PAGURE_TOKEN PAGURE_USER env variables")

        self.github_service = GithubService(
            token=self.github_token, persistent_storage=self.persistent_object_storage
        )

        self.pagure_service = PagureMockAPI(
            token=self.pagure_token, persistent_storage=self.persistent_object_storage
        )

    def tearDown(self):
        self.persistent_object_storage.dump()

    def test_get_project_github(self):
        project = get_project(
            url="https://github.com/packit-service/ogr",
            custom_instances=[self.github_service, self.pagure_service],
        )
        assert isinstance(project, GithubProject)
        assert project.github_repo

    def test_get_project_pagure(self):
        project = get_project(
            url="https://src.fedoraproject.org/rpms/python-ogr",
            custom_instances=[self.github_service, self.pagure_service],
        )
        assert isinstance(project, PagureProject)
        assert project.exists()
