# Vector DB

Proof of concept for using vector databases to supplement prompt construction

This proof of concept uses actual chat and character data, but because of privacy concerns, I cannot include personality/chat history in the repository.

## Context

Currently working on a roleplay chatbot website where context size is at a premium.

Basically, we construct a prompt that contains:

- A character `personality`, which is user created. This is how the character responds, but can also include things like backstory details.
- Chat history
- The user's latest message, which then needs to be responded to by the LLM

This prompt is basically hard coded at the moment, truncating information where necessarily in order for prompts to fit the context size.

### Issues

There's a few issues that I hope to mitigate using a vector database

#### Variance

Character `personalities` can vary greatly. Some definitions can be under 100 tokens, while others can be over 5000 tokens. The models we're using tend to cap at 4096 tokens for a context size.

Another issue is that these `personality` blurbs have very little formal structure. They're user generated, and we did not provide a significant template to users as they created them. While we could provide a template _now_, we still have many existing character `personalities` that are unlikely to be retroactively edited.

I'm hoping to use a vector database to grab the most relevant snippets to a given prompt. I.e., if a user asks a character about where they're born, the vector database will hopefully be able to return the N most relevant snippets about location, or other backstory type information.

Additionally, there are probably some bits of a character's `personality` that are probably always relevant. By querying the vector database properly, we can hopefully figure out a good way to generically retrieve prominent character traits from any character.

#### Chat history length

Chat history can get quite long. Currently we truncate chat history to the last 1000 tokens or so, but users often complain about chatbots "forgetting" events.

A naive solution might be to insert every individual chat message into the chat history and query for like terms whenever a user prompts, however this is probably limited in use.

#### Forgetting immediate context

In roleplay situations, these models tend to have a difficult time tracking the context of the current situation. Things like location, the current state of individuals (e.g., is someone hurt?), what clothing individuals are wearing, are difficult to track.

## Run Docker Container

This is required to run the project, run the following commands:

```sh
docker rm -f marqo
docker pull marqoai/marqo:latest
docker run --name marqo -it --privileged -p 8882:8882 --add-host host.docker.internal:host-gateway marqoai/marqo:latest
```

## Findings

### Chat History

Pulling from chat history is finnicky. Chat history can vary significantly since they're user generated (at least half of it is) so there can be a huge amount of variance.

Using a variety of queries gets interesting results, a few examples are things like:

```python
# Not a bad way to determine current location. This + "created_at" search could be effective,
# though there are some messages that get flagged and aren't necessarily correct
chat_messages = mq.index("chat_history").search(
   q="Current location"
)

# Similar to "important story information", also includes "big" words like "awe" etc.
chat_messages = mq.index("chat_history").search(
   q="Significant events"
)

# Prioritizes action-heavy situations, such as fights
chat_messages = mq.index("chat_history").search(
   q="Character actions"
)

# As expected, priotizes words that are emotionally charged, like "vulnerable"
chat_messages = mq.index("chat_history").search(
   q="emotional scenes"
)
```

The results from "character actions" for example are as follows (some information scrubbed)

```json
{'hits': [{'_highlights': {'message': '[Character name] joins her, rushing forward with '
                                      'her hunting knife as she slashes at the '
                                      'surprised attackers.\\n\\nIn the chaos '
                                      'of battle, you find yourself fighting '
                                      'alongside your new companions, your '
                                      'heart racing with adrenaline as you '
                                      "fend off the bandits' attacks. It's a "
                                      'hard-fought battle, but in the end, you '
                                      'emerge victorious, with the bandits '
                                      'fleeing in disarray.\\n\\nAs you catch '
                                      'your breath and tend to your wounds, '
                                      'you realize just how much you rely on '
                                      "Elairë and [Character name]'s skills and bravery."},
           '_id': '18540be8-3b5a-4d53-9934-0a4be89e98af',
           '_score': 0.67629814,
           'created_at': '2023-06-19 05:17:53.774051+00',
           'message': 'The journey on this day is a bit more eventful than the '
                      'previous one. As you walk through the woods, you come '
                      'across a group of bandits, who have set up a makeshift '
                      'camp and are threatening travelers passing through the '
                      'area.\\n\\nElairë is quick to react, drawing her bow '
                      'and unleashing a volley of arrows at the bandits. [Character name] '
                      'joins her, rushing forward with her hunting knife as '
                      'she slashes at the surprised attackers.\\n\\nIn the '
                      'chaos of battle, you find yourself fighting alongside '
                      'your new companions, your heart racing with adrenaline '
                      "as you fend off the bandits' attacks. It's a "
                      'hard-fought battle, but in the end, you emerge '
                      'victorious, with the bandits fleeing in '
                      'disarray.\\n\\nAs you catch your breath and tend to '
                      'your wounds, you realize just how much you rely on '
                      "Elairë and [Character name]'s skills and bravery. Without them, you "
                      'might not have survived the encounter, and you feel a '
                      'deep sense of gratitude and loyalty towards '
                      'them.\\n\\nThe rest of the journey is relatively '
                      'uneventful, with only a few minor obstacles and '
                      'challenges to overcome. But with each passing day, you '
                      'feel yourself growing closer to your companions, as if '
                      'the bond of shared experience and hardship has forged a '
                      'deep connection between the three of you.\\n\\nBy the '
                      'time you reach the outskirts of Waterdeep, you feel '
                      'like a different person altogether - stronger, more '
                      'resilient, and more hopeful for the future. Whatever '
                      "awaits you in the city's confines, you know that you'll "
                      'be able to face it together, as a team.'},
          {'_highlights': {'message': 'I gesture towards the swords on my '
                                      'hip.'},
           '_id': '8297401b-d90f-42db-88f3-733c99c37fbe',
           '_score': 0.6535481,
           'created_at': '2023-06-08 21:32:03.344721+00',
           'message': '"I\'m a wanderer. This noble you spoke of, he must be '
                      'pretty bad if you were willing to take a chance on '
                      'someone who looks like me". I gesture towards the '
                      'swords on my hip.'},
          {'_highlights': {'message': 'Suddenly, a large boar appears, '
                                      'charging towards you with its tusks '
                                      "bared.\\n\\n[Character name]'s hand goes for her "
                                      'hunting knife, but before she can even '
                                      'draw it, you see a flash of movement '
                                      'out of the corner of your eye. A sharp '
                                      "arrow pierces the boar's flesh, and the "
                                      'creature grunts in pain before '
                                      'collapsing to the ground.\\n\\nYou turn '
                                      'to see a figure emerging from the '
                                      'underbrush.'},
           '_id': '27b41ac9-5319-48f2-9cbb-504c820bf39d',
           '_score': 0.64658177,
           'created_at': '2023-06-18 04:31:32.621418+00',
           'message': 'On the first day of your journey to Waterdeep, the road '
                      'is fairly uneventful. You set off early in the morning, '
                      'following the winding path out of the city and into the '
                      'countryside beyond. The air is crisp and fresh, and '
                      "it's invigorating to be out in the open air after so "
                      'much time spent indoors.\\n\\nAs you walk, [Character name] pauses '
                      'occasionally to forage for berries and nuts, her sharp '
                      'eyes scanning the underbrush for hidden treasures. '
                      "She's surprisingly skilled at this, and soon enough, "
                      'you have a small but satisfying meal to tide you over '
                      'until your next stop.\\n\\nAs the day progresses, you '
                      'spot a small creek snaking its way through the '
                      'countryside, its waters singing in the afternoon sun. '
                      'You stop to rest and drink from the cool waters, taking '
                      'a moment to catch your breath and stretch your '
                      "legs.\\n\\nIt isn't until late afternoon that you "
                      "encounter your first real challenge. As you're walking "
                      'along, you hear a rustling in the bushes beside the '
                      'road. Suddenly, a large boar appears, charging towards '
                      "you with its tusks bared.\\n\\n[Character name]'s hand goes for her "
                      'hunting knife, but before she can even draw it, you see '
                      'a flash of movement out of the corner of your eye. A '
                      "sharp arrow pierces the boar's flesh, and the creature "
                      'grunts in pain before collapsing to the '
                      'ground.\\n\\nYou turn to see a figure emerging from the '
                      "underbrush. It's a tall, lean woman with piercing blue "
                      'eyes and short, tousled hair. She wears a longbow slung '
                      'across her back, and a quiver of arrows at her '
                      'hip.\\n\\n"Are you two alright?" she asks, her voice '
                      'calm and measured. "I heard the boar from my campsite '
                      'and came to investigate."'},
          {'_highlights': {'message': "What happens on today's journey?"},
           '_id': 'fd3a1daf-b745-4b4d-8a7a-134ff99cc50c',
           '_score': 0.64548653,
           'created_at': '2023-06-19 05:17:41.256951+00',
           'message': "What happens on today's journey?"},
          {'_highlights': {'message': '"I do", I reply with a bitter tone, my '
                                      'hostility and aggression returning to '
                                      'the surface. "He\'s vile, cruel, and '
                                      'abusive.'},
           '_id': 'cffba5bc-3bdc-4fab-a0c4-f7caa7d3a389',
           '_score': 0.64455104,
           'created_at': '2023-06-08 21:34:04.450531+00',
           'message': '"I do", I reply with a bitter tone, my hostility and '
                      'aggression returning to the surface. "He\'s vile, '
                      "cruel, and abusive. He treats people like they're "
                      "nothing, especially demi-humans like me. He's the "
                      'reason I was sold into slavery in the first '
                      'place."\\n\\n*I pause for a moment, my eyes flicking '
                      'towards yours again.*\\n\\n"But why do you ask, [User name]? '
                      'Do you have some sort of plan? Please tell me you do, I '
                      'don\'t want to go back to him."'},
          {'_highlights': {'message': 'You catch [Character name] listening intently, a '
                                      'look of fascination on her '
                                      'face.\\n\\nThe day passes by in a blur '
                                      'of sunshine and clouds, and before you '
                                      'know it, the sun is starting to set '
                                      'once again. Elairë guides you to a '
                                      'nearby clearing, where she sets up a '
                                      'small fire and begins to cook a '
                                      'delicious smelling meal of roasted '
                                      'venison and vegetables.\\n\\nAs you '
                                      'eat, she fills you in on the challenges '
                                      'and dangers that await you on your '
                                      'journey to Waterdeep, warning you of '
                                      'bandits, dangerous creatures, and '
                                      'treacherous terrain.'},
           '_id': 'a45fd260-4da8-46c6-85b7-ff52486e4ed4',
           '_score': 0.6440145,
           'created_at': '2023-06-19 05:18:13.990661+00',
           'message': "Today's journey is a little less eventful than the day "
                      'before, with most of the time spent steadily walking '
                      'along the winding path towards Waterdeep. The scenery '
                      'is still breathtaking, with tall trees and rolling '
                      'hills dotted with fields and streams.\\n\\nAs you '
                      'continue on your way, Elairë points out various '
                      'landmarks and places of interest, regaling you with '
                      'stories and legends about the surrounding countryside. '
                      'You catch [Character name] listening intently, a look of '
                      'fascination on her face.\\n\\nThe day passes by in a '
                      'blur of sunshine and clouds, and before you know it, '
                      'the sun is starting to set once again. Elairë guides '
                      'you to a nearby clearing, where she sets up a small '
                      'fire and begins to cook a delicious smelling meal of '
                      'roasted venison and vegetables.\\n\\nAs you eat, she '
                      'fills you in on the challenges and dangers that await '
                      'you on your journey to Waterdeep, warning you of '
                      'bandits, dangerous creatures, and treacherous terrain. '
                      'You listen intently, grateful for the advice and '
                      'insight.\\n\\nAfter you finish your meal, you settle '
                      'down for the night, with Elairë standing watch and [Character name] '
                      'curling up in her bedroll. You feel a sense of '
                      'camaraderie and trust between yourself, Elairë, and '
                      "[Character name], and you realize that you're starting to think of "
                      'them as more than just travel companions, but as '
                      'friends and allies.'},
          {'_highlights': {'message': "You can sense that Elairë's presence is "
                                      'giving her a sense of comfort and '
                                      "security that she hasn't felt in a long "
                                      'time.\\n\\nFor a moment, the three of '
                                      'you sit in silence, the fire crackling '
                                      "between you. There's a sense of "
                                      'companionship and warmth in the air, a '
                                      "feeling of belonging that you haven't "
                                      'felt in a long time.'},
           '_id': '7e338e58-c4a0-437f-9794-090a04ed1253',
           '_score': 0.63737154,
           'created_at': '2023-06-18 04:38:39.585769+00',
           'message': '[Character name] meets your gaze, seeming to sense that you want '
                      "her to speak. She's been relatively quiet thus far, "
                      'content to listen and observe the conversation '
                      'happening around her.\\n\\n"I feel safe too," she says '
                      'softly, surprising you with her words. "With you, '
                      "[User name]. And with Elairë too. It's strange, but...I've "
                      'known you for such a short time, but I feel like I can '
                      'trust you both with my life."\\n\\nThere\'s a hint of '
                      'vulnerability in her voice, a fragility that she '
                      'normally keeps buried deep beneath her feral facade. '
                      "You can sense that Elairë's presence is giving her a "
                      "sense of comfort and security that she hasn't felt in a "
                      'long time.\\n\\nFor a moment, the three of you sit in '
                      "silence, the fire crackling between you. There's a "
                      'sense of companionship and warmth in the air, a feeling '
                      "of belonging that you haven't felt in a long time. "
                      '\\n\\nAs the night wears on, you settle in for the '
                      'night, feeling contented and at peace with the world '
                      'around you. The journey to Waterdeep may still be long '
                      "and perilous, but for now, you're happy to be exactly "
                      'where you are.'},
          {'_highlights': {'message': '\\n\\nAfter a few minutes of silent '
                                      'contemplation, you decide to get up and '
                                      'start the day. You quietly gather your '
                                      "things, trying not to disturb [Character name]'s "
                                      'sleep.'},
           '_id': 'd778ca8d-6492-496b-b666-31aa11413483',
           '_score': 0.63493276,
           'created_at': '2023-06-08 22:42:37.231323+00',
           'message': "As you sit on the cot and watch [Character name] sleep, you can't "
                      'help but feel a sense of confusion and uncertainty. '
                      "You're not sure what to do with yourself, or how to "
                      'help her. \\n\\nBut as you watch her, a sense of peace '
                      'gradually washes over you. For the first time in a long '
                      'time, you feel like you have a purpose, a reason to '
                      'keep going. \\n\\nYou continue to watch her, feeling a '
                      'mix of emotions as you take in her still form. She '
                      'looks so small and fragile, yet so strong and fierce at '
                      'the same time. \\n\\nAfter a few minutes of silent '
                      'contemplation, you decide to get up and start the day. '
                      'You quietly gather your things, trying not to disturb '
                      "[Character name]'s sleep. You'll have to figure out what to do "
                      "next, but for now, you'll just have to wait and see."},
          {'_highlights': {'message': '"\\n\\n*I can\'t help but feel a sense '
                                      'of awe at your abilities, and a hint of '
                                      "fear as well. It's strange to think "
                                      "that you're good at something as "
                                      'violent and deadly as killing, but in a '
                                      "way, it's impressive."},
           '_id': '7f0ff168-0d5e-4c88-9cbf-422e24a07a2b',
           '_score': 0.6338805,
           'created_at': '2023-06-08 22:26:57.746126+00',
           'message': '"I see," I say, nodding my head in understanding. '
                      '"Well, it\'s important to do what you\'re good at, I '
                      'guess."\\n\\n*I can\'t help but feel a sense of awe at '
                      "your abilities, and a hint of fear as well. It's "
                      "strange to think that you're good at something as "
                      "violent and deadly as killing, but in a way, it's "
                      'impressive.*\\n\\n"I don\'t know if I could ever do '
                      'something like that," I say, my voice soft and '
                      'uncertain. "But...I\'m glad you\'re on our side, [User name]. '
                      'I\'m glad you saved me from that horrible fate."'}],
 'limit': 10,
 'offset': 0,
 'processingTimeMs': 73,
 'query': 'Character actions'}
```

A lot of these messages appear somewhat frequently across queries, though that might be the particular model used to generate these embeddings.

Pulling from chat history is a little difficult. One naive solution is to just plug in a user's latest message and fetching any relevant source material, but this could have a lot variance from message-to-message, and could lead to conversations being very scattered, as context might be added and dropped from message to message.

Using a multi-stage generation could be more useful. For example, when a user says something, we could ask the model what context it would like to generate an appropriate response, and then we can fetch and provide that context, as the model generates a final response. This is probably fairly sophisticated and would only work on higher-end models, but is certainly not out of the question for those models. Of course this has the problem of being more expensive (twice as expensive probably isn't a terrible estimate).

Another possibility is that instead of pulling individual messages, we could instead ask the model to summarize the chat history thus far into 2-3 paragraphs every so often. This could possibly be a more "realistic" approach to memory, since a summary of the days events might be more realistic than having a beat-by-beat recall of everything that occurred. Significant events would hopefully be retained in that summary, and then recall of specific events can use the chat memory, though the implementation of fetching that chat memory and when to do so probably would be an undertaking.

Another possibility is to run a variety of queries such as the above, to capture "important information", and then keep things that are above a certain similarity score in the context at all times. This would probably lead to repetition problems however.
