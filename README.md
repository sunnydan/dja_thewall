Assignment: The Wall
Create a wall/forum page where users will be able to post a message and see the message displayed by other users. Store the messages in a table called 'messages' and retrieve the messages from the database. Follow the below wireframe.

1. Create a login and registration page that is displayed when a user navigates to 'localhost:5000/'

2. Once the user has logged in successfully redirect them to 'localhost:5000/wall' that will show the wall.

Once you get the messages to show up, allow users to post comments for any message. Store the replies/comments to the message in a separate table called 'comments'.

Extra Credit I (optional) 
Allow the user to delete his/her own messages.

Extra Credit II (optional)
Allow the user to delete his/her own message but only if the message was made in the last 30 minutes.

Assignment: Semi-Restful Users
Create a web app that can handle all of the CRUD operations (create, read, update and destroy) for a table. Use your friends database for the following assignment.

But first, what does REST mean?
It's very common for a web application to provide the user interface for creating, reading, updating, or destroying a 'resource' (a table). For example, imagine you want to build a web application that allows the user to create/read/update/destroy users. There are many ways that you can build web applications like this. For example, you could have resources called users, products, pd (short for products) and so forth. You could also have different methods that essentially do the same thing. So, to display user information for user id 1, you could have the URL 'users/1' provide this info or 'users/show/1' or 'users/show_info/1' or 'users/display/1', etc.

Since many web applications perform CRUD operations, you can imagine how confusing this could get if everyone followed different conventions for creating routing and method names for these operations.

A REST or RESTful route is simply a set of route naming conventions that the industry has agreed to follow in order to make it easier to send requests to APIs. It's up to you whether you also follow these rules/conventions but we strongly encourage you to get familiar with how the following rules for RESTful routing, as you may be making requests to, or someday creating your own, API.

Right now with Flask, it's not quite possible for you to do the full RESTful architecture, so the exercise below is to help you get somewhat familiar with RESTful routes. Later when you get into other stacks (such as MEAN or Rails), you'll already be somewhat familiar with REST concepts.

Follow the instructions in the wireframe below to build this application in Flask.