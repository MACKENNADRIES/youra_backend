# YOURA (Your - Aura)

Mackenna

## Planning:

### Concept/Name
**YOURA** is a social media platform designed to inspire and promote kindness through Random Acts of Kindness (RAKs). Users can post either requests or offers of a RAK, claim acts to fulfil, and earn aura points, which represent their contribution to the kindness community. The more RAKs a user performs, the higher their aura level grows, symbolised by visual elements such as glowing avatars or badges.

The app integrates social media features, allowing users to follow others, share posts, upload media, and comment on acts of kindness. It encourages users to pay it forward after receiving a RAK, ensuring that kindness spreads throughout the community. With a focus on positive interactions, users can take part in kindness challenges, earn achievements, and build an inspiring feed of their contributions.

The app fosters a supportive environment where users can track their impact, connect with like-minded individuals, and share their journey toward making the world a kinder place, all while maintaining privacy and control over their profiles and posts.

### Intended Audience/User Stories
- **Intended Audience**: The intended audience for YOURA includes individuals who are passionate about community service, random acts of kindness, and social responsibility.
- **User Stories**:
  - As a user, I want to post an offer to perform an act of kindness so that others can benefit.
  - As a user, I want to request help through a Random Act of Kindness when I need support.
  - As a user, I want to claim an existing offer so I can help someone in need.
  - As a user, I want to earn aura points and badges for completing acts of kindness to track my contributions.
  - As a user, I want to follow other users who inspire me, and view their RAK contributions.

### Front End Pages/Functionality
- **Home Page**
  - Displays a feed of active RAK posts (offers and requests).
  - Users can filter and search for specific types of RAKs.
  - Provides an overview of the user's aura level and badges.
- **RAK Creation Page**
  - Allows users to create a new RAK (offer or request).
  - Users can upload media (photos, videos) and set the visibility of their RAK (public/private).
- **RAK Detail Page**
  - Displays details about a specific RAK post, including the owner and claimant.
  - Users can claim an offer or fulfil a request.
  - Includes comments and updates from users involved in the RAK.
- **User Profile Page**
  - Shows the user's history of RAKs (offers and requests).
  - Displays earned badges and aura levels.
  - Users can edit their profile details.

### API Spec

| URL                          | HTTP Method | Purpose                                  | Request Body                          | Success Response Code | Authentication/Authorisation  |
|------------------------------|-------------|------------------------------------------|---------------------------------------|-----------------------|-------------------------------|
| `/api/rakposts/`              | GET         | List all RAK posts                       | None                                  | 200                   | None                          |
| `/api/rakposts/`              | POST        | Create a new RAK post                    | `{ description, media, post_type }`   | 201                   | Authenticated users only      |
| `/api/rakposts/<pk>/`         | GET         | Retrieve a specific RAK                  | None                                  | 200                   | None                          |
| `/api/rakposts/<pk>/`         | PUT         | Update a specific RAK                    | `{ description, status, visibility }` | 200                   | Owner only                    |
| `/api/rakposts/<pk>/`         | DELETE      | Delete a specific RAK                    | None                                  | 204                   | Owner only                    |
| `/api/claimedraks/`           | GET         | List all claimed RAKs                    | None                                  | 200                   | None                          |
| `/api/claimedraks/`           | POST        | Claim a RAK post                         | `{ rak_id, details }`                 | 201                   | Authenticated users only      |
| `/api/claimedraks/<pk>/`      | GET         | Retrieve a specific claimed RAK          | None                                  | 200                   | None                          |
| `/api/claimedraks/<pk>/`      | PUT         | Update the status of a claimed RAK       | `{ status, completed }`               | 200                   | Claimant only                 |
| `/api/claimactions/`          | GET         | List all claim actions                   | None                                  | 200                   | None                          |
| `/api/claimactions/`          | POST        | Create a new claim action                | `{ claimed_rak_id, action_type }`     | 201                   | Authenticated users only      |
| `/api/users/`                 | GET         | List all users                           | None                                  | 200                   | Admin only                    |
| `/api/users/<pk>/`            | GET         | Retrieve user profile                    | None                                  | 200                   | Authenticated users only      |
| `/api/users/<pk>/`            | PUT         | Update user profile                      | `{ bio, profile_image, aura_points }` | 200                   | Profile owner only            |
| `/api/users/<pk>/followers/`  | GET         | List user’s followers                    | None                                  | 200                   | Authenticated users only      |
| `/api/users/<pk>/follow/`     | POST        | Follow another user                     | None                                  | 201                   | Authenticated users only      |
| `/api/users/<pk>/unfollow/`   | POST        | Unfollow a user                          | None                                  | 204                   | Authenticated users only      |
| `/api/notifications/`         | GET         | List user notifications                  | None                                  | 200                   | Authenticated users only      |
| `/api/notifications/<pk>/`    | GET         | Retrieve a specific notification         | None                                  | 200                   | Authenticated users only      |
| `/api/notifications/<pk>/`    | PUT         | Mark notification as read                | `{ read: true }`                      | 200                   | Authenticated users only      |
| `/api/badges/`                | GET         | List all badges                          | None                                  | 200                   | None                          |
| `/api/badges/user/<pk>/`      | GET         | List badges earned by a user             | None                                  | 200                   | Authenticated users only      |
| `/api/feed/`                  | GET         | List all RAKs in the community feed      | None                                  | 200                   | None                          |
| `/api/feed/user/<pk>/`        | GET         | List personalised feed for a user        | None                                  | 200                   | Authenticated users only      |
| `/api/comments/`              | GET         | List all comments on a RAK post          | None                                  | 200                   | None                          |
| `/api/comments/`              | POST        | Add a comment to a RAK post              | `{ rak_id, content }`                 | 201                   | Authenticated users only      |
| `/api/comments/<pk>/`         | PUT         | Edit a comment                           | `{ content }`                         | 200                   | Comment owner only            |
| `/api/comments/<pk>/`         | DELETE      | Delete a comment                         | None                                  | 204                   | Comment owner only            |
| `/api/likes/`                 | POST        | Like a RAK post                          | `{ rak_id }`                          | 201                   | Authenticated users only      |
| `/api/likes/<pk>/`            | DELETE      | Unlike a RAK post    

### DB Schema
![]( ../class.png)

### Aura Levels

1. **Generator (The Masterful Creator)**: Warm Yellow or Golden Aura, signifying the power to start and sustain acts of kindness.
   - **Initiator**: Light Yellow - Focus on starting projects.
   - **Sustainer**: Golden Yellow - Maintaining momentum.
   - **Visionary**: Amber - Long-term impact.
   - **Creator**: Deep Orange - Manifesting through hard work.
2. **Manifesting Generator (The Impacting Creator)**: Fiery Red Aura, representing quick action and impactful results.
   - **Accelerator**: Bright Red - Quick decision-making and action.
   - **Multitasker**: Coral Red - Efficient and dynamic.
   - **Problem Solver**: Burgundy - Strategically finding solutions.
   - **Transformer**: Crimson - Creating impactful changes.
3. **Projector (The Wisdom Keeper)**: Deep Blue Aura, symbolising wisdom and guidance.
   - **Guide**: Sky Blue - Supporting others with clarity.
   - **Teacher**: Navy Blue - Sharing wisdom.
   - **Healer**: Indigo - Restoring balance.
   - **Orchestrator**: Royal Blue - Directing complex situations.
4. **Manifestor (The Force of Nature)**: Dark Green Aura, representing the power to initiate change.
   - **Instigator**: Olive Green - Initiating change.
   - **Leader**: Emerald Green - Powerful presence.
   - **Independent**: Dark Teal - Working solo, pushing boundaries.
   - **Creator**: Deep Forest Green - Transforming ideas into action.
5. **Reflector (The Sacred Mirror)**: Silver or White Aura, reflecting the community's energy.
   - **Observer**: Light Silver - Reflecting the environment.
   - **Analyzer**: Soft Grey - Processing feedback.
   - **Balancer**: Pearl White - Achieving harmony.
   - **Harmoniser**: Crystal White - Bringing balance.