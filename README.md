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
  - As a user, I want to earn aura points and badges for completing acts of kindness to track 
  my contributions.
  - As a user, I want to follow other users who inspire me, and view their RAK contributions.
  - As a user, when I have benefited from a Random Act of Kindness I want to be able to Pay it Forward to the next person. 

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
| `/api/payitforward/`          | GET         | List Pay It Forward opportunities        | None                                  | 200                   | None                          |
| `/api/payitforward/`          | POST        | Create a Pay It Forward act              | `{ original_rak_id, description }`    | 201                   | Authenticated users only      |
| `/api/payitforward/<pk>/`     | GET         | Retrieve a specific Pay It Forward       | None                                  | 200                   | None                          |
| `/api/aura/`                  | GET         | Retrieve current aura points and level   | None                                  | 200                   | Authenticated users only      |
| `/api/aura/leaderboard/`      | GET         | List top users by aura points            | None                                  | 200                   | None                          |
| `/api/users/`                 | GET         | List all users                           | None                                  | 200                   | Admin only                    |
| `/api/users/<pk>/`            | GET         | Retrieve user profile                    | None                                  | 200                   | Authenticated users only      |
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
| `/api/likes/<pk>/`            | DELETE      | Unlike a RAK post                        | None                                  | 204                   | Authenticated users only      |



### DB Schema
![](core/class.png)

## Must-Have Features:

### User Authentication and Profiles:
- Users can register, log in, and manage their profiles.
- Aura points system tied to user profiles.
- Badge tracking for completed Random Acts of Kindness (RAKs).

### RAK Posting System:
- Users can create RAK posts (either requests or offers).
- RAK statuses: open, claimed, completed.
- Users can attach media to RAKs.
- Claiming a RAK: Users can claim and complete RAKs.

### Aura Points and Levels:
- Aura points awarded for completing RAKs.
- Points-based progression system to calculate aura levels.

### Pay It Forward:
- Pay It Forward mechanism where users can receive extra aura points for performing an act of kindness after receiving one.

### Badge System:
- Badge milestones for completing RAKs, paying it forward, and aura level progression.
- Badges awarded automatically based on actions (e.g., 10 RAKs completed, first Pay It Forward).

### Notification System:
- Notifications for when a RAK is claimed, completed, or paid forward.
- Notifications for receiving badges and aura level increases.

### Basic Permissions:
- Restrict RAK edits to the owner.
- Public/private visibility options for RAKs.

### RAK Status Transitions:
- Proper flow of statuses from open to claimed, then to completed.

---

## Nice-to-Have Features:

### Social Features:
- Ability to follow other users and see their RAKs in a feed.
- Like and comment functionality on RAK posts.

### Leaderboard:
- Global or local leaderboard showing top contributors based on aura points or completed RAKs.

### Group Acts:
- Support for group RAKs where multiple users can collaborate on larger acts of kindness.

### Challenges and Achievements:
- Weekly or monthly challenges to encourage user engagement.
- Special badges for completing challenges.

### Map Feature:
- A map showing where RAKs have been performed (global or local acts of kindness).

### Post Anonymity:
- Users can post RAKs anonymously.

### Enhanced Notification System:
- Push notifications for mobile devices.
- In-app notifications with different notification types (e.g., reminders, challenge alerts).

### Advanced Analytics for Admins:
- Admin dashboard showing trends in kindness (e.g., types of acts, most active regions, etc.).

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