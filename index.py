class ChatPipe:
    def __init__(self):
        self.messages = []

    def add(self, text, class_name='', priority=1):
        self.messages.append({
           'text': text,
           'class': class_name,
           'priority': priority
        })

    def build_prompt(self, model_budget):
        # Sort messages based on priority
        sorted_messages = sorted(self.messages, key=lambda x: x['priority'], reverse=True)

        # Initialize variables to track space usage
        remaining_budget = model_budget
        prompt = []

        # Add system information (must fit)
        system_info = next((x for x in sorted_messages if x['class'] == 'system'), None)
        if system_info:
            prompt.append(system_info)
            remaining_budget -= len(system_info['text'])

        # Add project current file (must fit)
        project_file = next((x for x in sorted_messages if x['class'] == 'current_file'), None)
        if project_file and remaining_budget >= len(project_file['text']):
            prompt.append(project_file)
            remaining_budget -= len(project_file['text'])

        # Add users' last 1-3 messages (must fit, in historical order at the bottom)
        user_messages = [x for x in sorted_messages if x['class'] == 'messages'][:3]
        user_messages.reverse()  # Ensure historical order
        for message in user_messages:
            if remaining_budget >= len(message['text']):
                prompt.append(message)
                remaining_budget -= len(message['text'])

        # Add other information based on remaining budget
        for item in sorted_messages:
            if item not in prompt and remaining_budget >= len(item['text']):
                prompt.append(item)
                remaining_budget -= len(item['text'])

        return prompt


# Example usage:
PIPE = ChatPipe()

# Add messages with different classes and priorities
PIPE.add("You are a software tool in the Machinet system. You help analyze how Prompt is great at "
         "handling user requests. You think like Prompt's chief engineer, like Andrey Karpatiy or"
         " Ilya Sutskever.",
         class_name='system',
         priority=4)
PIPE.add('{project context}', class_name='project context', priority=3)
PIPE.add('{current_file}', class_name='current_file', priority=2)
PIPE.add('{messages}', class_name='messages', priority=1)


# Define the model budget
MODEL_BUDGET = 1000


# Build and print the prompt
result_prompt = PIPE.build_prompt(MODEL_BUDGET)
for res_item in result_prompt:
    print(f"{res_item['class']} - {res_item['text']}")

