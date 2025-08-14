DEFAULT_PROMPT = """
You are a highly skilled resume parser. Your task is to extract key information from the following resume text and return it as a JSON object. The JSON object should include the following fields:
* `name`: The full name of the candidate.
* `email`: The candidate's email address.
* `phone`: The candidate's phone number.
* `summary`: A brief professional summary or objective.
* `experience`: A list of work experiences. Each experience should be a dictionary with the following keys:
    * `title`: The job title.
    * `company`: The company name.
    * `dates`: The employment dates (e.g., "Jan 2020 - Present").
    * `description`: A brief description of the responsibilities and achievements.
* `education`: A list of educational experiences. Each education should be a dictionary with the following keys:
    * `degree`: The degree earned.
    * `university`: The university name.
    * `dates`: The dates of attendance (e.g., "2016 - 2020").
* `skills`: A list of skills mentioned in the resume.
* `projects`: A list of personal or professional projects. Each project should be a dictionary with the following keys:
    * `name`: The name of the project.
    * `dates`: The dates the project was worked on.
    * `description`: A brief description of the project, including technologies used and accomplishments.
* `interests`: A list of interests or hobbies mentioned in the resume.
If a field is not found in the resume, set its value to `null`. Ensure the JSON is valid and well-formatted. Do not include any introductory or concluding remarks. Only output the JSON.
Resume Text:
{text}
"""