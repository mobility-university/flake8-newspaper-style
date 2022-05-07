Feature: Simple

  Background:
    Given I installed flake8-enforce-newspaper-style

  Scenario: Check
    Given I have a file with
      """
      def text():
        ...

      def headline():
        text()
      """
    When I flake8 this file
    Then it fails with
      """
      file(5): violation of newspaper style. Function defined in line 1
      """

  Scenario: Check
    Given I have a file with
      """
      def headline():
        text()

      def text():
        ...
      """
    When I flake8 this file
    Then it succeeds
