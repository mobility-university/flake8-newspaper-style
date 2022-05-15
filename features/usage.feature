Feature: Usage

  Background:
    Given I installed flake8-newspaper-style

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
      file:5:5: NEWS100 newspaper style: function text defined in line 1 should be moved down
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
