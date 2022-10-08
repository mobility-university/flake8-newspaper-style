# Enforce Newspaper Style with Flake

## Motivation

Good code reads like a newspaper. Start with the highest abstraction, go to the details.
This also enables to read the code without an editor.

Quoting Robert C. Martin from his Clean Code book.

“Think of a well-written newspaper article. You read it vertically. At the top you expect a headline that will tell you what the story is about and allows you to decide whether it is something you want to read. The first paragraph gives you a synopsis of the whole story, hiding all the details while giving you the broad-brush concepts. As you continue downward, the details increase until you have all the dates, names, quotes, claims, and other minutia.”

In Python newspaper code should look like this.

```py
def headline():
    text()

def text():  # this needs to be defined after the usage.
    ...
```

There hasn't been an automatic way in python to check for this. So here it is.

## Usage

```py
# install the flake8 extension for newspaper style
pip3 install flake8-newspaper-style==0.4.2
# then check your code
flake8 --select=NEW src  # here it restricts flake8 to newspaper style issues
```

## References

 - Clean Code book by Robert C. Martin
 - [Clean Code formatting matters](https://www.codingblocks.net/podcast/clean-code-formatting-matters/)
