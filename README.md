# Youra Back End
Mackenna

## Planning:

### Concept/Name
Youra (Your Aura) is a platform designed to inspire and track acts of kindness within a community. Users can create, request, and fulfill Random Acts of Kindness (RAK's) and share their experiences. The platform encourages positive actions and rewards users with badges and aura points for their contributions.

### Intended Audience/User Stories
- **Intended Audience**: The intended audience for Youra includes individuals who are passionate about community service, random acts of kindness, and social responsibility. It's also designed for those who want to track and be recognised for their positive actions.
- **User Stories**:
  - As a user, I want to create an offer to perform an act of kindness so that others can benefit from my help.
  - As a user, I want to request a Random Act of Kindness when I need support in a particular area (e.g., help with groceries, buying a coffee).
  - As a user, I want to claim an existing offer so that I can help someone in need.
  - As a user, I want to earn aura points and badges for completing acts of kindness to track my contributions.
  - As a user, I want to view a history of my RAKs to see my impact.

### Front End Pages/Functionality
- **Home Page**
  - Displays a feed of active RAK posts (offers and requests).
  - Users can filter and search for specific types of RAKs.
  - Provides an overview of the user's aura level and badges.
- **RAK Creation Page**
  - Allows users to create a new Random Act of Kindness (offer or request).
  - Users can upload media and set the visibility of their RAK (public/private).
- **RAK Detail Page**
  - Shows details about a specific RAK post, including the owner and claimant.
  - Users can claim an offer or fulfill a request.
  - Displays comments and updates from users involved in the RAK.
- **User Profile Page**
  - Shows user's history of RAKs (both offers and requests).
  - Displays badges earned and current aura level.
  - Users can edit their profile information.

### API Spec

| URL                 | HTTP Method | Purpose                   | Request Body                         | Success Response Code | Authentication/Authorisation  |
|---------------------|-------------|---------------------------|--------------------------------------|-----------------------|-------------------------------|
| `/api/rakposts/`    | GET         | List all RAK posts        | None                                 | 200                   | None                          |
| `/api/rakposts/`    | POST        | Create a new RAK post     | `{ description, media, post_type }`  | 201                   | Authenticated users only      |
| `/api/rakposts/<pk>/` | GET       | Retrieve a specific RAK   | None                                 | 200                   | None                          |
| `/api/rakposts/<pk>/` | PUT       | Update a specific RAK     | `{ description, status, visibility }`| 200                   | Owner only                    |
| `/api/rakposts/<pk>/` | DELETE    | Delete a specific RAK     | None                                 | 204                   | Owner only                    |
| `/api/claimedraks/` | GET         | List all claimed RAKs     | None                                 | 200                   | None                          |
| `/api/claimedraks/` | POST        | Claim a RAK post          | `{ rak_id, details }`                | 201                   | Authenticated users only      |
| `/api/claimactions/`| GET         | List all claim actions    | None                                 | 200                   | None                          |
| `/api/claimactions/`| POST        | Create a new claim action | `{ claimed_rak_id, action_type }`    | 201                   | Authenticated users only      |

### DB Schema
![]( ../class.png)

