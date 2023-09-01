import csv
import pprint
import marqo

def parse_file():
    output = []
    with open('./description.txt', 'r') as file:
        lines = file.readlines()

    for line in lines:
      edited_line = line.replace("{{char}}", "Aqua")
      output.append({ "line": edited_line })
    return output


character_description_lines = parse_file()

def refresh_descriptions(mq, documents):
   mq.index("char_descriptions").delete()
   mq.create_index("char_descriptions")
   mq.index("char_descriptions").add_documents(documents, tensor_fields=["line"])

def flush_chat_history(mq):
   mq.index("chat_history").delete()
   mq.create_index("chat_history")

def db_insert_chat(mq):
  output = []
  with open("chat_history.csv", "r") as chat_history_csv:
      csv_reader = csv.reader(chat_history_csv)
      for row in csv_reader:
        #  print(row[1], row[4])
         output.append({ "created_at": row[1], "message": row[4] })
  mq.index("chat_history").add_documents(output, tensor_fields=["message"])

mq = marqo.Client(url='http://localhost:8882')
# flush_chat_history(mq)
# db_insert_chat(mq)
# refresh_db(mq, character_description_lines)

# Trying a variety of queries to see what kinds of responses I get.

# Not a bad way to determine current location. This + "created_at" search could be effective,
# though there are some messages that get flagged and aren't necessarily correct
# chat_messages = mq.index("chat_history").search(
#    q="Current location"
# )

# Seems to prioritize words like "journey", "adventure", etc. Not bad.
# chat_messages = mq.index("chat_history").search(
#    q="Most important story information"
# )

# Similar to "important story information", also includes "big" words like "awe" etc.
# chat_messages = mq.index("chat_history").search(
#    q="Significant events"
# )

# Prioritizes action-heavy situations, such as fights
chat_messages = mq.index("chat_history").search(
   q="Character actions"
)

# As expected, priotizes words that are emotionally charged, like "vulnerable"
# chat_messages = mq.index("chat_history").search(
#    q="emotional scenes"
# )

# Not great, a lot of the same messages as above, but harder to categorize.
# chat_messages = mq.index("chat_history").search(
#    q="character backstory"
# )

# Was hoping for character memories but I suppose it's a little vague. Not that useful.
# chat_messages = mq.index("chat_history").search(
#    q="memories"
# )

pprint.pprint(chat_messages)
# pprint.pprint(results)