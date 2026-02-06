def normalize_resume_json(data: dict) -> dict:
    # ---------- Projects ----------
    for project in data.get("projects", []):
        # description: list → string
        if isinstance(project.get("description"), list):
            project["description"] = " ".join(project["description"])

        # technologies: string → list
        if isinstance(project.get("technologies"), str):
            project["technologies"] = [
                t.strip() for t in project["technologies"].split(",")
            ]

    # ---------- Education ----------
    for edu in data.get("education", []):
        if "university" in edu and "institution" not in edu:
            edu["institution"] = edu.pop("university")

    # ---------- Skills ----------
    if isinstance(data.get("skills"), list):
        data["skills"] = {"General": data["skills"]}

    # Ensure all required fields are present and not None
    required_fields = {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "location": "",
        "Work_Experiemce": "",
        "job_roles": [],
        "summary": "",
        "skills": {},
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
        "achievements": [],
    }
    for k, v in required_fields.items():
        if k not in data or data[k] is None:
            data[k] = v

    # Education cgpa normalization
    for edu in data.get("education", []):
        if "cgpa" not in edu or edu["cgpa"] is None:
            edu["cgpa"] = ""

    return data
