# League of Trading
#### Video demo: [video](https://youtu.be/dWvH2dZ4gz4)
### Overview:
This is a virtual card trading website built using python, javascript, html, css and sqlite3 as the main languages.
This platform allows users to sign up using socials or creating a new account, use a lootbox system to gain cards using gems and trade with other users.

####Features
- **User Registration and Authentication:** Users can sign up and log in using their email and a secure password, or their google or github account. This is managed through Auth0 for a more secure authentication, such as brute force protection.
- **Bot Prevention:** When users sign up, they are required to verify their accounts via email as an extra step to try prevent bots from creating accounts. Auth0 also tries to detect for suspiscious behaviour.
- **Gem Management:** Upon first registration, a user receives 100 gems for free. Users can then get a new random card for 10 gems, or enter the marketplace and buy the card they desire, and also sell their cards there to earn gems.
- **Marketplace:** Users can view all cards on sale by all users, on a 'buy' page. This page excludes the user's cards so they don't buy their own card. There is another 'sell' page where the user can view which cards they already have on sale, allowing them to change their pricing or cancelling the sale. They will also see all of their available cards, that can be selected and put up for sale.
- **Collection:** Users can see their entire collection and select a card to view it enlarged with it's name and value. Users can also see the quantity of each card owned.
- **Dynamic Pricing:** Cards have different values based on their rarity, and users can set their own prices when selling their cards, whether above or below value is up to them.
- **Account Management:** Users can view their account details and change their username, no matter how they have signed up. Usernames will be assigned locally should a user sign up through their socials.
Users who have created a new account, can also change their password through their account page.
- **Animated Background:** The websites theme background rotates through images, and zooms in and pans around for an animated effect.
- **Password Reset:** If a user has signed up with a new account, they can request to reset their password should they forget it. They will then receive an email with a link to reset their password. This can also be done from the accounts page as well as the login screen.

### Design Choices
#### Technologies and APIs
- **Auth0:** I wanted to learn how to implement an API and so I looked up a few ideas. There were many to choose from, but I thought it would be great to allow a user to sign up using their social accounts. Auth0 allowed for this as well as having bot detection, email verification, brute force protection and more. I thought it would simplify my login and and sign-ups flows, but it did add complications, however it is still more secure and was a great learning experience.
- **Flask:** I wanted a more dynamic website that changes for the users, and works with backend. Flask was easy to setup and works very well with python. Python also works well with sqlite so that was chosen for my database. It took many attempts getting auth0's database to intergrate with my database.
- **JavaScript:** I had to create a few custom scripts for my webpage that I couldn't figure out how to do using Jinja or Python, such as calculating the total cost of selected cards in real-time before submitting the form.
- **Bootstrap:** Majority of the sites front-end is thanks to bootstrap but I did have to edit some of the classes and go through a lot of trial and error with my background using the carousel class.

#### Design Considerations
- **User Experience:** I wanted the site to have a captivating background and be easy to navigate. The cards are interactive, but I would've like to make the submission forms a little more user friendly and assign default values. I have added placeholders and heading and checkboxes to make things easier to understand. I implemented features that prevent users from doing things they shouldn't, such as buying more cards than they can afford, a pop up will appear and the submit button disables.
- **Mobile Friendly:** In most cases, the site works well on mobile, however I didn't get the background perfect and instead added a darker theme to make it look more natural when the background image gets too small. There are some parts that sometimes don't look great on mobile but they still function, unfortunately this also altered my initial design on desktop but I feel that I got a good design for both within the timeframe.
- **Security:** I wanted brute force protection, and bot detection, and extra layers of security. Auth0 allowed for this but added complications as the unique ID's created and all the user information upon account creation was on their database, so I had to find a way to get the details I required and add it to my database and then to call back to Auth0 when required using just the unique Auth0 user ID to maintain data integrity.
- **Dynamic Content:** Using JavaScript, I was able to update certain information without needing to reload the page, creating a smoother user experience.
- **Login authentiication:** Every page checks whether the user is logged in or not. If the user is not logged in, they are shown a page asking them to sign in.

### File Structure
#### Templates:
No login html was required as I created it within Auth0's client and my python code refers to it.
- **account.html:** All known information about the user is shown on this page.
The user can then alter their username if they wish.
The password change button only works for users who create a new account without logging in through scoials. When they click the button, they are sent an email with a reset password link.
- **buy.html:** Here all cards on sale by all users, apart from the current user, are shown. It is a form where the image of the card is selectable, shows the value of the card and then how much it is being sold for. On top of the form it shows how many gems the user has and at the bottom, as the user selects cards, the total is calculated in real-time and shown to the user.
- **sell.html:** A form that shows users their cards currently on sale, if they have any. This form allows the user to update the pricing or return the card back to their collection.
 Below that form is another form that shows all the users owned cards with their values and inputs next to them to set pricing and the quantity they want to sell. Despite choosing multiple of the same card, e.g., quantity of 3, they all become unique sales. AKA, If you choose one card that you own many of and say sell 2 of them, in the trade table, this will show as 2 sales.
- **trade.html:** This is simply a page where a users chooses whether they want to sell or buy cards
- **layout.html:** This is the default layout of the website that each page uses
- **collection.html:** This page shows a large image of the first card owned by default, along with the card name and value. Below that is a all the cards owned as smaller images. When a user clicks on any of the smaller cards, they replace the large image in real-time without refreshing and shows that cards details
- **index.html:** Here the user will be welcomed by name.
They can see how many gems they currently have and can reveal a new card for 10 gems. Below the card, it shows the percentage chance of which value card you will get. When a user clicks to reveal a new card, a flash of the new card is shown.

#### Static
- **images:** This stores all the images always available to the website for all users such as the background.
- **cards:** These are strictly for the collectable cards that python logic uses for loops and the database refers to.
- **custom JS:** I kept all my javascript in a separate file to keep my HTML clean and allow other pages access to the same functions if required. This is client-side logic.
- **styles.css:** Here I have my classes and ids as well as any bootstrap alterations. This determines the websites theme, colours and layout.

#### Root
- **app.py:** The main application to run flask with all the python functions, route handling, interaction with both databases and all the backend logic.
- **cardtrading.db:** My SQL database that stores all the information on users, the cards they own, the cards themselves etc. and to maintain the marketplace
- **requirements.txt:** Lists all the dependencies required to run the project
- **README.md:** This file for CS50 explaining the project
