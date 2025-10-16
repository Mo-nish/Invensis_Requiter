# Use Cursor AI to Integrate Cloudinary

## 🎯 Problem: Files are in iCloud (dataless)
Your files are stored in iCloud and causing timeout errors. Use Cursor AI directly to make the changes!

---

## 📝 Step 1: Open Files in Cursor

Open these files in Cursor (they'll download from iCloud automatically):
1. `routes/recruiter_mongo.py`
2. `templates/recruiter/dashboard.html`
3. `templates/recruiter/candidates.html`
4. `templates/recruiter/candidate_details.html`
5. `templates/manager/candidate_details.html`
6. `templates/hr/candidate_details.html`

---

## 🤖 Step 2: Use Cursor AI (Cmd+K)

### Command 1: Update Routes

**Open:** `routes/recruiter_mongo.py`

**Press Cmd+K and paste:**

```
Add this import at the top after other imports:
from cloudinary_config import upload_file_to_cloudinary, delete_file_to_cloudinary, get_resource_type, check_cloudinary_configured

Then find the upload_candidate() function and replace the resume file save section with:

# Upload resume to Cloudinary
resume_path = None
resume_public_id = None
if resume_file and resume_file.filename:
    resource_type = get_resource_type(resume_file.filename)
    success, resume_url, resume_public_id = upload_file_to_cloudinary(
        resume_file,
        folder='invensis/resumes',
        resource_type=resource_type
    )
    if success:
        resume_path = resume_url
        print(f"✅ Resume uploaded to Cloudinary: {resume_url}")
    else:
        flash(f"Resume upload failed: {resume_url}", "error")

Also replace the image file save section with:

# Upload image to Cloudinary
image_path = None
image_public_id = None
if image_file and image_file.filename:
    resource_type = get_resource_type(image_file.filename)
    success, image_url, image_public_id = upload_file_to_cloudinary(
        image_file,
        folder='invensis/images',
        resource_type=resource_type
    )
    if success:
        image_path = image_url
        print(f"✅ Image uploaded to Cloudinary: {image_url}")
```

---

### Command 2: Update Templates

**For EACH template file, press Cmd+K and paste:**

```
Replace all occurrences of:
url_for('static', filename=candidate.resume_path)
with:
candidate.resume_path

Also replace:
url_for('static', filename=candidate.image_path)
with:
candidate.image_path

And replace:
url_for('static', filename=candidate.photo_path)
with:
candidate.photo_path
```

---

## ✅ Step 3: Save and Deploy

```bash
git add .
git commit -m "Integrate Cloudinary for permanent file storage"
git push origin main
```

Then go to Render → Manual Deploy

---

## 🎉 Done!

After deployment:
- Upload a new candidate with resume
- Click "View Resume"
- Should open Cloudinary URL (no 404!)

---

## 📋 Quick Checklist

- [ ] Open `routes/recruiter_mongo.py` in Cursor
- [ ] Use Cmd+K to add Cloudinary import
- [ ] Use Cmd+K to replace file upload code
- [ ] Open each template in Cursor
- [ ] Use Cmd+K to replace url_for with direct URLs
- [ ] Save all files
- [ ] Commit and push
- [ ] Deploy on Render
- [ ] Test upload

---

**Tip:** Cursor AI will make the changes automatically. Just review and accept them!

