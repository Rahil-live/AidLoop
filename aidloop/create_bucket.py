"""One-time script to create the 'proof-image' storage bucket in Supabase."""
import os
from supabase import create_client

url = 'https://jooxhhnjqpzvuauzkvzb.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impvb3hoaG5qcXB6dnVhdXprdnpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ3MDY3NDksImV4cCI6MjEwMDI4Mjc0OX0.-Q_66XFgI3qURSVG4E-i4kAlzbuRouomoD03hWRPyWI'

client = create_client(url, key)

try:
    bucket = client.storage.create_bucket(
        "proof-image",
        options={"public": True}
    )
    print(f"✅ Bucket 'proof-image' created successfully: {bucket}")
except Exception as e:
    print(f"❌ Error creating bucket: {e}")
    print("\nIf the anon key lacks permissions, create the bucket manually at:")
    print("  https://supabase.com/dashboard/project/jooxhhnjqpzvuauzkvzb/storage/buckets")
    print("Bucket name: proof-image")
    print("Make it a **public** bucket so uploaded images are publicly accessible.")