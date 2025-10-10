# Cloudinary Integration - Quick Setup

## ✅ Status: Ready to Integrate!

Your Cloudinary credentials are set in Render:
- Cloud Name: `dspnu4jld`
- API Key: `192143441554598`
- API Secret: `o1ZSjvmZGpaU9rNM9nZQcES8vpk`

## 🚀 Integration Steps

### Step 1: Update Local .env File

Add these to your `.env` file:

```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=dspnu4jld
CLOUDINARY_API_KEY=192143441554598
CLOUDINARY_API_SECRET=o1ZSjvmZGpaU9rNM9nZQcES8vpk
```

### Step 2: Install Cloudinary Locally

```bash
pip install cloudinary>=1.36.0
```

### Step 3: Update `routes/recruiter_mongo.py`

**Add import at the top (after existing imports):**

```python
from cloudinary_config import upload_file_to_cloudinary, delete_file_from_cloudinary, get_resource_type, check_cloudinary_configured
```

**Find the `upload_candidate()` function and replace the file upload section:**

**OLD CODE (around line 200-250):**
```python
# Save resume file
if resume_file and resume_file.filename:
    resume_filename = f"{unique_id}_{secure_filename(resume_file.filename)}"
    resume_path = os.path.join('uploads', resume_filename)
    resume_file.save(os.path.join('static', resume_path))
```

**NEW CODE:**
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
        return redirect(url_for('recruiter.dashboard'))
```

**Do the same for image/photo upload:**

**OLD CODE:**
```python
# Save image file
if image_file and image_file.filename:
    image_filename = f"{unique_id}_{secure_filename(image_file.filename)}"
    image_path = os.path.join('uploads', image_filename)
    image_file.save(os.path.join('static', image_path))
```

**NEW CODE:**
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

**In ALL these templates:**
- `templates/recruiter/dashboard.html`
- `templates/recruiter/candidates.html`
- `templates/recruiter/candidate_details.html`
- `templates/manager/candidate_details.html`
- `templates/hr/candidate_details.html`

**Find and replace:**

**OLD:**
```html
{{ url_for('static', filename=candidate.resume_path) }}
```

**NEW:**
```html
{{ candidate.resume_path }}
```

**OLD:**
```html
{{ url_for('static', filename=candidate.image_path) }}
```

**NEW:**
```html
{{ candidate.image_path }}
```

### Step 5: Update MongoDB Schema (Optional)

Add `public_id` fields to store Cloudinary public IDs for deletion:

```python
# In the candidate document
candidate = {
    # ... existing fields ...
    'resume_path': resume_path,  # Now stores full Cloudinary URL
    'resume_public_id': resume_public_id,  # For deletion
    'image_path': image_path,  # Now stores full Cloudinary URL
    'image_public_id': image_public_id,  # For deletion
}
```

### Step 6: Test Locally

```bash
python run.py
```

1. Go to recruiter dashboard
2. Upload a candidate with resume and photo
3. Click "View Resume" - should open Cloudinary URL
4. No more 404 errors!

### Step 7: Deploy to Render

```bash
git add .
git commit -m "Integrate Cloudinary for permanent file storage"
git push origin main
```

Then trigger Manual Deploy on Render.

---

## 🎉 Benefits

- ✅ **No more 404 errors** - files stored in cloud
- ✅ **Persistent storage** - survives deployments
- ✅ **Fast CDN delivery** - Cloudinary's global CDN
- ✅ **Free tier** - 25GB storage, 25GB bandwidth
- ✅ **Automatic backups** - Cloudinary handles it

---

## 🆘 Troubleshooting

**Upload fails with "Cloudinary not configured":**
- Check Render environment variables are set
- Restart Render service after adding env vars

**Resume still shows 404:**
- Old candidates in database still have local paths
- New uploads will work correctly
- Run migration script to update old records (optional)

**"Module not found: cloudinary":**
- Run: `pip install cloudinary>=1.36.0`
- Make sure it's in `requirements.txt`

---

## 📞 Need Help?

If you get stuck, just ask! The integration is straightforward once the files are updated.

