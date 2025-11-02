# Manual Cloudinary Integration - Step by Step

## ⚠️ File System Issue Detected
The automated patcher encountered file system timeouts. Please follow these manual steps:

---

## 🎯 Quick Integration (5 Minutes)

### Step 1: Open `routes/recruiter_mongo.py` in Cursor

**At the top, after the existing imports (around line 10-20), add:**

```python
from cloudinary_config import upload_file_to_cloudinary, delete_file_from_cloudinary, get_resource_type, check_cloudinary_configured
```

### Step 2: Find `upload_candidate()` Function

Search for: `def upload_candidate`

**Find this section (around line 200-300):**

```python
# Save resume file
if resume_file and resume_file.filename:
    resume_filename = f"{unique_id}_{secure_filename(resume_file.filename)}"
    resume_path = os.path.join('uploads', resume_filename)
    resume_file.save(os.path.join('static', resume_path))
```

**Replace with:**

```python
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
```

### Step 3: Update Image Upload in Same Function

**Find this section:**

```python
# Save image file
if image_file and image_file.filename:
    image_filename = f"{unique_id}_{secure_filename(image_file.filename)}"
    image_path = os.path.join('uploads', image_filename)
    image_file.save(os.path.join('static', image_path))
```

**Replace with:**

```python
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

### Step 4: Update Templates

**In these 5 templates, use Find & Replace (Cmd+H):**

1. `templates/recruiter/dashboard.html`
2. `templates/recruiter/candidates.html`
3. `templates/recruiter/candidate_details.html`
4. `templates/manager/candidate_details.html`
5. `templates/hr/candidate_details.html`

**Find:**
```
url_for('static', filename=candidate.resume_path)
```

**Replace with:**
```
candidate.resume_path
```

**Find:**
```
url_for('static', filename=candidate.image_path)
```

**Replace with:**
```
candidate.image_path
```

---

## 🚀 Deploy

```bash
git add .
git commit -m "Integrate Cloudinary for permanent file storage"
git push origin main
```

Then go to Render → Manual Deploy

---

## ✅ Test

1. Go to recruiter dashboard
2. Upload a new candidate with resume
3. Click "View Resume" → should open Cloudinary URL (no 404!)
4. Check console logs for "✅ Resume uploaded to Cloudinary"

---

## 🎉 Done!

After this:
- ✅ No more 404 errors
- ✅ Files persist across deployments
- ✅ Fast CDN delivery
- ✅ 25GB free storage

---

## 🆘 If You Get Stuck

Just say "help with Cloudinary" and I'll guide you through any specific error!

